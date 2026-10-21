# Hasil uji skrip setup Intercom DEX

**Lulus: 31 pemeriksaan pada Node 24.19.0 dan 31 pemeriksaan pada Node 26.12.0.** Tahap instalasi `prepare` lengkap juga berhasil di Sandbox. Tidak ada eksekusi pada laptop WSL, akses wallet/keystore/password pengguna, push GitHub, integrasi Hermes, atau transaksi.

Seluruh 31 pemeriksaan diulang dari checkout `resetDex` pada kedua runtime saat persiapan repositori, termasuk setelah fixture diubah untuk menurunkan vektor BIP39 saat runtime tanpa phrase literal. Arsip lokal diperiksa ulang terhadap SHA-256 resmi dan sumber instalasi uji diperiksa terhadap manifest `prepared.json`. Log kedua runtime diperbarui; `tests/prepare-output.txt` tetap merupakan bukti instalasi lengkap sebelumnya, bukan klaim instalasi npm diulang pada tahap ini.

## Hasil yang paling penting

Setup aktual memakai `bin/dex.mjs setup` dari rilis resmi v0.1.5, melalui terminal virtual dengan password **sintetis**. Ini bukan simulasi pengganti fungsi kriptografi upstream.

Dua setup independen berhasil mempertahankan identitas Trac dari fixture RESET yang sama, tetapi menghasilkan kunci dan alamat **Solana baru yang berbeda**. Tidak ada argumen impor Solana. Isi wallet DEX terenkripsi dibuka kembali dalam pengujian untuk memastikan identitasnya benar; mnemonic maupun password sintetis tidak ditemukan sebagai plaintext di file output.

Setelah setup sukses, setup ulang yang ditolak, dan password RESET salah, isi sumber tetap sama. Pemeriksaan mencakup SHA-256/bytes, waktu modifikasi, pemilik, serta mode izin sumber. Waktu akses tidak dinilai karena pembacaan file dapat memperbaruinya.

Wallet output bermode `0600`, folder data `0700`. Setup ulang dan data parsial ditolak tanpa menimpa atau menghapus file lama. Snapshot terenkripsi sementara dibersihkan pada jalur sukses dan kegagalan password.

## Rilis benar-benar diverifikasi

