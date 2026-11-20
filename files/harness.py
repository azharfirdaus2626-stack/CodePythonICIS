"""
harness.py - menjalankan satu program uji pada 5 "alat" seperti di Tabel 2 makalah:
  compile()  | Run-time execution | Pyflakes | mypy --check-untyped-defs | Proposed analyzer

Kriteria "detected" (Bab 3.2): alat melaporkan >= 1 diagnostik
(run-time: eksekusi memunculkan exception atau SyntaxError).
Untuk proposed analyzer, klasifikasi dianggap tepat bila kode kelas == kelas yang disuntikkan.
"""
import subprocess
import sys

from semantic_analyzer import analyze

TOOLS = ["compile()", "Run-time", "Pyflakes", "mypy", "Proposed"]


def run_compile(src):
    try:
        compile(src, "<case>", "exec")
        return False, ""
    except (SyntaxError, ValueError) as e:
        return True, f"{type(e).__name__}: {getattr(e, 'msg', e)}"


def run_runtime(src):
    code = ("import sys\nexec(compile(sys.stdin.read(), '<case>', 'exec'), {'__name__': '__main__'})")
    p = subprocess.run([sys.executable, "-c", code], input=src, capture_output=True, text=True, timeout=20)
    if p.returncode != 0:
        last = p.stderr.strip().splitlines()[-1] if p.stderr.strip() else "error"
        return True, last
    return False, ""


def run_pyflakes(src):
    from pyflakes import api, reporter

    class Collect:
        def __init__(self): self.msgs = []
        def unexpectedError(self, fn, msg): self.msgs.append(str(msg))
        def syntaxError(self, fn, msg, ln, col, text): self.msgs.append(f"SyntaxError: {msg}")
        def flake(self, m): self.msgs.append(m.message % m.message_args)

    c = Collect()
    api.check(src, "<case>", c)
    return bool(c.msgs), "; ".join(c.msgs)


def run_mypy(src):
    # subprocess per kasus: menghindari crash mypy (compiled) saat dipanggil berulang dalam satu proses
    p = subprocess.run([sys.executable, "-m", "mypy", "--check-untyped-defs", "--no-incremental",
                        "--no-error-summary", "--cache-dir=/dev/null", "-c", src],
                       capture_output=True, text=True, timeout=120)
    errs = [l.split("error:", 1)[1].strip() for l in p.stdout.splitlines() if "error:" in l]
    return bool(errs), "; ".join(errs)


def run_proposed(src, expected=None):
    ds = analyze(src)
    if not ds:
        return False, ""
    msg = "; ".join(f"[{d.code}] {d.message}" for d in ds)
    return True, msg


def evaluate(src, expected=None):
    """Mengembalikan dict {tool: (detected: bool, message: str)} + 'class_ok' untuk proposed."""
    res = {
        "compile()": run_compile(src),
        "Run-time": run_runtime(src),
        "Pyflakes": run_pyflakes(src),
        "mypy": run_mypy(src),
        "Proposed": run_proposed(src, expected),
    }
    ds = analyze(src)
    res["class_ok"] = bool(expected) and bool(ds) and all(d.code == expected for d in ds)
    return res


def mark(flag):
    return "DETECTED" if flag else "-"


def run_category(title, code, cases, paper_expected, valid=False):
    """Jalankan semua kasus satu kategori dan cetak laporan."""
    print("=" * 100)
    print(f"{title}   (n = {len(cases)})")
    print("=" * 100)
    totals = {t: 0 for t in TOOLS}
    class_ok = 0
    for i, src in enumerate(cases, 1):
        r = evaluate(src, None if valid else code)
        print(f"\nKasus {i}:")
        for line in src.splitlines():
            print(f"    | {line}")
        for t in TOOLS:
            flag, msg = r[t]
            totals[t] += flag
            print(f"    {t:<10} {mark(flag):<9} {msg[:110]}")
        class_ok += r["class_ok"]
    print("\n" + "-" * 100)
    label = "False positive" if valid else "Terdeteksi"
    print(f"RINGKASAN ({label} per alat):")
    for t in TOOLS:
        n = totals[t]
        rate = f"{100 * n / len(cases):.1f}%"
        ref = paper_expected.get(t)
        refs = f"   (makalah: {ref})" if ref is not None else ""
        print(f"    {t:<10} {n}/{len(cases)}  {rate:>6}{refs}")
    if not valid:
        print(f"    Klasifikasi kelas tepat oleh Proposed: {class_ok}/{len(cases)}")
    return totals
