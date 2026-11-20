"""
case_SE_T.py
============
Kategori : KESALAHAN TIPE DATA (Type Mismatch)
Kode     : SE-T
Jumlah   : 8 kasus uji
Alat uji : compile(), Run-time execution, Pyflakes, mypy (--check-untyped-defs), Proposed analyzer

Cara menjalankan (satu folder dengan semantic_analyzer.py dan harness.py):
    python case_SE_T.py
"""
from harness import run_category

KODE = "SE-T"

CASES = [
    'total = "angka: " + 5',                  # 1. String + Integer
    'umur: int = "dua puluh"',                # 2. Deklarasi int diisi string
    'berat: float = "lima"',                  # 3. Deklarasi float diisi string
    'status: bool = 100',                     # 4. Deklarasi bool diisi integer
    'angka = 10\nangka()',                    # 5. Memanggil tipe integer sebagai fungsi
    'data: list = 50',                        # 6. Deklarasi list diisi integer
    'nama: str = 123',                        # 7. Deklarasi string diisi integer
    'harga: dict = []'                        # 8. Deklarasi dictionary diisi list
]

# Hasil yang dilaporkan makalah (Tabel 2) sebagai pembanding
PAPER = {'compile()': 0, 'Run-time': 6, 'Pyflakes': 0, 'mypy': 8, 'Proposed': 8}

if __name__ == "__main__":
    run_category("SE-T: KESALAHAN TIPE DATA (Type Mismatch)", KODE, CASES, PAPER)


# ==================================================================================================
# HASIL UJI (dijalankan 27 Okt 2026 | Python 3.12.3, Pyflakes 4.0.3, mypy 2.4.0 --check-untyped-defs)
# ==================================================================================================
# ====================================================================================================
# SE-T: KESALAHAN TIPE DATA (Type Mismatch)   (n = 8)
# ====================================================================================================
#
# Kasus 1:
#     | total = "angka: " + 5
#     compile()  -
#     Run-time   DETECTED  TypeError: can only concatenate str (not "int") to str
#     Pyflakes   -
#     mypy       DETECTED  Unsupported operand types for + ("str" and "int")  [operator]
#     Proposed   DETECTED  [SE-T] unsupported operand types for +: 'str' and 'int'
#
# Kasus 2:
#     | umur: int = "dua puluh"
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       DETECTED  Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
#     Proposed   DETECTED  [SE-T] cannot assign str to 'umur' declared as int
#
# Kasus 3:
#     | berat: float = "lima"
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       DETECTED  Incompatible types in assignment (expression has type "str", variable has type "float")  [assignment]
#     Proposed   DETECTED  [SE-T] cannot assign str to 'berat' declared as float
#
# Kasus 4:
#     | status: bool = 100
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       DETECTED  Incompatible types in assignment (expression has type "int", variable has type "bool")  [assignment]
#     Proposed   DETECTED  [SE-T] cannot assign int to 'status' declared as bool
#
# Kasus 5:
#     | angka = 10
#     | angka()
#     compile()  -
#     Run-time   DETECTED  TypeError: 'int' object is not callable
#     Pyflakes   -
#     mypy       DETECTED  "int" not callable  [operator]
#     Proposed   DETECTED  [SE-T] 'angka' of type 'int' is not callable
#
# Kasus 6:
#     | data: list = 50
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       DETECTED  Incompatible types in assignment (expression has type "int", variable has type "list[Any]")  [assignment]
#     Proposed   DETECTED  [SE-T] cannot assign int to 'data' declared as list
#
# Kasus 7:
#     | nama: str = 123
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       DETECTED  Incompatible types in assignment (expression has type "int", variable has type "str")  [assignment]
#     Proposed   DETECTED  [SE-T] cannot assign int to 'nama' declared as str
#
# Kasus 8:
#     | harga: dict = []
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       DETECTED  Incompatible types in assignment (expression has type "list[Never]", variable has type "dict[Any, Any]")  [ass
#     Proposed   DETECTED  [SE-T] cannot assign list to 'harga' declared as dict
#
# ----------------------------------------------------------------------------------------------------
# RINGKASAN (Terdeteksi per alat):
#     compile()  0/8    0.0%   (makalah: 0)
#     Run-time   2/8   25.0%   (makalah: 6)
#     Pyflakes   0/8    0.0%   (makalah: 0)
#     mypy       8/8  100.0%   (makalah: 8)
#     Proposed   8/8  100.0%   (makalah: 8)
#     Klasifikasi kelas tepat oleh Proposed: 8/8
