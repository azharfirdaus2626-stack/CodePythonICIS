"""
case_SE_F.py
============
Kategori : ATURAN FUNGSI (Function Rules)
Kode     : SE-F
Jumlah   : 7 kasus uji
Alat uji : compile(), Run-time execution, Pyflakes, mypy (--check-untyped-defs), Proposed analyzer

Cara menjalankan (satu folder dengan semantic_analyzer.py dan harness.py):
    python case_SE_F.py
"""
from harness import run_category

KODE = "SE-F"

CASES = [
    'def luas(p, l): pass\nluas(10)',                       # 1. Kekurangan argumen
    'def luas(p, l): pass\nluas(10, 5, 2)',                 # 2. Kelebihan argumen
    'def sapa(nama): pass\nsapa(name="Budi")',              # 3. Salah nama keyword
    'def tambah(a: int): pass\ntambah("satu")',             # 4. Salah tipe argumen (str bukan int)
    'return 100',                                           # 5. Return berada di luar fungsi
    'def get_id() -> int: return "ID-01"',                  # 6. Tipe return salah (str bukan int)
    'def set_data(id, val): pass\nset_data(1)'              # 7. Kurang argumen kedua
]

# Hasil yang dilaporkan makalah (Tabel 2) sebagai pembanding
PAPER = {'compile()': 1, 'Run-time': 6, 'Pyflakes': 1, 'mypy': 7, 'Proposed': 7}

if __name__ == "__main__":
    run_category("SE-F: ATURAN FUNGSI (Function Rules)", KODE, CASES, PAPER)


# ==================================================================================================
# HASIL UJI (dijalankan 27 Okt 2026 | Python 3.12.3, Pyflakes 4.0.3, mypy 2.4.0 --check-untyped-defs)
# ==================================================================================================
# ====================================================================================================
# SE-F: ATURAN FUNGSI (Function Rules)   (n = 7)
# ====================================================================================================
#
# Kasus 1:
#     | def luas(p, l): pass
#     | luas(10)
#     compile()  -
#     Run-time   DETECTED  TypeError: luas() missing 1 required positional argument: 'l'
#     Pyflakes   -
#     mypy       DETECTED  Missing positional argument "l" in call to "luas"  [call-arg]
#     Proposed   DETECTED  [SE-F] 'luas' missing required argument(s): l
#
# Kasus 2:
#     | def luas(p, l): pass
#     | luas(10, 5, 2)
#     compile()  -
#     Run-time   DETECTED  TypeError: luas() takes 2 positional arguments but 3 were given
#     Pyflakes   -
#     mypy       DETECTED  Too many arguments for "luas"  [call-arg]
#     Proposed   DETECTED  [SE-F] 'luas' takes 2 positional argument(s) but 3 were given
#
# Kasus 3:
#     | def sapa(nama): pass
#     | sapa(name="Budi")
#     compile()  -
#     Run-time   DETECTED  TypeError: sapa() got an unexpected keyword argument 'name'
#     Pyflakes   -
#     mypy       DETECTED  Unexpected keyword argument "name" for "sapa"  [call-arg]
#     Proposed   DETECTED  [SE-F] 'sapa' got an unexpected keyword argument 'name'; [SE-F] 'sapa' missing required argument(s): nama
#
# Kasus 4:
#     | def tambah(a: int): pass
#     | tambah("satu")
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       DETECTED  Argument 1 to "tambah" has incompatible type "str"; expected "int"  [arg-type]
#     Proposed   DETECTED  [SE-F] 'tambah' argument 'a' expects int, got str
#
# Kasus 5:
#     | return 100
#     compile()  DETECTED  SyntaxError: 'return' outside function
#     Run-time   DETECTED  SyntaxError: 'return' outside function
#     Pyflakes   DETECTED  'return' outside function
#     mypy       DETECTED  "return" outside function  [misc]
#     Proposed   DETECTED  [SE-F] 'return' outside function
#
# Kasus 6:
#     | def get_id() -> int: return "ID-01"
#     compile()  -
#     Run-time   -
#     Pyflakes   -
#     mypy       DETECTED  Incompatible return value type (got "str", expected "int")  [return-value]
#     Proposed   DETECTED  [SE-F] return value of type str does not match declared return type int
#
# Kasus 7:
#     | def set_data(id, val): pass
#     | set_data(1)
#     compile()  -
#     Run-time   DETECTED  TypeError: set_data() missing 1 required positional argument: 'val'
#     Pyflakes   -
#     mypy       DETECTED  Missing positional argument "val" in call to "set_data"  [call-arg]
#     Proposed   DETECTED  [SE-F] 'set_data' missing required argument(s): val
#
# ----------------------------------------------------------------------------------------------------
# RINGKASAN (Terdeteksi per alat):
#     compile()  1/7   14.3%   (makalah: 1)
#     Run-time   5/7   71.4%   (makalah: 6)
#     Pyflakes   1/7   14.3%   (makalah: 1)
#     mypy       7/7  100.0%   (makalah: 7)
#     Proposed   7/7  100.0%   (makalah: 7)
#     Klasifikasi kelas tepat oleh Proposed: 7/7
