# Setup aman Intercom DEX v0.1.5

Skrip ini disiapkan untuk Ubuntu/WSL di laptop Anda, tetapi **belum dijalankan di laptop**. Checkout lokal disiapkan untuk `zeroichi666/resetDex`; belum ada push pada tahap persiapan ini. Integrasi Hermes belum dilakukan, dan setup ini belum merupakan DEX yang sepenuhnya operasional.

Lihat [penjelasan kode, sumber resmi, dan rencana Hermes](PROJECT_OVERVIEW.md) serta [laporan pengujian](TEST_REPORT.md).

## Apa yang dikerjakan

`setup_intercom_dex.py` mengunci aset rilis resmi **v0.1.5**, bukan branch `main`. SHA-256 wajib cocok:

```text
63cef1771c8596e095cd7eaa52da2c74bc3670fad54f0d7b20f32b8a1b547b56
```

Tahap `prepare` mengunduh dan memverifikasi arsip, lalu menjalankan `npm ci` pada direktori rilis dan `peer`. Tahap ini tidak membaca wallet. Instalasi npm memerlukan jaringan dan dapat menjalankan lifecycle dependency; jangan jalankan instalasi sebagai root/sudo.

Tahap `wallet-setup` membaca **keystore RESET yang sudah terenkripsi** dari `~/.reset-signer/keystore.json`, membuat snapshot terenkripsi sementara, lalu menjalankan CLI resmi:

```text
node <rilis>/bin/dex.mjs setup --config <setup-only.json> --import-reset-keystore <snapshot-terenkripsi>
```

Ini memakai mekanisme resmi `--import-reset-keystore` dengan isi yang sama seperti direktori sumber. Snapshot mencegah CLI menulis ke lokasi wallet mining. Snapshot dibersihkan setelah proses berakhir normal atau gagal; setelah proses dibunuh paksa/komputer mati, snapshot terenkripsi dapat tertinggal dan harus diperiksa sendiri. Tidak ada mnemonic atau private key yang diekspor ke plaintext.

Hasilnya adalah **salinan DEX terenkripsi terpisah untuk identitas RESET/Trac yang sama**, serta **wallet Solana baru**. Salinan RESET bukan identitas atau dana yang terisolasi: ketika kelak dijalankan untuk trading, salinan ini punya kewenangan atas alamat RESET/Trac yang sama dengan wallet asal.

**Jangan pernah menggunakan recovery phrase yang sebelumnya terpapar.** Skrip tidak menyediakan impor Solana, impor mnemonic, atau parameter perintah trading.

## Menjalankan nanti, setelah Anda siap

Prasyarat: Linux Ubuntu/WSL, **Python 3.12+**, Node.js **23.11+** (Node 26 memenuhi batas versi upstream), npm, curl, dan git. Gunakan filesystem Linux di bawah `HOME`, bukan `/mnt/c`. Sumber harus dimiliki user Anda, direktorinya `0700`, dan `keystore.json` berupa file biasa `0600`. Skrip hanya memeriksa izin sumber—tidak mengubahnya otomatis.

Tinjau rencana tanpa unduhan, pembacaan isi wallet, atau penulisan:

```bash
python3 setup_intercom_dex.py plan
```

Instal rilis terkunci saja:

```bash
python3 setup_intercom_dex.py prepare
```

Lalu, jika Anda sudah siap membuat wallet DEX, jalankan langsung di terminal Anda:

```bash
python3 setup_intercom_dex.py wallet-setup
```

Prompt resmi meminta password DEX baru minimal 12 karakter dan password keystore RESET yang sudah ada. Ketik langsung pada prompt tersembunyi. Wrapper tidak menerima password lewat argumen atau menyimpannya; password lingkungan yang diwarisi juga diabaikan. Jangan memakai `tee`, rekaman terminal, atau memasukkan recovery phrase.

Folder default:

```text
~/.local/share/intercom-dex-v0.1.5/
  intercom-dex-v0.1.5/   # kode + dependency
  setup-only.json       # konfigurasi minimum khusus setup, bukan runtime
  prepared.json         # manifest hash file rilis
  data/
    keyring.json        # Solana baru + kunci DEX, terenkripsi
    trac-wallet.json    # salinan identitas RESET/Trac, terenkripsi
  setup-complete.json   # hanya ditulis setelah setup sukses
```

Folder ini terpisah dari `~/src/resetmnr` dan `~/.reset-signer`. Opsi `--root /path/baru/di/HOME` tersedia jika ingin lokasi lain; lokasi yang bertumpang tindih dengan proyek mining atau sumber keystore ditolak.

## Tidak ada start atau transaksi

Skrip **tidak** menjalankan peer, trader, MCP, dashboard, service/autostart, pengecekan saldo jaringan, offer, trade, transfer, atau transaksi apa pun. Tidak ada pembentukan proof key atau perubahan konfigurasi Hermes. `setup-only.json` sengaja tidak memuat konfigurasi runtime lengkap.

Integrasi Hermes nanti membutuhkan tahap terpisah: proof key, konfigurasi peer/trader yang benar, keamanan password dan payout lock, lalu izin eksplisit sebelum start. Menyalakan MCP upstream dapat otomatis menyalakan trader; karena itu jangan menganggap memasukkan konfigurasi MCP hanya sebagai kegiatan pasif. Belum ada izin untuk tahap tersebut.

## Tidak menimpa data

`prepare` menolak direktori tujuan yang sudah ada. `wallet-setup` menolak data wallet lama maupun parsial, konfigurasi yang diubah, atau sumber rilis yang berubah sejak instalasi. Skrip tidak menghapus atau menimpa wallet untuk membuat retry berhasil.

Jika instalasi/setup terputus, simpan folder tersebut dan periksa isinya sebelum bertindak. Bila hanya instalasi yang gagal dan belum ada wallet, Anda dapat memilih **root baru** setelah meninjau kegagalan. Bila ada wallet/keystore parsial atau lengkap, jangan mengulang setup ke lokasi baru secara membabi buta: pastikan dahulu data dan backup mana yang harus dipertahankan. Lock `.wallet-setup.lock` yang tertinggal setelah proses dibunuh paksa perlu ditinjau manual; pastikan tidak ada proses aktif sebelum perubahan apa pun.

Sesudah sukses, cadangkan folder data terenkripsi dan simpan password DEX secara terpisah. Hasil setup menampilkan alamat publik saja; tidak ada alamat yang didanai oleh skrip ini.

## Bukti dan pengujian

Lihat `TEST_REPORT.md` dan folder `tests/`. Semua wallet pengujian bersifat sintetis dan tidak boleh menerima dana. Tes memakai CLI setup resmi, bukan wallet pengguna.

Sumber: [rilis resmi v0.1.5](https://github.com/Trac-Systems/intercom-dex/releases/tag/v0.1.5), [dokumentasi wallet pada tag v0.1.5](https://github.com/Trac-Systems/intercom-dex/blob/v0.1.5/docs/WALLETS.md), serta kode `bin/dex.mjs` dan `src/wallets/setup.js` dalam arsip yang telah diverifikasi.
