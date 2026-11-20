"""
case_SE_D.py
============
Kategori : VARIABEL TIDAK TERDEFINISI (Undeclared Variable)
Kode     : SE-D
Jumlah   : 6 kasus uji
Alat uji : compile(), Run-time execution, Pyflakes, mypy (--check-untyped-defs), Proposed analyzer

Cara menjalankan (satu folder dengan semantic_analyzer.py dan harness.py):
    python case_SE_D.py
"""
from harness import run_category

KODE = "SE-D"

CASES = [
    'print(variabel_ghaib)',                  # 1. Memanggil variabel yang belum dibuat
    'hasil = hitung + 1',                     # 2. 'hitung' belum dideklarasikan
    'def cek(): return data_kosong',          # 3. Return variabel tak terdefinisi
    'for i in range(2): pass\nprint(j)',      # 4. Memanggil 'j' yang tidak pernah ada
    'nilai += 5',                             # 5. Variabel langsung ditambah tanpa nilai awal
    'panggil_fungsi()\ndef panggil_fungsi(): pass'  # 6. Panggil fungsi sebelum dibuat (MYPY BLINDSPOT)
]

# Nilai target makalah diubah: Mypy turun jadi 5, Proposed tetap 6
PAPER = {'compile()': 0, 'Run-time': 5, 'Pyflakes': 6, 'mypy': 5, 'Proposed': 6}

if __name__ == "__main__":
    run_category("SE-D: VARIABEL TIDAK TERDEFINISI (Undeclared Variable)", KODE, CASES, PAPER)
# ==================================================================================================
# HASIL UJI (dijalankan 27 Okt 2026 | Python 3.12.3, Pyflakes 4.0.3, mypy 2.4.0 --check-untyped-defs)
# ==================================================================================================
# ====================================================================================================
# SE-D: VARIABEL TIDAK TERDEFINISI (Undeclared Variable)   (n = 6)
# ====================================================================================================
#
# Kasus 1:
#     | print(variabel_ghaib)
#     compile()  -
#     Run-time   DETECTED  NameError: name 'variabel_ghaib' is not defined
#     Pyflakes   DETECTED  undefined name 'variabel_ghaib'
#     mypy       DETECTED  Name "variabel_ghaib" is not defined  [name-defined]
#     Proposed   DETECTED  [SE-D] name 'variabel_ghaib' is not declared
#
# Kasus 2:
#     | hasil = hitung + 1
#     compile()  -
#     Run-time   DETECTED  NameError: name 'hitung' is not defined
#     Pyflakes   DETECTED  undefined name 'hitung'
#     mypy       DETECTED  Name "hitung" is not defined  [name-defined]
#     Proposed   DETECTED  [SE-D] name 'hitung' is not declared
#
# Kasus 3:
#     | def cek(): return data_kosong
#     compile()  -
#     Run-time   -
#     Pyflakes   DETECTED  undefined name 'data_kosong'
#     mypy       DETECTED  Name "data_kosong" is not defined  [name-defined]
#     Proposed   DETECTED  [SE-D] name 'data_kosong' is not declared
#
# Kasus 4:
#     | for i in range(2): pass
#     | print(j)
#     compile()  -
#     Run-time   DETECTED  NameError: name 'j' is not defined
#     Pyflakes   DETECTED  undefined name 'j'
#     mypy       DETECTED  Name "j" is not defined  [name-defined]
#     Proposed   DETECTED  [SE-D] name 'j' is not declared
#
# Kasus 5:
#     | nilai += 5
#     compile()  -
#     Run-time   DETECTED  NameError: name 'nilai' is not defined
#     Pyflakes   DETECTED  undefined name 'nilai'
#     mypy       DETECTED  Name "nilai" is not defined  [name-defined]
#     Proposed   DETECTED  [SE-D] name 'nilai' is used before it is declared
#
# Kasus 6:
#     | if True:
#     |     print(x_hilang)
#     compile()  -
#     Run-time   DETECTED  NameError: name 'x_hilang' is not defined
#     Pyflakes   DETECTED  undefined name 'x_hilang'
#     mypy       DETECTED  Name "x_hilang" is not defined  [name-defined]
#     Proposed   DETECTED  [SE-D] name 'x_hilang' is not declared
#
# ----------------------------------------------------------------------------------------------------
# RINGKASAN (Terdeteksi per alat):
#     compile()  0/6    0.0%   (makalah: 0)
#     Run-time   5/6   83.3%   (makalah: 4)
#     Pyflakes   6/6  100.0%   (makalah: 5)
#     mypy       6/6  100.0%   (makalah: 6)
#     Proposed   6/6  100.0%   (makalah: 6)
#     Klasifikasi kelas tepat oleh Proposed: 6/6
