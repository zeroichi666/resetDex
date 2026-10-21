# Gambaran Proyek Intercom DEX v0.1.5

> **Status singkat:** skrip setup telah diuji dengan wallet sintetis saja. Ini belum merupakan sistem trading yang operasional sepenuhnya dan belum dijalankan pada laptop pengguna.

## Apa proyek ini?

Intercom DEX adalah perangkat lunak untuk menukar TNK atau RESET di Trac dengan USDC di Solana melalui jaringan peer-to-peer. Program memegang wallet terenkripsi di komputer pengguna. Namun, ringkasan ini hanya membahas persiapan aman dan pembuatan wallet; **tidak ada trading, transfer, atau transaksi yang dijalankan**.

## Rilis yang dikunci

Setup memakai arsip tag resmi, bukan branch `main`:

- [Halaman release v0.1.5](https://github.com/Trac-Systems/intercom-dex/releases/tag/v0.1.5)
- [Unduh arsip resmi `intercom-dex-v0.1.5.tar.gz`](https://github.com/Trac-Systems/intercom-dex/releases/download/v0.1.5/intercom-dex-v0.1.5.tar.gz)
- SHA-256 yang wajib cocok: `63cef1771c8596e095cd7eaa52da2c74bc3670fad54f0d7b20f32b8a1b547b56`

Skrip memverifikasi hash sebelum ekstraksi, menolak path berbahaya/symlink di arsip, memasang dependency dengan `npm ci`, lalu memeriksa bahwa file sumber rilis tidak berubah. Hash arsip tidak sama dengan audit menyeluruh atas semua dependency transitif atau perlindungan dari penyerang lokal.

## Tiga fase skrip

Skrip pada repositori ini adalah [`setup_intercom_dex.py`](setup_intercom_dex.py).

1. **`plan` — melihat rencana saja**
   - Tidak mengunduh, menulis folder, membaca isi wallet, atau memulai proses.
   - Menampilkan rilis, hash, lokasi instalasi, dan sumber RESET terenkripsi secara umum.

2. **`prepare` — menyiapkan program**
   - Mengunduh arsip di atas, memverifikasi SHA-256, mengekstrak dengan aman, dan menjalankan `npm ci` pada rilis serta `peer`.
   - Membuat folder root Linux baru yang terpisah di bawah `HOME`, manifest hash, dan konfigurasi **setup-only**.
   - **Tidak membaca keystore/wallet RESET** dan tidak memulai peer, trader, MCP, dashboard, service/autostart, atau transaksi.

3. **`wallet-setup` — membuat wallet DEX**
   - Hanya interaktif di terminal; meminta password DEX baru minimal 12 karakter dan password keystore RESET yang sudah ada.
   - Membuat snapshot sementara yang tetap terenkripsi dari keystore RESET, lalu memanggil CLI resmi `setup --import-reset-keystore`. Mnemonic/private key tidak diekspor ke plaintext atau argumen/environment.
   - Menghasilkan wallet Solana baru serta salinan wallet RESET/Trac terenkripsi. Sumber RESET diperiksa tetap byte-for-byte sama dan tidak ditimpa.
   - Tidak membuat proof key, konfigurasi runtime Hermes, peer, trader, MCP, offer, market, trade, transfer, atau transaksi.

## Arti “terpisah” dan batas perlindungan

- Folder data DEX terpisah dari sumber RESET dan proyek lain; setup menolak folder tujuan yang sudah ada, data parsial, konfigurasi yang berubah, izin file yang salah, serta percobaan setup ulang yang berisiko menimpa data.
- Data wallet dibuat terenkripsi dengan folder/file privat. Backup terenkripsi dan password DEX harus disimpan terpisah.
- Snapshot impor menghindari CLI menulis ke direktori sumber. Jika proses dibunuh paksa atau komputer mati, snapshot atau lock dapat tertinggal; **jangan menghapus atau mengulang otomatis** sebelum pemeriksaan manual.
- **Penting:** keystore RESET/Trac yang diimpor dan wallet asal mempunyai **otoritas, alamat, dan dana yang sama**. Ini bukan isolasi dana atau identitas. Yang baru dan berbeda adalah wallet/identitas Solana.
- Skrip tidak mendanai alamat Solana baru, tidak mengecek saldo on-chain, dan tidak melindungi mesin yang sudah dikuasai pihak lain. Jangan pernah memakai recovery phrase yang pernah terpapar.

## Belum operasional sepenuhnya

Sampai ada persetujuan dan pekerjaan lanjutan, belum ada:

- Hermes, proof key, runtime config lengkap, payout lock, atau service start;
- peer jaringan, trader, market/offer, atau koneksi market;
- wallet pengguna yang didanai, saldo jaringan, trade, transfer, maupun transaksi;
- bukti bahwa teknik MCP **read-only** yang aman sudah tersedia. Jangan menganggap MCP pasif: dokumentasi upstream menyatakan `src/mcp/server.mjs` dapat otomatis memulai program trader bila role belum berjalan.

## Rencana Hermes (rencana, bukan fitur yang sudah implemented)

1. **Review kompatibilitas dan dependency:** cocokkan versi, konfigurasi, proof/runtime, peer, dan dependency; jangan menganggap hasil setup sintetis sebagai kesiapan produksi.
2. **Owner lokal:** pemilik menyiapkan wallet setup dan backup aman; password tidak ditaruh di file proyek atau dibagikan.
3. **Bukti dan kunci:** verifikasi proof key, runtime config, dan payout lock; setiap start dilakukan dengan persetujuan terpisah setelah bukti diperiksa.
4. **Peer/market secara hati-hati:** bila diperlukan, mulai dari observasi yang benar-benar dibuktikan aman dan read-only. Tidak ada klaim bahwa mode MCP read-only aman telah tersedia. Jangan menyalakan MCP sembarangan karena dapat auto-start trader.
5. **Transaksi per kejadian:** offer, trade, transfer, atau transaksi hanya setelah persetujuan pemilik yang spesifik untuk setiap transaksi. Persetujuan harus menyebut **jumlah, aset, harga, biaya, slippage, tujuan/payout, network, dan masa berlaku (expiry)**. Tidak ada blanket approval.

Dokumentasi upstream menunjukkan role runtime memakai peer terpisah dan `bin/dex.mjs`; peer harus dijalankan lebih dulu pada operasi nyata. Detail tersebut adalah dokumentasi operasi masa depan, bukan bukti bahwa runtime sudah dikonfigurasi di proyek ini.

## Sumber resmi yang diperiksa

- [Dokumentasi wallet pada tag v0.1.5](https://github.com/Trac-Systems/intercom-dex/blob/v0.1.5/docs/WALLETS.md)
- [CLI resmi pada tag v0.1.5: `bin/dex.mjs`](https://github.com/Trac-Systems/intercom-dex/blob/v0.1.5/bin/dex.mjs)
- [Implementasi setup pada tag v0.1.5: `src/wallets/setup.js`](https://github.com/Trac-Systems/intercom-dex/blob/v0.1.5/src/wallets/setup.js)
- [Panduan operator/runtime pada tag v0.1.5](https://github.com/Trac-Systems/intercom-dex/blob/v0.1.5/docs/OPERATORS.md)
- [Profil network pada tag v0.1.5](https://github.com/Trac-Systems/intercom-dex/blob/v0.1.5/docs/NETWORKS.md)

Pemeriksaan perilaku kode memakai sumber dalam arsip resmi yang SHA-256-nya cocok dengan pin di atas. Tautan tag memudahkan pembacaan; arsip beserta hash adalah acuan byte yang digunakan skrip.

## Bukti pengujian dan batasnya

[`TEST_REPORT.md`](TEST_REPORT.md) menjelaskan **31 pemeriksaan pada Node 24.19.0 dan 31 pada Node 26.12.0**, memakai fixture/wallet sintetis. Pemeriksaan mencakup sumber tetap tidak berubah, wallet Solana antar-setup berbeda, penolakan overwrite dan arsip tidak aman, serta tidak ada peer/trader/MCP atau transaksi jaringan yang dijalankan.

Tahap `prepare` lengkap sebelumnya juga berhasil di Sandbox pada Node 24; log disertakan. Pengujian ini bukan audit keamanan menyeluruh dan berlangsung di Linux Sandbox, bukan laptop Ubuntu/WSL pengguna. Dependency npm, proof key, konfigurasi runtime, konektivitas market, integrasi Hermes, dan transaksi nyata tetap memerlukan pemeriksaan terpisah.
