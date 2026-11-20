# 1. TULIS 1 KODE YANG MAU KAMU UJI DI SINI (GANTI-GANTI DI SINI)
kode_uji = 'umur: int = "dua puluh"'

# 2. JALANKAN KODENYA
try:
    exec(kode_uji)
    print("Hasil: KODE VALID (TIDAK ADA ERROR)")
except Exception as e:
    print(f"Hasil Error: {type(e).__name__} -> {e}")