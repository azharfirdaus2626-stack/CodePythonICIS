"""run_all.py - menjalankan ketujuh kategori sekaligus."""
import case_SE_T, case_SE_D, case_SE_R, case_SE_S, case_SE_F, case_VALID  # noqa
import runpy
from harness import run_category

for m in (case_SE_T, case_SE_D, case_SE_R, case_SE_S, case_SE_F):
    run_category(f"{m.KODE}", m.KODE, m.CASES, m.PAPER)
run_category("VALID", "VALID", case_VALID.CASES, case_VALID.PAPER, valid=True)
runpy.run_module("case_LIMITATION", run_name="__main__")
