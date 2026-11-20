"""
case_LIMITATION.py
==================
Kategori : KASUS BATAS (Limitation Cases)
Kode     : LIMITATION
Jumlah   : 4 kasus uji
Alat uji : compile(), Run-time execution, Pyflakes, mypy (--check-untyped-defs), Proposed analyzer

Cara menjalankan (satu folder dengan semantic_analyzer.py dan harness.py):
    python case_LIMITATION.py
"""
from harness import TOOLS, evaluate, mark

KODE = "LIMITATION"

CASES = [
    'def f(a): pass\ng = f\ng(1, 2)',                              # L01: Aliased call
    'def label(): return "T"\nprint(label() + 1)',                 # L02: Unannotated return
    'teks = "halo"\nteks.method_ngarang()',                        # L03: Nonexistent method
    'globals()["w"] = 1\nprint(w)'                                 # L04: Dynamic globals
]

# Kelas galat yang seharusnya terdeteksi (None = program valid saat dijalankan -> setiap laporan = false positive)
EXPECTED = ["SE-F", "SE-T", "SE-T", None]
LABEL = ["L01 Aliased call", "L02 Unannotated return", "L03 Nonexistent method", "L04 Dynamic globals"]

# Tabel 3 makalah: hasil per alat ("Missed", "Detected", "False positive")
PAPER = {
    "L01": {"Proposed": "Missed", "Pyflakes": "Missed",         "mypy": "Detected"},
    "L02": {"Proposed": "Missed", "Pyflakes": "Missed",         "mypy": "Missed"},
    "L03": {"Proposed": "Missed", "Pyflakes": "Missed",         "mypy": "Detected"},
    "L04": {"Proposed": "False positive", "Pyflakes": "False positive", "mypy": "False positive"},
}


def verdict(flag, expected):
    if expected is None:
        return "False positive" if flag else "OK (no report)"
    return "Detected" if flag else "Missed"


if __name__ == "__main__":
    print("=" * 100)
    print("LIMITATION: KASUS BATAS (Limitation Cases)   (n = 4)")
    print("=" * 100)
    for i, (src, exp, lab) in enumerate(zip(CASES, EXPECTED, LABEL), 1):
        r = evaluate(src, exp)
        print(f"\n{lab}   (diharapkan: {exp or 'tidak ada - valid saat run-time'})")
        for line in src.splitlines():
            print(f"    | {line}")
        for t in TOOLS:
            flag, msg = r[t]
            print(f"    {t:<10} {mark(flag):<9} {msg[:110]}")
        key = f"L0{i}"
        print("    Verdict   " + " | ".join(
            f"{t}: {verdict(r[t][0], exp)} (makalah: {PAPER[key][t]})" for t in ("Proposed", "Pyflakes", "mypy")))


# ==================================================================================================
# HASIL UJI (dijalankan 27 Okt 2026 | Python 3.12.3, Pyflakes 4.0.3, mypy 2.4.0 --check-untyped-defs)
# ==================================================================================================
# ====================================================================================================
# LIMITATION: KASUS BATAS (Limitation Cases)   (n = 4)
# ====================================================================================================
#
# L01 Aliased call   (diharapkan: SE-F)
#     | def f(a): pass
#     | g = f
#     | g(1, 2)
#     compile()  -
#     Run-time   DETECTED  TypeError: f() takes 1 positional argument but 2 were given
#     Pyflakes   -
#     mypy       DETECTED  Too many arguments  [call-arg]
#     Proposed   -
#     Verdict   Proposed: Missed (makalah: Missed) | Pyflakes: Missed (makalah: Missed) | mypy: Detected (makalah: Detected)
#
# L02 Unannotated return   (diharapkan: SE-T)
#     | def label(): return "T"
#     | print(label() + 1)
#     compile()  -
#     Run-time   DETECTED  TypeError: can only concatenate str (not "int") to str
#     Pyflakes   -
#     mypy       -
#     Proposed   -
#     Verdict   Proposed: Missed (makalah: Missed) | Pyflakes: Missed (makalah: Missed) | mypy: Missed (makalah: Missed)
#
# L03 Nonexistent method   (diharapkan: SE-T)
#     | teks = "halo"
#     | teks.method_ngarang()
#     compile()  -
#     Run-time   DETECTED  AttributeError: 'str' object has no attribute 'method_ngarang'
#     Pyflakes   -
#     mypy       DETECTED  "str" has no attribute "method_ngarang"  [attr-defined]
#     Proposed   -
#     Verdict   Proposed: Missed (makalah: Missed) | Pyflakes: Missed (makalah: Missed) | mypy: Detected (makalah: Detected)
#
# L04 Dynamic globals   (diharapkan: tidak ada - valid saat run-time)
#     | globals()["w"] = 1
#     | print(w)
#     compile()  -
#     Run-time   -
#     Pyflakes   DETECTED  undefined name 'w'
#     mypy       DETECTED  Name "w" is not defined  [name-defined]
#     Proposed   DETECTED  [SE-D] name 'w' is not declared
#     Verdict   Proposed: False positive (makalah: False positive) | Pyflakes: False positive (makalah: False positive) | mypy: False positive (makalah: False positive)
