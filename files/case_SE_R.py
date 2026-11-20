"""
case_SE_R.py
============
Kategori : DEKLARASI GANDA (Duplicate Declaration)
Kode     : SE-R
Jumlah   : 5 kasus uji
Alat uji : compile(), Run-time execution, Pyflakes, mypy (--check-untyped-defs), Proposed analyzer

Cara menjalankan (satu folder dengan semantic_analyzer.py dan harness.py):
    python case_SE_R.py
"""
from harness import run_category

KODE = "SE-R"

CASES = [
    'def hitung(a, a): return a',             # 1. Nama parameter sama
    'def fungsi(): pass\ndef fungsi(): pass', # 2. Deklarasi fungsi 2 kali di lingkup sama
    'class User: pass\nclass User: pass',     # 3. Deklarasi class 2 kali
    'x: int = 1\nx: str = "A"',               # 4. Anotasi ganda pada variabel yang sama
    'def login(user, user): pass'             # 5. Parameter duplikat di fungsi lain
]

# Hasil yang dilaporkan makalah (Tabel 2) sebagai pembanding
PAPER = {'compile()': 1, 'Run-time': 1, 'Pyflakes': 4, 'mypy': 5, 'Proposed': 5}

if __name__ == "__main__":
    run_category("SE-R: DEKLARASI GANDA (Duplicate Declaration)", KODE, CASES, PAPER)


# ==================================================================================================
# HASIL UJI (dijalankan 27 Okt 2026 | Python 3.12.3, Pyflakes 4.0.3, mypy 2.4.0 --check-untyped-defs)
# ==================================================================================================
# ====================================================================================================
# SE-R: DEKLARASI GANDA (Duplicate Declaration)   (n = 5)
# ====================================================================================================
#
# Kasus 1:
#     | def hitung(a, a): return a
#     compile()  DETECTED  SyntaxError: duplicate argument 'a' in function definition
#     Run-time   DETECTED  SyntaxError: duplicate argument 'a' in function definition
#     Pyflakes   DETECTED  duplicate argument 'a' in function definition
#     mypy       DETECTED  Duplicate parameter "a" in function definition  [syntax]
#     Proposed   DETECTED  [SE-R] duplicate parameter name 'a'
#
# Kasus 2:
#     | def fungsi(): pass
#     | def fungsi(): pass
#     compile()  -
#     Run-time   -
#     Pyflakes   DETECTED  redefinition of unused 'fungsi' from line 1
#     mypy       DETECTED  Name "fungsi" already defined on line 1  [no-redef]
#     Proposed   DETECTED  [SE-R] function 'fungsi' is already declared in '<module>'
#
# Kasus 3:
#     | class User: pass
#     | class User: pass
#     compile()  -
#     Run-time   -
#     Pyflakes   DETECTED  redefinition of unused 'User' from line 1
#     mypy       DETECTED  Name "User" already defined on line 1  [no-redef]
#     Proposed   DETECTED  [SE-R] class 'User' is already declared in '<module>'
#
# Kasus 4:
#     | x: int = 1
#     | x: str = "A"
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       DETECTED  Name "x" already defined on line 1  [no-redef]
#     Proposed   DETECTED  [SE-R] 'x' re-declared as str; previously declared as int
#
# Kasus 5:
#     | def login(user, user): pass
#     compile()  DETECTED  SyntaxError: duplicate argument 'user' in function definition
#     Run-time   DETECTED  SyntaxError: duplicate argument 'user' in function definition
#     Pyflakes   DETECTED  duplicate argument 'user' in function definition
#     mypy       DETECTED  Duplicate parameter "user" in function definition  [syntax]
#     Proposed   DETECTED  [SE-R] duplicate parameter name 'user'
#
# ----------------------------------------------------------------------------------------------------
# RINGKASAN (Terdeteksi per alat):
#     compile()  2/5   40.0%   (makalah: 1)
#     Run-time   2/5   40.0%   (makalah: 1)
#     Pyflakes   4/5   80.0%   (makalah: 4)
#     mypy       5/5  100.0%   (makalah: 5)
#     Proposed   5/5  100.0%   (makalah: 5)
#     Klasifikasi kelas tepat oleh Proposed: 5/5
