# Langkah berikutnya untuk Hermes — preflight baca-saja

**Commit kode yang ditinjau (main):** `57859693b4ab9cb6988af89559ef213587361cf6`
**Branch instruksi:** `hermes/review-2026-10-21`
**Rilis yang dipatok:** Intercom DEX v0.1.5

## Batas izin

Dokumen ini hanya mengizinkan pemeriksaan prasyarat lokal yang baca-saja. Dokumen ini **tidak mengizinkan `prepare` atau `wallet-setup`**.

Worker dan wallet adalah urusan terpisah. Jangan membaca file, jurnal, kredensial, atau proses worker; jangan menghentikan, memulai ulang, atau mengubah worker. Jangan membuka, membaca, mengimpor, atau mengubah wallet/keystore.

Alasan berhenti sebelum `prepare`: tahap itu menjalankan `npm ci`, yang dapat menjalankan lifecycle scripts pihak ketiga. Helper bukan sandbox, dan proses instalasi berjalan dengan akses akun pengguna. Hash rilis tidak membatasi efek samping kode dependency. Risiko ini perlu ditinjau sebelum instalasi pada WSL yang juga dipakai untuk wallet atau worker.

## Pemeriksaan yang diizinkan

Di terminal Linux/WSL, dari checkout repo `~/src/resetDex`, jalankan hanya pemeriksaan versi, alat, status checkout, dan ruang disk berikut. Jangan gunakan `sudo` dan jangan memasang atau memperbarui apa pun.

```sh
cd ~/src/resetDex || exit 1
printf 'checkout='; git rev-parse --short HEAD
if [ -z "$(git status --porcelain)" ]; then echo 'working_tree=clean'; else echo 'working_tree=has_local_changes'; fi
python3 --version
node --version
npm --version
for tool in curl git tar; do
  if command -v "$tool" >/dev/null 2>&1; then echo "$tool=available"; else echo "$tool=missing"; fi
done
df -Pk "$HOME" | awk 'NR==2 {print "home_free_kib=" $4}'
```

Perintah itu tidak membuka wallet, mengunduh rilis, menulis file, atau menjalankan peer/trader/MCP. Jangan tampilkan path pribadi atau output mentah ke GitHub. Ringkas hasil hanya untuk pemilik, tanpa wallet data.

## Syarat dan cara berhenti

- Prasyarat untuk `prepare` kelak: Python 3.12+, Node.js 23.11.0+, npm, curl, git, tar, ruang disk yang cukup, serta akses HTTPS.
- Jika repo memiliki perubahan lokal, versi alat kurang, ada error, atau ruang disk tidak cukup, laporkan ringkas dan berhenti. Jangan mengubah checkout atau memasang alat.
- Setelah pemeriksaan ini, laporkan hasil lalu berhenti. Jangan lanjutkan ke `python3 setup_intercom_dex.py prepare` dalam sesi/perintah yang sama.
- `prepare` memerlukan tinjauan dan izin terpisah setelah risiko lifecycle scripts ditangani. Bila suatu saat diizinkan, helper dapat menolak folder target yang sudah ada; jangan menghapusnya atau mencoba ulang otomatis.
- Dilarang menjalankan `wallet-setup`, membangun proof key, membuat konfigurasi runtime, mengaktifkan Hermes MCP, peer atau trader, membaca registry/order book, menawarkan atau mengambil order, menandatangani, mengirim, atau menyiarkan transaksi.

Rilis yang digunakan helper dipatok ke v0.1.5 dengan SHA-256 `63cef1771c8596e095cd7eaa52da2c74bc3670fad54f0d7b20f32b8a1b547b56`. Pemeriksaan preflight ini tidak mengunduh atau memverifikasi ulang arsip.
