# Tinjauan Hermes — Intercom DEX v0.1.5

**Commit kode yang ditinjau (main):** `57859693b4ab9cb6988af89559ef213587361cf6`
**Branch laporan dan instruksi:** `hermes/review-2026-10-21`
**Tanggal:** 2026-10-21

## Kesimpulan

Langkah berikutnya hanya pemeriksaan prasyarat baca-saja dalam [instruksi Hermes](HERMES_NEXT_COMMAND.md). Dokumen itu tidak mengizinkan download, pemasangan dependency, wallet setup, atau start DEX.

Worker merupakan proses terpisah dan berada di luar lingkup review ini. Review ini tidak memeriksa, menghentikan, memulai ulang, atau mengubah worker.

## Temuan kode

- Helper mematok Intercom DEX v0.1.5 dengan SHA-256 `63cef1771c8596e095cd7eaa52da2c74bc3670fad54f0d7b20f32b8a1b547b56`.
- Fasenya dipisah menjadi `plan`, `prepare`, dan `wallet-setup`. `plan` hanya menampilkan rencana.
- Kode helper `prepare` mengunduh dan memverifikasi arsip, memasang dependency release dan peer dengan `npm ci`, lalu membuat manifest, konfigurasi setup-only, dan direktori data kosong. Kode helper pada fase ini tidak membaca isi wallet/keystore dan tidak memulai peer, trader, atau MCP.
- `wallet-setup` adalah langkah terpisah yang membuat wallet Solana baru dan salinan terenkripsi RESET/Trac. Salinan RESET/Trac mempertahankan alamat, otoritas, dan dana yang sama dengan sumber, jadi bukan isolasi dana.
- Laporan sebelumnya mencatat tes sintetis lulus pada Node 24.19.0 dan 26.12.0. Tes itu tidak dijalankan ulang untuk revisi dokumentasi ini dan bukan bukti runtime/market/transaksi.

## Batas verifikasi dan risiko

`npm ci` dapat menjalankan lifecycle scripts pihak ketiga. Helper, checksum arsip, dan pemeriksaan hash bukan sandbox: kode dependency berjalan dengan hak akun pengguna, dan efek samping di luar direktori proyek tidak dibatasi oleh pemeriksaan hash. Karena itu, instruksi sekarang berhenti pada preflight baca-saja; pemasangan dependency memerlukan peninjauan dan izin terpisah.

Catatan uji sebelumnya menyebut dependency usang dan dua dependency Git tanpa integrity metadata. Ini bukan audit keamanan menyeluruh atau jaminan dependency aman.

Belum ada runtime config, proof key, Hermes MCP, peer, trader, pemeriksaan live registry, atau transaksi yang dibuat/dijalankan oleh helper ini. Dokumentasi upstream menyebut MCP dapat memulai trader, jadi jangan anggap konfigurasi MCP sebagai akses pasif.

## Urutan yang diizinkan sekarang

1. Jalankan hanya preflight baca-saja dalam `HERMES_NEXT_COMMAND.md`.
2. Laporkan versi alat, status checkout secara ringkas, dan ruang disk yang tersedia kepada pemilik; jangan unggah output mentah atau path lokal ke GitHub.
3. Berhenti. `prepare` belum diizinkan oleh instruksi ini; evaluasi risiko dependency dan minta keputusan terpisah sebelum tahap tersebut.

Revisi ini hanya mengubah dokumentasi. Tidak ada helper yang dijalankan, wallet dibuka, konfigurasi Hermes diubah, worker disentuh, atau proses trading dimulai.
