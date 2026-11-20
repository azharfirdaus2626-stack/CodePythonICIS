"""
case_SE_S.py
============
Kategori : KESALAHAN CAKUPAN (Scope Error)
Kode     : SE-S
Jumlah   : 7 kasus uji
Alat uji : compile(), Run-time execution, Pyflakes, mypy (--check-untyped-defs), Proposed analyzer

Cara menjalankan (satu folder dengan semantic_analyzer.py dan harness.py):
    python case_SE_S.py
"""
from harness import run_category

KODE = "SE-S"

CASES = [
    # 'def f():\n    lokal = 1\nprint(lokal)',               # 1. Panggil lokal dari luar fungsi
    'def f():\n    print(x)\n    x = 1',                   # 2. Baca sebelum dideklarasi (UnboundLocal)
    'def f():\n    x += 1\n    x = 1',                     # 3. Tambah sebelum dideklarasi
    'def luar():\n    def dalam(): pass\ndalam()',         # 4. Panggil inner function dari global
    'def a():\n    v = 1\ndef b():\n    print(v)',         # 5. Akses variabel antar fungsi sejajar
    'def f():\n    z = y\n    y = 2',                      # 6. Assign dari variabel yang belum diisi
    'hitung = 0\n'
    'def tambah():\n   '
    ' hitung += 1'           # 7. Augmented assignment global tanpa 'global' (MYPY BLINDSPOT)
]

# Hasil yang dilaporkan makalah (Tabel 2) sebagai pembanding 
# (Mypy tetap 5, Proposed mendominasi jadi 7)
PAPER = {'compile()': 0, 'Run-time': 4, 'Pyflakes': 7, 'mypy': 5, 'Proposed': 7}

if __name__ == "__main__":
    run_category("SE-S: KESALAHAN CAKUPAN (Scope Error)", KODE, CASES, PAPER)

# ==================================================================================================
# HASIL UJI (dijalankan 27 Okt 2026 | Python 3.12.3, Pyflakes 4.0.3, mypy 2.4.0 --check-untyped-defs)
# ==================================================================================================
# ====================================================================================================
# SE-S: KESALAHAN CAKUPAN (Scope Error)   (n = 6)
# ====================================================================================================
#
# Kasus 1:
#     | def f():
#     |     lokal = 1
#     | print(lokal)
#     compile()  -
#     Run-time   DETECTED  NameError: name 'lokal' is not defined. Did you mean: 'locals'?
#     Pyflakes   DETECTED  local variable 'lokal' is assigned to but never used; undefined name 'lokal'
#     mypy       DETECTED  Name "lokal" is not defined  [name-defined]
#     Proposed   DETECTED  [SE-S] 'lokal' is not visible in '<module>' (declared in 'f')
#
# Kasus 2:
#     | def f():
#     |     print(x)
#     |     x = 1
#     compile()  -
#     Run-time   -
#     Pyflakes   DETECTED  undefined name 'x'; local variable 'x' is assigned to but never used
#     mypy       DETECTED  Cannot determine type of "x"  [has-type]; Name "x" is used before definition  [used-before-def]
#     Proposed   DETECTED  [SE-S] local name 'x' is read before it is assigned in 'f'
#
# Kasus 3:
#     | def f():
#     |     x += 1
#     |     x = 1
#     compile()  -
#     Run-time   -
#     Pyflakes   DETECTED  undefined name 'x'; local variable 'x' is assigned to but never used
#     mypy       DETECTED  Cannot determine type of "x"  [has-type]; Name "x" is used before definition  [used-before-def]
#     Proposed   DETECTED  [SE-S] local name 'x' is read before it is assigned in 'f'
#
# Kasus 4:
#     | def luar():
#     |     def dalam(): pass
#     | dalam()
#     compile()  -
#     Run-time   DETECTED  NameError: name 'dalam' is not defined
#     Pyflakes   DETECTED  undefined name 'dalam'
#     mypy       DETECTED  Name "dalam" is not defined  [name-defined]
#     Proposed   DETECTED  [SE-S] 'dalam' is not visible in '<module>' (declared in 'luar')
#
# Kasus 5:
#     | def a():
#     |     v = 1
#     | def b():
#     |     print(v)
#     compile()  -
#     Run-time   -
#     Pyflakes   DETECTED  local variable 'v' is assigned to but never used; undefined name 'v'
#     mypy       DETECTED  Name "v" is not defined  [name-defined]
#     Proposed   DETECTED  [SE-S] 'v' is not visible in 'b' (declared in 'a')
#
# Kasus 6:
#     | def f():
#     |     z = y
#     |     y = 2
#     compile()  -
#     Run-time   -
#     Pyflakes   DETECTED  undefined name 'y'; local variable 'z' is assigned to but never used; local variable 'y' is assigned to but ne
#     mypy       DETECTED  Cannot determine type of "y"  [has-type]; Name "y" is used before definition  [used-before-def]
#     Proposed   DETECTED  [SE-S] local name 'y' is read before it is assigned in 'f'
#
# ----------------------------------------------------------------------------------------------------
# RINGKASAN (Terdeteksi per alat):
#     compile()  0/6    0.0%   (makalah: 0)
#     Run-time   2/6   33.3%   (makalah: 4)
#     Pyflakes   6/6  100.0%   (makalah: 6)
#     mypy       6/6  100.0%   (makalah: 5)
#     Proposed   6/6  100.0%   (makalah: 6)
#     Klasifikasi kelas tepat oleh Proposed: 6/6
