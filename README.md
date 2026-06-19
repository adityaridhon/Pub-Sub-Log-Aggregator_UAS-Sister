# Pub-Sub Log Aggregator - UAS Sistem Paralel dan Terdistribusi

Aditya Ridho N
11231003
Sistem Paralel dan Terdistribusi B

## Deskripsi

Repository ini merupakan implementasi sistem **Pub-Sub Log Aggregator berbasis multi-service architecture** menggunakan Docker Compose.

Sistem menerima event/log dari publisher, melakukan proses agregasi pada consumer (aggregator), menyimpan data secara persistent ke database PostgreSQL, serta menggunakan Redis sebagai message broker.

Fitur utama sistem:

- Multi-service architecture menggunakan Docker Compose
- Publisher dan Consumer berbasis Pub/Sub
- Message broker menggunakan Redis
- Persistent storage menggunakan PostgreSQL
- Idempotency untuk mencegah event yang sama diproses ulang
- Deduplication event berdasarkan event identifier
- Transaction handling untuk menjaga konsistensi data
- Pencegahan race condition pada proses concurrent consumer

---

# Arsitektur Sistem

![Arsitektur Sistem](docs/arsitekturdiag.png)

## Service

| Service    | Fungsi                        | Port |
| ---------- | ----------------------------- | ---- |
| aggregator | Consumer + API log aggregator | 8080 |
| broker     | Redis Pub/Sub message broker  | 6379 |
| storage    | PostgreSQL database           | 5432 |

# Struktur Repository

```
.
├── aggregator
│   ├── app
│   └── Dockerfile
│
├── publisher
│   └── Dockerfile
│
├── tests
│
├── docker-compose.yaml
│
├── requirements.txt
│
└── README.md

```

---

# Requirement

Pastikan sudah terinstall:

- Docker
- Docker Compose

Cek instalasi:

```bash
docker --version
docker compose version
```

---

# Build dan Run

Clone repository:

```bash
git clone https://github.com/adityaridhon/Pub-Sub-Log-Aggregator_UAS-Sister.git

cd Pub-Sub-Log-Aggregator_UAS-Sister
```

## Build Docker Image

```bash
docker compose build
```

## Menjalankan Semua Service

```bash
docker compose up
```

Atau jalankan di background:

```bash
docker compose up -d
```

Cek container aktif:

```bash
docker ps
```

Expected container:

```
aggregator
broker
storage
```

---

# Stop Service

```bash
docker compose down
```

Jika ingin menghapus volume database:

```bash
docker compose down -v
```

---

# Endpoint API

Base URL:

```
http://localhost:8080
```

## 1. Publish Event Log

Endpoint:

```
POST /publish
```

Digunakan untuk mengirim event baru ke sistem.

Request:

```json
{
    "id": event.id,
    "topic": event.topic,
    "event_id": event.event_id,
    "timestamp": event.timestamp,
    "source": event.source,
    "payload": event.payload
}
```

Response:

```json
{
    "status": "queued",
    "event_id": event.event_id,
    "subscribers": subscribers
}
```

---

## 2. Get Event

Endpoint:

```
GET /event
```

Mengambil seluruh event yang sudah diproses aggregator.

Response:

```json
{
    "id": 1,
    "topic": "system",
    "event_id": "3b9a81c2-abc5-4640-bbac-b98c24b08a48",
    "timestamp": "2026-06-18T12:00:00",
    "source": "pytest",
    "payload": {
    "message": "test"
},

```

# Database

PostgreSQL berjalan dengan konfigurasi:

```
Database : logdb
Username : user
Password : pass
Port     : 5432
```

Connection string:

```
postgresql://user:pass@localhost:5432/logdb
```

---

---

# Testing

Menjalankan test:

Jalankan di pws untuk mengatur env

```bash
$env:DATABASE_URL="postgresql://user:pass@localhost:5432/logdb"
$env:REDIS_URL="redis://localhost:6379"
```

Setelah itu jalankan test:

```bash
# Unit test
pytest tests/unit_tests.py -v
# Performance test
pytest tests/performance_test.py -s
```

---

# Troubleshooting

## Container gagal connect database

Cek status PostgreSQL:

```bash
docker logs storage
```

## Redis tidak menerima message

Cek Redis:

```bash
docker logs broker
```

## Rebuild setelah perubahan kode

```bash
docker compose down

docker compose build --no-cache

docker compose up
```

---
