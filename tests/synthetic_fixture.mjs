// TEST ONLY: public deterministic mnemonic. These wallets must NEVER receive funds.
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';
import { mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { randomBytes, scryptSync, createCipheriv } from 'node:crypto';
import assert from 'node:assert/strict';
const [action, app, source, ...roots] = process.argv.slice(2);
const load = path => import(pathToFileURL(join(app, path)).href);
const { default: PeerWallet } = await load('peer/node_modules/trac-wallet/index.js');
const { walletOptions, walletMnemonic } = await load('src/trac/wallet.js');
const { resolveNetwork } = await load('src/net/profile.js');
const { openKeyring } = await load('src/roles/keyring.js');
const require = createRequire(join(app, 'package.json'));
const { Keypair } = require('@solana/web3.js');
const profile = resolveNetwork({ network: 'mainnet' });
// Public zero-entropy BIP39 test vector, derived only at runtime; never fund it.
const peerRequire = createRequire(join(app, 'peer/package.json'));
const { entropyToMnemonic } = peerRequire('bip39');
const mnemonic = entropyToMnemonic(Buffer.alloc(16));
const resetPassword = 'SYNTHETIC-reset-only-12345';
const dexPassword = 'SYNTHETIC-dex-only-67890';
const peer = new PeerWallet({ ...walletOptions(profile), mnemonic });
await peer.ready;
try {
  if (action === 'create') {
    mkdirSync(source, { mode: 0o700 });
    const salt = randomBytes(16), iv = randomBytes(12);
    const header = { v: 1, address: peer.publicKey.toString('hex'), kdf: 'scrypt-32768-8-1', cipher: 'aes-256-gcm', salt: salt.toString('hex'), iv: iv.toString('hex') };
    const key = scryptSync(resetPassword, salt, 32, { N: 32768, r: 8, p: 1, maxmem: 64 * 1024 * 1024 });
    const cipher = createCipheriv('aes-256-gcm', key, iv);
    cipher.setAAD(Buffer.from(JSON.stringify(header)));
    const encrypted = Buffer.concat([cipher.update(JSON.stringify({ mnemonic, derivationPath: peer.derivationPath })), cipher.final()]);
    writeFileSync(join(source, 'keystore.json'), JSON.stringify({ ...header, ciphertext: encrypted.toString('hex'), tag: cipher.getAuthTag().toString('hex') }), { mode: 0o600 });
    key.fill(0);
    console.log('SYNTHETIC fixture created (no secrets printed).');
  } else if (action === 'verify') {
    const addresses = [];
    for (const root of roots) {
      const tracFile = join(root, 'data/trac-wallet.json');
      const packet = await walletMnemonic(tracFile, dexPassword);
      assert.equal(packet.mnemonic, mnemonic);
      const keys = await openKeyring(join(root, 'data/keyring.json'), dexPassword);
      try {
        assert.ok(keys.solanaSecret?.length === 64);
        addresses.push(Keypair.fromSecretKey(keys.solanaSecret).publicKey.toBase58());
        for (const name of ['trac-wallet.json', 'keyring.json']) {
          const text = readFileSync(join(root, 'data', name), 'utf8');
          assert.ok(!text.includes(mnemonic));
          assert.ok(!text.includes(dexPassword));
          assert.ok(!text.includes(resetPassword));
        }
        assert.equal(JSON.parse(readFileSync(tracFile)).publicKey, peer.publicKey.toString('hex'));
      } finally { keys.storeKey.fill(0); keys.solanaSecret.fill(0); }
    }
    assert.equal(new Set(addresses).size, roots.length, 'each setup must generate a distinct fresh Solana key');
    console.log('SYNTHETIC verification passed: same Trac identity, fresh distinct Solana keys, encrypted outputs.');
  } else throw new Error('Unknown fixture action');
} finally { peer.secretKey.fill(0); }
