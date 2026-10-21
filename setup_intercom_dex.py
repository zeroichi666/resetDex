#!/usr/bin/env python3
"""Setup-only Intercom DEX v0.1.5 for Ubuntu/WSL. No daemon or trading commands.
Python 3.12+, Node >=23.11, npm, curl, tar, git required for installation.
Run `python3 setup_intercom_dex.py --help`. Never place this beside real secrets.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile

VERSION = '0.1.5'
SHA256 = '63cef1771c8596e095cd7eaa52da2c74bc3670fad54f0d7b20f32b8a1b547b56'
URL = f'https://github.com/Trac-Systems/intercom-dex/releases/download/v{VERSION}/intercom-dex-v{VERSION}.tar.gz'
SERVICE_KEY = 'f5ac9f9cae208e0d8bb4e79e066e5ec423d6abb820377a5b0258e2ff358e6437'
PEER_KEY = 'e5fed943601365608957d82588fd8b71e1e44457f2c2e80dcb5748fd803ff1f1'
MARKER = 'prepared.json'


def fail(message):
    raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def clean_env():
    # Do not inherit passwords, Node preload hooks, npm hooks or agent credentials.
    return {k: os.environ[k] for k in ('PATH', 'HOME', 'USER', 'LOGNAME', 'LANG', 'LC_ALL', 'TERM', 'TMPDIR', 'SSL_CERT_FILE', 'SSL_CERT_DIR') if k in os.environ}


def run(args, cwd=None):
    subprocess.run([str(x) for x in args], cwd=cwd, env=clean_env(), check=True)


def path_checked(value):
    p = Path(os.path.abspath(os.path.expanduser(str(value))))
    for part in [p, *p.parents]:
        if part.is_symlink():
            fail(f'Symlink path refused: {part}')
    return p


def overlaps(a, b):
    return a == b or a in b.parents or b in a.parents


def validate_root(value, source=None):
    root = path_checked(value)
    if os.geteuid() == 0:
        fail('Run as your ordinary Ubuntu user, never sudo/root.')
    home = path_checked(Path.home())
    if root == home or home not in root.parents:
        fail('Root must be a dedicated new directory inside your Linux HOME.')
    if root == Path('/mnt') or Path('/mnt') in root.parents:
        fail('Use the WSL Linux filesystem, not /mnt Windows mounts.')
    protected = [home / 'src' / 'resetmnr', home / '.reset-signer']
    if source is not None:
        protected.append(source)
    if any(overlaps(root, p) for p in protected):
        fail('DEX directory must be separate from RESET source and ~/src/resetmnr.')
    return root


def private(path, directory=False):
    s = path.lstat()
    expected = 0o700 if directory else 0o600
    kind = stat.S_ISDIR if directory else stat.S_ISREG
    if not kind(s.st_mode) or stat.S_IMODE(s.st_mode) != expected or s.st_uid != os.getuid():
        fail(f'Expected owned, non-symlink {expected:04o} {"directory" if directory else "regular file"}: {path}')
    return s


def read_private(path, limit=16384):
    private(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        s = os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_uid != os.getuid() or stat.S_IMODE(s.st_mode) != 0o600:
            fail('Private file changed during open.')
        with os.fdopen(fd, 'rb', closefd=False) as f:
            data = f.read(limit + 1)
        if len(data) > limit:
            fail('Private file exceeds size limit.')
        return data
    finally:
        os.close(fd)


def write_new(path, data):
    if not isinstance(data, bytes):
        data = (json.dumps(data, indent=2) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
    finally:
        os.close(fd)


def node_binary():
    node = shutil.which('node')
    if not node:
        fail('Node.js not found.')
    version = subprocess.check_output([node, '--version'], env=clean_env(), text=True).strip()
    parts = tuple(int(x) for x in version.lstrip('v').split('.')[:3])
    if parts < (23, 11, 0):
        fail('Node.js >=23.11.0 required; Node 26 is supported by the upstream version constraint.')
    return node


def extract_verified(archive, destination):
    # Validate every entry before writing anything; reject links and device files.
    if digest(archive.read_bytes()) != SHA256:
        fail('Official archive SHA-256 mismatch. Nothing extracted.')
    prefix = f'intercom-dex-v{VERSION}'
    with tarfile.open(archive, 'r:gz') as tf:
        seen = set()
        for item in tf.getmembers():
            p = Path(item.name)
            if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0] != prefix:
                fail('Unsafe archive path.')
            if not (item.isfile() or item.isdir()) or item.name in seen:
                fail('Archive links, special files or duplicate entries refused.')
            seen.add(item.name)
        tf.extractall(destination, filter='data')


def source_hashes(app):
    # Hash all release files except installed dependency trees; no wallet data here.
    result = {}
    for base, dirs, files in os.walk(app, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d != 'node_modules')
        for d in dirs:
            if (Path(base) / d).is_symlink():
                fail('Unexpected symlink in release tree.')
        for name in sorted(files):
            p = Path(base) / name
            if not p.is_file() or p.is_symlink():
                fail('Unexpected non-regular release file.')
            result[str(p.relative_to(app))] = digest(p.read_bytes())
    return result


def prepare(root):
    node_binary()
    if not shutil.which('npm') or not shutil.which('curl') or not shutil.which('git'):
        fail('Install npm, curl and git first. This script never runs apt/sudo.')
    if root.exists():
        fail('Install directory already exists. Never overwrite/reuse it, including a partial installation.')
    # Download and verify before creating the persistent installation.
    with tempfile.TemporaryDirectory(prefix='dex-release-') as tmp:
        tmp = Path(tmp)
        archive = tmp / 'release.tar.gz'
        run(['curl', '--fail', '--location', '--silent', '--show-error', '--proto', '=https', '--proto-redir', '=https', '--tlsv1.2', '--connect-timeout', '30', '--max-time', '600', '--output', archive, URL])
        extract_verified(archive, tmp)
        app_src = tmp / f'intercom-dex-v{VERSION}'
        if json.loads((app_src / 'package.json').read_text())['version'] != VERSION:
            fail('Unexpected package version.')
        original_hashes = source_hashes(app_src)
        root.parent.mkdir(parents=True, exist_ok=True)
        root.mkdir(mode=0o700)  # exclusive: concurrent/repeated installs fail
        app = root / f'intercom-dex-v{VERSION}'
        shutil.move(str(app_src), str(app))
        write_new(root / 'RELEASE-SHA256.txt', (SHA256 + '\n').encode())
        print('Installing pinned dependencies. No wallet is read in this phase.', flush=True)
        run(['npm', 'ci', '--no-audit', '--no-fund'], cwd=app)
        run(['npm', 'ci', '--prefix', 'peer', '--no-audit', '--no-fund'], cwd=app)
        if source_hashes(app) != original_hashes:
            fail('Release files changed during dependency installation; stop and inspect.')
        data = root / 'data'
        data.mkdir(mode=0o700)
        config = {'network': 'mainnet', 'role': 'trader', 'dataDir': str(data),
                  'serviceKey': SERVICE_KEY, 'servicePeerKey': PEER_KEY}
        write_new(root / 'setup-only.json', config)
        write_new(root / MARKER, {'version': VERSION, 'sha256': SHA256, 'files': original_hashes})
    print(f'Prepared: {root}\nNo wallets yet. No proof key, runtime configuration, peer, trader or MCP started.')


def verify_prepared(root):
    private(root, True)
    marker = json.loads(read_private(root / MARKER, 2_000_000))
    if marker.get('version') != VERSION or marker.get('sha256') != SHA256:
        fail('Preparation manifest does not match the pinned release.')
    app = path_checked(root / f'intercom-dex-v{VERSION}')
    if source_hashes(app) != marker['files']:
        fail('Release source changed since preparation. Refusing setup.')
    data = path_checked(root / 'data')
    private(data, True)
    config_path = path_checked(root / 'setup-only.json')
    config = json.loads(read_private(config_path))
    expected = {'network': 'mainnet', 'role': 'trader', 'dataDir': str(data),
                'serviceKey': SERVICE_KEY, 'servicePeerKey': PEER_KEY}
    if config != expected:
        fail('Setup-only config changed. No custom imports/runtime options accepted.')
    if list(data.iterdir()) or (root / 'setup-complete.json').exists():
        fail('Existing/partial wallet data detected. Never overwrite or auto-delete it.')
    return app, data, config_path


def wallet_setup(root, source):
    node = node_binary()
    if not sys.stdin.isatty() or not sys.stderr.isatty():
        fail('Run wallet-setup interactively in your own terminal; no piped passwords accepted.')
    app, data, config_path = verify_prepared(root)
    private(source, True)
    source_file = source / 'keystore.json'
    original = read_private(source_file)
    # The upstream CLI reads a separate encrypted snapshot, never the source directory.
    # No plaintext mnemonic/private key is exported, stored or passed in argv/env.
    lock = root / '.wallet-setup.lock'
    lock.mkdir(mode=0o700)
    try:
        with tempfile.TemporaryDirectory(prefix='.reset-import-', dir=root) as tmp:
            snapshot = Path(tmp)
            write_new(snapshot / 'keystore.json', original)
            print('Setup only: new empty Solana wallet + separate encrypted RESET/Trac copy.\n'
                  'Enter a NEW DEX password (at least 12 characters), then the existing RESET password\n'
                  'at the upstream hidden prompts. Neither is saved by this wrapper.\n'
                  'Never enter or reuse the exposed recovery phrase.', flush=True)
            try:
                run([node, app / 'bin/dex.mjs', 'setup', '--config', config_path,
                     '--import-reset-keystore', snapshot], cwd=app)
            finally:
                if read_private(source_file) != original:
                    fail('RESET source changed during setup. Stop and inspect; this script never restores or overwrites it.')
        private(data / 'keyring.json')
        private(data / 'trac-wallet.json')
        write_new(root / 'setup-complete.json', {'version': VERSION, 'setupOnly': True,
                  'sourceUnchanged': True, 'freshSolana': True, 'runtimeStarted': False})
    finally:
        lock.rmdir()
    print('Wallet setup finished. Source bytes unchanged; no runtime or transaction started.\n'
          'Back up the encrypted data directory and keep the DEX password separately.\n'
          'Hermes integration, proof key, runtime config and service start are deliberately NOT performed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['plan', 'prepare', 'wallet-setup'], nargs='?', default='plan')
    parser.add_argument('--root', default='~/.local/share/intercom-dex-v0.1.5', help='Dedicated fresh Linux HOME directory')
    parser.add_argument('--reset-keystore', default='~/.reset-signer', help='Existing private encrypted RESET directory; wallet-setup only')
    args = parser.parse_args()
    os.umask(0o077)
    if sys.version_info < (3, 12):
        fail('Python >=3.12 required for safe archive extraction.')
    source = path_checked(args.reset_keystore)
    root = validate_root(args.root, source)
    if args.phase == 'plan':
        print(f'Pinned release: v{VERSION}\nOfficial archive: {URL}\nSHA256: {SHA256}\n'
              f'DEX root: {root}\nEncrypted RESET source: {source}\n'
              'plan: no download, writes, wallet reads or processes.\n'
              'prepare: download, verify, npm ci in separate release folder; no wallet access.\n'
              'wallet-setup: interactive upstream setup using an encrypted source snapshot; fresh Solana.\n'
              'Never: overwrite/reuse existing data, import Solana, start peer/trader/MCP, trade, push GitHub, configure Hermes.')
    elif args.phase == 'prepare':
        prepare(root)
    else:
        wallet_setup(root, source)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError, tarfile.TarError) as error:
        print(f'STOP: {error}', file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nStopped; preserve any partial data. No automatic retry or deletion.', file=sys.stderr)
        sys.exit(130)
