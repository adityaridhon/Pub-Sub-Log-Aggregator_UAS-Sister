Aditya Ridho Nugroho
11231003
UAS - Sistem Paralel dan Terdistribusi B

## Deskripsi
Repository ini berisi sistem Pub-Sub log aggregator multi-service yang berjalan dengan Docker Compose. Sistem yang dibangun mendukung idempotency (consumer tidak memproses ulang event yang sama), deduplication, serta transaksi/konkurensi yang mencegah race condition dan memastikan konsistensi data. Semua layanan berjalan pada jaringan lokal Compose, tanpa akses layanan eksternal publik.

## Build dan Run Sistem
soon