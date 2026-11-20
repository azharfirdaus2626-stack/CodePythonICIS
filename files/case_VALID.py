"""
case_VALID.py
=============
Kategori : PROGRAM VALID (Negative Controls)
Kode     : VALID
Jumlah   : 10 kasus uji
Alat uji : compile(), Run-time execution, Pyflakes, mypy (--check-untyped-defs), Proposed analyzer

Cara menjalankan (satu folder dengan semantic_analyzer.py dan harness.py):
    python case_VALID.py
"""
from harness import run_category

KODE = "VALID"

CASES = [
    'def f():\n    x=1\n    def g(): nonlocal x; x=2\n    g()', # 1. Closure & nonlocal
    'hitung = 0\ndef tambah(): global hitung; hitung += 1',       # 2. Global counter
    'kuadrat = [x*x for x in range(5)]',                          # 3. Comprehensions
    'kali = lambda a, b: a * b',                                  # 4. Lambdas
    'class Siswa:\n    def __init__(self): self.nama = ""',       # 5. Classes
    'try:\n    x = 1/0\nexcept ZeroDivisionError: pass',          # 6. Exception handling
    'def f(a=1, *args): pass\nf(2, 3, 4)',                        # 7. Default & variadic
    'for i in range(3): pass\nprint(i)',                          # 8. Loop-carried variables
    'def a(): b()\ndef b(): a()',                                 # 9. Mutual recursion
    'hasil = 10 + 5.5'                                            # 10. Mixed numeric arithmetic
]

# Hasil yang dilaporkan makalah (Tabel 2) sebagai pembanding
PAPER = {'compile()': 0, 'Run-time': 0, 'Pyflakes': 0, 'mypy': 0, 'Proposed': 0}

if __name__ == "__main__":
    run_category("VALID: PROGRAM VALID (Negative Controls)", KODE, CASES, PAPER, valid=True)


# ==================================================================================================
# HASIL UJI (dijalankan 27 Okt 2026 | Python 3.12.3, Pyflakes 4.0.3, mypy 2.4.0 --check-untyped-defs)
# ==================================================================================================
# ====================================================================================================
# VALID: PROGRAM VALID (Negative Controls)   (n = 10)
# ====================================================================================================
#
# Kasus 1:
#     | def f():
#     |     x=1
#     |     def g(): nonlocal x; x=2
#     |     g()
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#
# Kasus 2:
#     | hitung = 0
#     | def tambah(): global hitung; hitung += 1
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#
# Kasus 3:
#     | kuadrat = [x*x for x in range(5)]
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#
# Kasus 4:
#     | kali = lambda a, b: a * b
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#
# Kasus 5:
#     | class Siswa:
#     |     def __init__(self): self.nama = ""
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#
# Kasus 6:
#     | try:
#     |     x = 1/0
#     | except ZeroDivisionError: pass
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#
# Kasus 7:
#     | def f(a=1, *args): pass
#     | f(2, 3, 4)
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#
# Kasus 8:
#     | for i in range(3): pass
#     | print(i)
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#
# Kasus 9:
#     | def a(): b()
#     | def b(): a()
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#
# Kasus 10:
#     | hasil = 10 + 5.5
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#
# ----------------------------------------------------------------------------------------------------
# RINGKASAN (False positive per alat):
#     compile()  0/10    0.0%   (makalah: 0)
#     Run-time   0/10    0.0%   (makalah: 0)
#     Pyflakes   0/10    0.0%   (makalah: 0)
#     mypy       0/10    0.0%   (makalah: 0)
#     Proposed   0/10    0.0%   (makalah: 0)
