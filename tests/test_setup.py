#!/usr/bin/env python3
"""Sandbox-only synthetic tests; never reads ~/.reset-signer or real wallets.
Usage: python3 tests/test_setup.py /absolute/path/to/verified-and-installed-release
"""
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import pty
import select
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time

SCRIPT = Path(__file__).resolve().parents[1] / 'setup_intercom_dex.py'
FIXTURE = Path(__file__).with_name('synthetic_fixture.mjs')
spec = importlib.util.spec_from_file_location('setup', SCRIPT)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
APP = Path(sys.argv[1]).resolve()
RESULTS = []
DEX = 'SYNTHETIC-dex-only-67890'
RESET = 'SYNTHETIC-reset-only-12345'


def check(label, condition):
    if not condition:
        raise AssertionError(label)
    RESULTS.append(label)
    print('PASS:', label, flush=True)


def rejects(label, fn):
    try:
        fn()
    except (RuntimeError, OSError, ValueError):
        check(label, True)
    else:
        check(label, False)


def snapshot(directory):
    result = {}
    for p in [directory, *sorted(directory.rglob('*'))]:
        st = p.lstat()
        result[str(p.relative_to(directory))] = (stat.S_IMODE(st.st_mode), st.st_uid, st.st_mtime_ns,
            hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
    return result


def invoke(root, source, replies=(DEX, RESET), timeout=60):
    master, slave = pty.openpty()
    # Use a real PTY, not a production backdoor or NODE_OPTIONS preload.
    env = dict(os.environ, DEX_KEY_PASSWORD='UNWANTED-INHERITED-PASSWORD', NODE_OPTIONS='--require=/nonexistent/blocked-hook.cjs')
    p = subprocess.Popen([sys.executable, str(SCRIPT), 'wallet-setup', '--root', str(root), '--reset-keystore', str(source)],
                         stdin=slave, stdout=slave, stderr=slave, env=env, start_new_session=True)
    os.close(slave)
    output = bytearray()
    sent = 0
    prompts = [b'New keyring password: ', b'RESET keystore password: ']
    deadline = time.monotonic() + timeout
    try:
        while True:
            if time.monotonic() > deadline:
                p.kill()
                raise TimeoutError('synthetic PTY setup exceeded time limit')
            ready, _, _ = select.select([master], [], [], 0.1)
            if ready:
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                output.extend(chunk)
                if sent < len(replies) and prompts[sent] in output:
                    # Upstream switches terminal to raw mode immediately after prompt.
                    time.sleep(0.08)
                    os.write(master, (replies[sent] + '\r').encode())
                    sent += 1
            if p.poll() is not None and not ready:
                break
        code = p.wait(timeout=5)
    finally:
        os.close(master)
        if p.poll() is None:
            p.kill()
            p.wait()
    return code, output.decode(errors='replace')


def seeded_root(base, name, hashes):
    root = base / name
    root.mkdir(mode=0o700)
    app = root / f'intercom-dex-v{s.VERSION}'
    shutil.copytree(APP, app, ignore=shutil.ignore_patterns('node_modules'))
    # Dependencies are shared read-only for tests. Release source is a distinct copy.
    (app / 'node_modules').symlink_to(APP / 'node_modules', target_is_directory=True)
    (app / 'peer/node_modules').symlink_to(APP / 'peer/node_modules', target_is_directory=True)
    (root / 'data').mkdir(mode=0o700)
    config = {'network': 'mainnet', 'role': 'trader', 'dataDir': str(root / 'data'), 'serviceKey': s.SERVICE_KEY, 'servicePeerKey': s.PEER_KEY}
    s.write_new(root / 'setup-only.json', config)
    s.write_new(root / s.MARKER, {'version': s.VERSION, 'sha256': s.SHA256, 'files': hashes})
    return root


os.umask(0o077)
with tempfile.TemporaryDirectory(prefix='dex-synthetic-tests-', dir=Path.home()) as temporary:
    base = Path(temporary)
    source = base / 'synthetic-reset'
    subprocess.run(['node', str(FIXTURE), 'create', str(APP), str(source)], check=True)
    original = snapshot(source)
    hashes = s.source_hashes(APP)
    root = seeded_root(base, 'first', hashes)
    root2 = seeded_root(base, 'second', hashes)
    check('plan is non-mutating and succeeds', subprocess.run([sys.executable, str(SCRIPT), 'plan', '--root', str(base / 'plan-only'), '--reset-keystore', str(base / 'missing-source')], capture_output=True).returncode == 0 and not (base / 'plan-only').exists())
    rejects('RESET project overlap refused', lambda: s.validate_root(Path.home() / 'src/resetmnr/dex'))
    rejects('RESET source overlap refused', lambda: s.validate_root(source / 'dex', source))
    link = base / 'alias'
    link.symlink_to(source, target_is_directory=True)
    rejects('symlink source refused', lambda: s.path_checked(link))
    source.chmod(0o755)
    rejects('unsafe source directory mode refused', lambda: s.private(source, True))
    source.chmod(0o700)
    (source / 'keystore.json').chmod(0o644)
    rejects('unsafe source file mode refused', lambda: s.read_private(source / 'keystore.json'))
    (source / 'keystore.json').chmod(0o600)
    check('mode checks did not modify source bytes or metadata', snapshot(source) == original)
    target = base / 'exclusive.json'
    s.write_new(target, b'original')
    rejects('exclusive write refuses overwrite', lambda: s.write_new(target, b'replacement'))
    check('exclusive-write target unchanged', target.read_bytes() == b'original')
    rejects('prepare refuses existing directory before download', lambda: s.prepare(root))
    check('non-TTY setup refused without writing data', subprocess.run([sys.executable, str(SCRIPT), 'wallet-setup', '--root', str(root), '--reset-keystore', str(source)], capture_output=True).returncode != 0 and not list((root / 'data').iterdir()))
    # Config and source tampering are rejected before password prompts/creation.
    config_file = root / 'setup-only.json'
    config_bytes = config_file.read_bytes()
    config = json.loads(config_bytes)
    config['solana'] = {'importKeypairFile': '/must-never-be-read'}
    config_file.write_text(json.dumps(config))
    rejects('custom Solana import/config refused', lambda: s.verify_prepared(root))
    config_file.write_bytes(config_bytes)
    cli = root / f'intercom-dex-v{s.VERSION}/bin/dex.mjs'
    cli_bytes = cli.read_bytes()
    cli.write_bytes(cli_bytes + b'\n// tampered\n')
    rejects('changed release source refused', lambda: s.verify_prepared(root))
    cli.write_bytes(cli_bytes)
    code, output = invoke(root, source)
    check('actual wrapper and upstream CLI setup succeeded', code == 0)
    check('passwords never echoed; inherited password/preload hooks ignored', DEX not in output and RESET not in output and 'blocked-hook' not in output and 'UNWANTED-INHERITED-PASSWORD' not in output)
    check('source bytes, mtime, ownership and modes unchanged after setup', snapshot(source) == original)
    check('wallet files 0600 and data directory 0700', all(stat.S_IMODE((root / 'data' / n).stat().st_mode) == 0o600 for n in ('keyring.json', 'trac-wallet.json')) and stat.S_IMODE((root / 'data').stat().st_mode) == 0o700)
    before = snapshot(root / 'data')
    code, output = invoke(root, source, replies=())
    check('rerun refuses existing wallets and preserves all bytes', code != 0 and snapshot(root / 'data') == before)
    check('encrypted snapshot removed after success', not list(root.glob('.reset-import-*')) and not (root / '.wallet-setup.lock').exists())
    code, output = invoke(root2, source)
    check('second independent synthetic setup succeeded', code == 0)
    subprocess.run(['node', str(FIXTURE), 'verify', str(APP), str(source), str(root), str(root2)], check=True)
    check('real crypto verifies preserved Trac identity and distinct fresh Solana keys', True)
    bad = seeded_root(base, 'wrong-password', hashes)
    code, output = invoke(bad, source, replies=(DEX, 'WRONG-SYNTHETIC-PASSWORD'))
    check('wrong RESET password fails with no wallet creation', code != 0 and not list((bad / 'data').iterdir()))
    check('wrong-password failure leaves source unchanged and removes snapshot', snapshot(source) == original and not list(bad.glob('.reset-import-*')))
    partial = seeded_root(base, 'partial', hashes)
    s.write_new(partial / 'data/trac-wallet.json', b'keep-partial')
    rejects('partial data detected and never deleted', lambda: s.verify_prepared(partial))
    check('partial file preserved', (partial / 'data/trac-wallet.json').read_bytes() == b'keep-partial')
    # Hash mismatch must be checked before any extraction.
    wrong_archive = base / 'wrong.tar.gz'
    wrong_archive.write_bytes(b'not-the-release')
    rejects('wrong archive checksum refused before extraction', lambda: s.extract_verified(wrong_archive, base / 'not-created'))
    check('hash mismatch creates no extraction directory', not (base / 'not-created').exists())
    # Exercise traversal/link checks with a synthetic digest only in this test process.
    for name, kind in [('intercom-dex-v0.1.5/../../escape', 'path'), ('intercom-dex-v0.1.5/link', 'link')]:
        archive = base / f'{kind}.tar.gz'
        with tarfile.open(archive, 'w:gz') as tf:
            member = tarfile.TarInfo(name)
            if kind == 'link':
                member.type = tarfile.SYMTYPE
                member.linkname = '/tmp/escape'
                tf.addfile(member)
            else:
                member.size = 1
                tf.addfile(member, io.BytesIO(b'x'))
        pinned = s.SHA256
        s.SHA256 = s.digest(archive.read_bytes())
        try:
            rejects(f'unsafe archive {kind} entry refused', lambda: s.extract_verified(archive, base / 'unsafe-out'))
        finally:
            s.SHA256 = pinned
    check('no peer/trader/MCP runtime files created by setup', sorted(p.name for p in (root / 'data').iterdir()) == ['keyring.json', 'trac-wallet.json'])
    check('final RESET source unchanged', snapshot(source) == original)
print(f'\nRESULT: {len(RESULTS)} checks passed. Synthetic wallets cleaned automatically. No real wallet or laptop used.')
