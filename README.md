# MIMIC THE EMOJI 

<img align="center" src="assets/poster.jpg" height="700" />

## 📋 Deskripsi Proyek 
<i>Mimic the Emoji</i> adalah sebuah game berbasis kamera yang mendeteksi ekspresi wajah pemain menggunakan DeepFace. Pemain akan ditampilkan 3 emoji secara acak, kemudian harus menirukan ekspresi emoji satu per satu dengan benar dan secepat mungkin untuk mendapatkan skor tertinggi.

Cara Kerja:
1. Mendeteksi wajah pemain secara real-time menggunakan webcam dan DeepFace.
2. Menampilkan 3 emoji acak dan menentukan satu emoji sebagai target yang harus ditiru.
3. Mendeteksi ekspresi wajah pemain dan mencocokkannya dengan emoji target.
4. Memberikan skor setiap kali pemain berhasil menirukan ekspresi dengan benar.
5. Memberikan efek suara (SFX) untuk jawaban benar, selesai ronde, dan game over.
6. Menampilkan Game Over screen yang berisi skor akhir dan high score terbaik pemain.

## 📋 Anggota Kelompok
<table>
  <tr>
    <td align="left">
      <b>Dzaki Gastiadirrijal</b><br/>
      122140030<br/>
      <a href="https://github.com/Dzaki-G">github.com/Dzaki-G</a>
    </td>
  </tr>

  <tr>
    <td align="left">
      <b>Bagas Andreanto</b><br/>
      122140017<br/>
      <a href="https://github.com/bagas017">github.com/bagas017</a>
    </td>
  </tr>

  <tr>
    <td align="left">
      <b>Fawwaz Abhitah S</b><br/>
      122140014<br/>
      <a href="https://github.com/FawwazAbhitah-122140014">github.com/FawwazAbhitah-122140014</a>
    </td>
  </tr>
</table>


## 📋 Teknologi Aplikasi
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
  </tr>

  <tr>
    <td><b>DeepFace</b></td>
    <td>
      Digunakan untuk mendeteksi emosi wajah secara real-time. 
      Sistem menggabungkan DeepFace dengan Haarcascade:
      Haarcascade mendeteksi posisi wajah dengan cepat,
      lalu DeepFace menganalisis ekspresi secara akurat.
    </td>
  </tr>

  <tr>
    <td><b>OpenCV (Haarcascade)</b></td>
    <td>
      Dipakai sebagai pendeteksi wajah ringan dan cepat untuk menentukan area wajah 
      dan meletakkan emoji pada UI. Memberikan bounding box sebelum DeepFace memproses emosi.
    </td>
  </tr>

  <tr>
    <td><b>Pygame Mixer</b></td>
    <td>
      Mengelola seluruh audio dalam game, seperti background music (BGM) dan sound effect (SFX). 
      Memungkinkan pemutaran banyak suara bersamaan dan kontrol volume yang mudah.
    </td>
  </tr>

</table>

## 📋 Logbook Mingguan

### TABEL LOGBOOK MINGGUAN
<table>

  <tr>
    <td><b>Minggu 1 (8 Nov 2025)</b></td>
    <td>
      Setup awal proyek di GitHub, pembuatan struktur folder, serta melakukan pengujian awal terhadap model deteksi emosi yang akan digunakan.
    </td>
  </tr>

  <tr>
    <td><b>Minggu 2 (16 Nov 2025)</b></td>
    <td>
      Pengembangan logika dasar game, seperti alur gameplay dan sistem penilaian, serta penambahan dan penyesuaian aset emoji untuk kebutuhan permainan.
    </td>
  </tr>

  <tr>
    <td><b>Minggu 3 (25 Nov 2025)</b></td>
    <td>
      Implementasi fitur Main Menu dan Game Over screen, termasuk navigasi antar scene serta penampilan skor akhir dan high score.
    </td>
  </tr>

  <tr>
    <td><b>Minggu 4 (26 Nov 2025)</b></td>
    <td>
      Finalisasi tampilan UI game, penyempurnaan elemen visual, penempatan elemen pada layar, dan perbaikan keseluruhan user interface.
    </td>
  </tr>

</table>


## 📋 Instruksi Instalasi
### 1. Clone Repository

Clone repository ini ke komputer anda:
```bash
git clone https://github.com/Dzaki-G/TUBES-MULMED-Emoji.git
cd TUBES-MULMED-Emoji
```


### 2. Buat dan Aktifkan Virtual Environment
pada terminal anda jalankan:
```bash
# buat venv baru
python -m venv venv
```

Lalu Aktifkan venv pada terminal:

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

Pada terminal, Install dari `requirements.txt` file pada:
```bash
pip install -r requirements.txt
```

## 🏃‍♀️ How to Run

### To Run MIMIC THE EMOJI

Jalankan ini pada terminal(pastikan sudah masuk ke directory TUBES-MULMED-Emoji)
```bash
python game_emotion.py
```