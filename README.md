# Plankton - Asisten Tanaman AI

Website Flask dengan fitur analisis tanaman menggunakan Plant.id API dan chatbot berbasis Groq AI yang fokus pada pertanian dan budidaya tanaman.

## 🌿 Fitur Utama

1. **Analisis Tanaman dari Foto**
   - Upload gambar tanaman
   - Identifikasi otomatis menggunakan Plant.id API
   - Menampilkan nama tanaman dan tingkat keyakinan

2. **Chat Bot AI (Groq)**
   - Dialog interaktif tentang tanaman
   - Fokus topik yang dapat dipilih (sayuran, buah, tanaman hias, dll)
   - Respons berdasarkan pengetahuan pertanian mendalam
   - Dukungan Bahasa Indonesia penuh

3. **Riwayat Chat**
   - Penyimpanan otomatis semua percakapan
   - Dapat dilihat, diunduh, atau dihapus
   - Database SQLite untuk penyimpanan lokal

4. **Riwayat Analisis Tanaman**
   - Penyimpanan hasil analisis tanaman
   - Galeri gambar yang telah dianalisis
   - Akurasi dan keyakinan terdeteksi

## 📋 Requirement

- Python 3.8+
- Flask 2.3.3
- Flask-SQLAlchemy 3.0.5
- python-dotenv
- requests
- groq SDK
- Pillow

## 🚀 Instalasi & Setup

### 1. Clone dan Setup Environment

```bash
cd /home/randukumbolo/Workspace/vscode/project/uji_coba_websites_bu_priska/plankton
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Konfigurasi API Keys

Copy `.env.example` ke `.env`:
```bash
cp .env.example .env
```

Edit `.env` dan masukkan API keys Anda:
```
PLANTID_API_KEY=your_plantid_api_key_here
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_here
```

**Cara mendapatkan API Keys:**

- **Plant.id API**: Daftar di https://plant.id
- **Groq API**: Daftar di https://console.groq.com/keys

### 3. Jalankan Aplikasi

```bash
python run.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## 📁 Struktur Proyek

```
plankton/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models.py             # Database models
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Styling
│   │   ├── js/
│   │   │   ├── main.js       # Chat functionality
│   │   │   └── history.js    # History page
│   │   └── uploads/          # Folder upload gambar
│   ├── templates/
│   │   ├── index.html        # Halaman chat utama
│   │   └── history.html      # Halaman riwayat
│   └── routes/
│       ├── main.py           # Route utama
│       ├── chat.py           # API chat
│       └── plant_analysis.py # API analisis tanaman
├── app/services/
│   ├── groq_service.py       # Integrasi Groq AI
│   └── plantid_service.py    # Integrasi Plant.id API
├── run.py                    # Entry point
├── requirements.txt          # Dependencies
├── .env.example              # Template environment
└── README.md                 # Dokumentasi ini
```

## 🔌 API Endpoints

### Chat API

- `POST /api/chat/send` - Kirim pesan chat
  ```json
  {
    "message": "Bagaimana cara menanam tomat?",
    "plant_topic": "sayuran"
  }
  ```

- `GET /api/chat/history?page=1&per_page=20` - Ambil riwayat chat

- `DELETE /api/chat/history/<id>` - Hapus chat tertentu

- `POST /api/chat/history/clear` - Hapus semua chat

### Plant Analysis API

- `POST /api/plant/analyze` - Analisis foto tanaman (form-data)

- `GET /api/plant/history?page=1&per_page=10` - Ambil riwayat analisis

- `DELETE /api/plant/history/<id>` - Hapus analisis tertentu

## 🎨 Fitur UI/UX

- **Responsive Design**: Bekerja di desktop dan mobile
- **Dark Mode Ready**: CSS variables untuk tema mudah diubah
- **Real-time Chat**: Loading indicator dan animasi
- **Image Preview**: Tampilan instan hasil analisis
- **History Management**: Pagination dan filter

## 🔒 Security

- Secret key untuk session (ubah di production)
- Database lokal (SQLite) - privacy terjaga
- Input validation di semua endpoint
- File upload validation (whitelist format)

## 📝 Cara Menggunakan

### 1. Chat dengan AI

1. Buka halaman utama
2. Pilih topik tanaman dari dropdown
3. Ketik pertanyaan Anda
4. Tekan Enter atau klik tombol kirim
5. AI akan merespons berdasarkan topik yang dipilih

### 2. Analisis Tanaman

1. Klik area upload atau drag & drop gambar
2. Pilih foto tanaman Anda
3. Tunggu hasil analisis
4. Lihat nama tanaman dan tingkat keyakinan
5. Tanyakan lebih lanjut tentang tanaman tersebut

### 3. Lihat Riwayat

1. Klik tab "Riwayat"
2. Pilih antara "Chat History" atau "Analisis Tanaman"
3. Gunakan pagination untuk melihat lebih banyak
4. Klik tombol hapus untuk menghapus item tertentu

## 🛠️ Troubleshooting

### Error: "Import could not be resolved"
- Pastikan virtual environment aktif
- Jalankan `pip install -r requirements.txt`

### Error API Keys
- Verifikasi API keys di `.env`
- Pastikan API keys valid dan tidak expired

### Database Error
- Hapus `plankton.db` untuk reset database
- Atau jalankan `python -c "from app import create_app; create_app()"`

### Upload Error
- Cek folder `app/static/uploads` ada permission write
- File harus format gambar (jpg, png, gif, webp)

## 📚 Dokumentasi Lengkap

### Groq AI Model

Model yang digunakan: `mixtral-8x7b-32768`

Prompt system disesuaikan untuk:
- Identifikasi tanaman
- Perawatan tanaman
- Cara budidaya
- Masalah penyakit
- Nutrisi tanaman
- Teknologi pertanian

### Plant.id API

Detail yang diambil:
- Nama tanaman umum
- Probability/keyakinan
- URL gambar referensi
- Deskripsi tanaman
- Klasifikasi taxonomy

## 🚀 Development

### Menambah Topik Baru

Edit `app/templates/index.html`:
```html
<option value="topik_baru">Nama Topik</option>
```

### Mengubah Model AI

Edit `app/services/groq_service.py`:
```python
self.model = "model_name_lain"  # Lihat Groq documentation
```

### Database Schema

Edit `app/models.py` untuk menambah kolom baru, kemudian:
```bash
rm plankton.db
python run.py
```

## 📞 Support

Jika ada masalah:
1. Periksa console error (`Ctrl+Shift+J`)
2. Lihat server logs
3. Verifikasi API keys
4. Cek koneksi internet

## 📄 License

Proyek open source untuk keperluan pembelajaran dan penggunaan pribadi.

## 🎯 Roadmap

- [ ] Autentikasi user
- [ ] Cloud storage untuk gambar
- [ ] Export riwayat ke PDF
- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] Rekomendasi berdasarkan riwayat
- [ ] Integrasi cuaca lokal
- [ ] Push notifications

---

**Dibuat dengan ❤️ untuk komunitas pertanian digital**
