# HR Management System

Aplikasi HR Management dengan fitur attendance berbasis face recognition, leave management, overtime request, dan dashboard analytics.

## Tech Stack

- **Backend**: Django 4.2+ & Django REST Framework
- **Frontend**: React (untuk halaman /absen)
- **Database**: PostgreSQL / SQLite
- **Face Recognition**: (akan diintegrasikan)

## Fitur Utama

- ✅ **Authentication** (Admin / Manager / Employee)
- ✅ **Attendance** (check-in / check-out dengan face recognition)
- ✅ **Leave Request** + approval flow dengan approval matrix
- ✅ **Overtime Request**
- ✅ **Dashboard** (summary per bulan)
- ✅ **Export** CSV / Excel

---

## Setup dari Awal (Development)

### 1. Clone Repository & Buat Virtual Environment

```bash
# Clone project
git clone <repository-url>
cd hr-management

# Buat virtual environment
python -m venv venv

# Aktivasi virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Buat file `.env` di root project:

```env
# Database Configuration
DB_ENGINE=sqlite
# DB_ENGINE=postgresql

# Jika pakai PostgreSQL, uncomment dan isi:
# DB_NAME=hr_management
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# Django Secret Key
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 4. Buat Project Structure

```bash
# Project sudah ada: config/ #django-admin startproject config .
# Buat apps yang dibutuhkan:

python manage.py startapp accounts      # Auth & User Management
python manage.py startapp attendance    # Attendance System
python manage.py startapp leaves        # Leave Request Management
python manage.py startapp overtime      # Overtime Request
python manage.py startapp dashboard     # Dashboard & Analytics
```

### 5. Migrate Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Buat Superuser

```bash
python manage.py createsuperuser
```

### 7. Jalankan Server

```bash
python manage.py runserver
```

Akses aplikasi di `http://localhost:8000`

---

## Setup dari Git (Existing Project)

### 1. Clone & Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd hr-management

# Buat virtual environment
python -m venv venv

# Aktivasi venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy .env.example ke .env (jika ada)
cp .env.example .env

# Edit .env sesuai kebutuhan
# nano .env atau buka dengan text editor
```

### 3. Database Setup

```bash
# Migrate database
python manage.py migrate

# Buat superuser untuk akses admin
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

---

## Project Structure

```
hr-management/
├── config/                 # Django project settings
│   ├── __init__.py
│   ├── settings.py        # Main settings (DB config)
│   ├── urls.py
│   └── wsgi.py
├── accounts/              # Authentication & User Management
├── attendance/            # Attendance System
├── leaves/                # Leave Management
├── overtime/              # Overtime Management
├── dashboard/             # Dashboard & Reports
├── venv/                  # Virtual environment
├── .env                   # Environment variables
├── .gitignore
├── db.sqlite3             # SQLite database (dev)
├── manage.py
├── requirements.txt
└── README.md
```

---

## Development Timeline (Target: 1 Minggu)

### Day 1-2: Core Setup
- ✅ Project initialization
- [ ] Models untuk semua apps
- [ ] Authentication & User roles

### Day 3-4: Main Features
- [ ] Attendance system (tanpa face recognition dulu)
- [ ] Leave request & approval matrix
- [ ] Overtime request

### Day 5-6: Dashboard & Export
- [ ] Dashboard dengan summary bulanan
- [ ] Export CSV/Excel functionality
- [ ] Testing

### Day 7: Face Recognition
- [ ] Integrasi face recognition di halaman /absen
- [ ] React frontend untuk camera
- [ ] Final testing

---

## Database Configuration

Project ini support 2 database:

### SQLite (Default - Development)
```env
DB_ENGINE=sqlite
```

### PostgreSQL (Production)
```env
DB_ENGINE=postgresql
DB_NAME=hr_management
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

---

## API Endpoints (akan dibuat)

```
/api/auth/login/
/api/auth/logout/
/api/attendance/checkin/
/api/attendance/checkout/
/api/leaves/request/
/api/leaves/approve/
/api/overtime/request/
/api/dashboard/summary/
/api/export/attendance/
```

---

## Catatan Development

- Fokus backend monolith dulu
- React hanya untuk halaman /absen (face recognition)
- Approval matrix untuk leave request
- Dashboard dengan summary per bulan
- Export ke CSV/Excel

---

## License

Private Project - Portfolio Purpose