Aset: [`intercom-dex-v0.1.5.tar.gz`](https://github.com/Trac-Systems/intercom-dex/releases/download/v0.1.5/intercom-dex-v0.1.5.tar.gz).

```text
SHA-256: 63cef1771c8596e095cd7eaa52da2c74bc3670fad54f0d7b20f32b8a1b547b56
```

Hash arsip yang diunduh cocok dengan hash yang diberikan dan [halaman rilis resmi](https://github.com/Trac-Systems/intercom-dex/releases/tag/v0.1.5). Kedua venue key di skrip cocok dengan metadata rilis tersebut. Tag, versi package, serta hash file sumber sebelum/sesudah instalasi dependency diperiksa.

Tahap `prepare` diuji melalui skrip final: unduh arsip resmi, validasi hash, ekstraksi aman, `npm ci`, `npm ci --prefix peer`, pembuatan konfigurasi khusus setup, dan manifest. Sumber RESET untuk uji tahap ini sengaja menunjuk lokasi sintetis yang **tidak ada**, membuktikan tahap instalasi tidak membutuhkan keystore.

## Yang diuji

| Area | Hasil |
|---|---|
| `plan` tanpa membuat folder atau membaca isi wallet | Lulus |
| Root bertumpang tindih dengan `~/src/resetmnr` atau sumber RESET | Ditolak |
| Path sumber symlink | Ditolak |
| Direktori sumber bukan `0700` atau file sumber bukan `0600` | Ditolak, tanpa perbaikan otomatis |
| Penulisan eksklusif ke file yang sudah ada | Ditolak; isi lama utuh |
| `prepare` pada direktori yang sudah ada | Ditolak sebelum unduhan |
| Setup tanpa terminal interaktif | Ditolak sebelum pembuatan wallet |
| Konfigurasi impor Solana yang disisipkan | Ditolak |
| File sumber rilis yang diubah setelah persiapan | Ditolak |
| CLI setup resmi dengan snapshot keystore sintetis | Berhasil |
| Password/preload hook Node dari environment | Tidak diwariskan ke CLI |
| Password sintetis di output terminal | Tidak tampil |
| Kriptografi wallet dan identitas Trac | Diverifikasi dengan membuka hasil terenkripsi |
| Solana antar dua setup independen | Kunci/alamat baru dan berbeda |
| Password RESET salah | Gagal tanpa membuat wallet |
| Setup ulang dan data parsial | Ditolak; data tetap utuh |
| Snapshot sementara pada sukses/gagal | Dihapus |
| Checksum arsip salah | Ditolak sebelum ekstraksi |
| Path traversal dan symlink dalam arsip sintetis | Ditolak |
| Isi folder data setelah setup | Hanya `keyring.json` dan `trac-wallet.json` |
| Peer/trader/MCP, saldo jaringan, offer/trade/transfer | Tidak dijalankan; perintah wrapper dibatasi ke `setup` |

Fixture menurunkan mnemonic vektor uji BIP39 publik dari 16 byte nol saat runtime, bukan menyimpan phrase literal dalam source; **jangan pernah mendanai alamat fixture**. Password berlabel `SYNTHETIC` pada harness adalah nilai uji publik, bukan kredensial pengguna. Wallet sintetis dibersihkan otomatis oleh test harness. Tidak ada phrase terpapar milik pengguna yang dipakai.

## Bukti yang dapat diulang

- `tests/test_setup.py`: 31 pemeriksaan wrapper, terminal, file, dan arsip.
- `tests/synthetic_fixture.mjs`: pembuatan keystore terenkripsi sintetis dan verifikasi kriptografi hasil.
- `tests/test-output.txt`: hasil Node 24.19.0.
- `tests/node26-test-output.txt`: hasil Node 26.12.0.
- `tests/prepare-output.txt`: hasil instalasi penuh di Sandbox.

Untuk mengulang di lingkungan uji tersendiri dengan rilis yang telah diverifikasi dan dipasangi dependency:

```bash
python3 tests/test_setup.py /absolute/path/intercom-dex-v0.1.5
```

Harness tidak membaca `~/.reset-signer`; semua fixture dibuat di direktori sementara khusus di Linux HOME. Dependensi dibagi dari instalasi uji, sementara file sumber dan wallet tiap kasus terpisah.

## Batas hasil ini

Pengujian berlangsung pada Linux Sandbox dengan Python 3.12.3, bukan Ubuntu WSL milik pengguna. Node 26.12.0 digunakan untuk mengulang seluruh uji wallet/setup; instalasi dependency penuh `prepare` dijalankan dengan Node 24.19.0. Belum ada pengujian jaringan DEX atau integrasi Hermes karena tahap itu tidak diizinkan.

Npm menampilkan peringatan dependency usang, pending lifecycle scripts pada versi npm Sandbox, dan integrity-check yang dilewati untuk dua dependency Git upstream. Kedua dependency Git dipatok commit oleh rilis upstream; hash arsip rilis **tidak** secara independen mengesahkan seluruh dependency transitif. Skrip tidak mengubah lockfile, mengganti versi, atau mengaktifkan approval script tambahan. Ini bukan audit keamanan menyeluruh atas dependency.

`npm ci` pada mesin berbeda dapat menjalankan lifecycle dependency sesuai versi/kebijakan npm setempat. Instalasi memerlukan internet; fase setup wallet sendiri tidak memanggil saldo/RPC, peer, trader, atau transaksi. Perlindungan hash manifest mendeteksi perubahan file sumber rilis, bukan audit seluruh `node_modules` atau perlindungan terhadap penyerang lokal yang sudah menguasai akun user.

Reuse RESET menghasilkan salinan otoritas atas **alamat yang sama**, bukan pemisahan dana RESET. Solana adalah identitas baru yang dibuat lokal dan belum didanai oleh skrip; saldo on-chain tidak ditanyakan. Proof key, runtime config, payout lock dan pengaktifan layanan harus dibahas terpisah sebelum integrasi Hermes.

Jika proses dimatikan paksa, snapshot terenkripsi atau lock dapat tertinggal. Skrip tidak melakukan penghapusan/retry otomatis terhadap instalasi atau wallet parsial. Pertahankan data dan tinjau manual sebelum tindakan pemulihan.

Referensi perilaku setup: [dokumentasi wallet v0.1.5](https://github.com/Trac-Systems/intercom-dex/blob/v0.1.5/docs/WALLETS.md), [CLI pada tag v0.1.5](https://github.com/Trac-Systems/intercom-dex/blob/v0.1.5/bin/dex.mjs), dan [implementasi setup](https://github.com/Trac-Systems/intercom-dex/blob/v0.1.5/src/wallets/setup.js).
