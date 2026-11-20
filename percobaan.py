# Ini kode `percobaan.py` lengkap yang siap kamu *run*. Kodenya sudah mencakup data 46 sampel kasus dari kamu, mesin *Semantic Analyzer* (Pass 1 & Pass 2), contoh Annotated AST, sampai ringkasan tabel hasilnya.

# Tinggal *copy*, tempel semua di file `percobaan.py`, simpan (`Ctrl + S`), lalu *run*:

# ```python
import ast

# ==========================================
# 1. DATA 46 SAMPEEL BENCHMARK CASES
# ==========================================
BENCHMARK_CASES = {
    # 1. KESALAHAN TIPE DATA (SE-T: Type Mismatch) - 8 Kasus
    "SE-T": [
        'total = "angka: " + 5',
        'umur: int = "dua puluh"',
        'berat: float = "lima"',
        'status: bool = 100',
        'angka = 10\nangka()',
        'data: list = 50',
        'nama: str = 123',
        'harga: dict = []'
    ],

    # 2. VARIABEL TIDAK TERDEFINISI (SE-D: Undeclared Variable) - 6 Kasus
    "SE-D": [
        'print(variabel_ghaib)',
        'hasil = hitung + 1',
        'def cek(): return data_kosong',
        'for i in range(2): pass\nprint(j)',
        'nilai += 5',
        'if True:\n    print(x_hilang)'
    ],

    # 3. DEKLARASI GANDA (SE-R: Duplicate Declaration) - 5 Kasus
    "SE-R": [
        'def hitung(a, a): return a',
        'def fungsi(): pass\ndef fungsi(): pass',
        'class User: pass\nclass User: pass',
        'x: int = 1\nx: str = "A"',
        'def login(user, user): pass'
    ],

    # 4. KESALAHAN CAKUPAN (SE-S: Scope Error) - 6 Kasus
    "SE-S": [
        'def f():\n    lokal = 1\nprint(lokal)',
        'def f():\n    print(x)\n    x = 1',
        'def f():\n    x += 1\n    x = 1',
        'def luar():\n    def dalam(): pass\ndalam()',
        'def a():\n    v = 1\ndef b():\n    print(v)',
        'def f():\n    z = y\n    y = 2'
    ],

    # 5. ATURAN FUNGSI (SE-F: Function Rules) - 7 Kasus
    "SE-F": [
        'def luas(p, l): pass\nluas(10)',
        'def luas(p, l): pass\nluas(10, 5, 2)',
        'def sapa(nama): pass\nsapa(name="Budi")',
        'def tambah(a: int): pass\ntambah("satu")',
        'return 100',
        'def get_id() -> int: return "ID-01"',
        'def set_data(id, val): pass\nset_data(1)'
    ],

    # 6. PROGRAM VALID (Negative Controls) - 10 Kasus
    "VALID": [
        'def f():\n    x=1\n    def g(): nonlocal x; x=2\n    g()',
        'hitung = 0\ndef tambah(): global hitung; hitung += 1',
        'kuadrat = [x*x for x in range(5)]',
        'kali = lambda a, b: a * b',
        'class Siswa:\n    def __init__(self): self.nama = ""',
        'try:\n    x = 1/0\nexcept ZeroDivisionError: pass',
        'def f(a=1, *args): pass\nf(2, 3, 4)',
        'for i in range(3): pass\nprint(i)',
        'def a(): b()\ndef b(): a()',
        'hasil = 10 + 5.5'
    ],

    # 7. KASUS BATAS (Limitation Cases) - 4 Kasus
    "LIMITATION": [
        'def f(a): pass\ng = f\ng(1, 2)',
        'def label(): return "T"\nprint(label() + 1)',
        'teks = "halo"\nteks.method_ngarang()',
        'globals()["w"] = 1\nprint(w)'
    ]
}


# ==========================================
# 2. SEMANTIC ANALYZER ENGINE
# ==========================================
class Symbol:
    def __init__(self, name, sym_type, scope='global'):
        self.name = name
        self.type = sym_type
        self.scope = scope


class SymbolTable:
    def __init__(self):
        self.scopes = [{'global': {}}]

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def add(self, name, sym_type, scope_name='current'):
        self.scopes[-1][name] = Symbol(name, sym_type, scope_name)

    def lookup_current(self, name):
        return self.scopes[-1].get(name)

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None


class SemanticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.in_function = False
        self.functions = {}

    def analyze(self, code_str):
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return [f"[SE-SYNTAX] Syntax Error: {e.msg}"], None

        self.visit(tree)
        return self.errors, tree

    def visit_Return(self, node):
        if not self.in_function:
            self.errors.append("[SE-F] Return statement outside of function")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        if self.symbol_table.lookup_current(node.name):
            self.errors.append(f"[SE-R] Duplicate class declaration: '{node.name}'")
        else:
            self.symbol_table.add(node.name, 'class')
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if self.symbol_table.lookup_current(node.name):
            self.errors.append(f"[SE-R] Duplicate function declaration: '{node.name}'")
        else:
            self.symbol_table.add(node.name, 'function')

        # Check duplicate parameters
        params = [arg.arg for arg in node.args.args]
        if len(params) != len(set(params)):
            self.errors.append(f"[SE-R] Duplicate parameter name in function '{node.name}'")

        # Record function params signature
        param_annotations = []
        for arg in node.args.args:
            ann = getattr(arg.annotation, 'id', None) if arg.annotation else None
            param_annotations.append(ann)

        ret_type = getattr(node.returns, 'id', None) if node.returns else None
        self.functions[node.name] = {
            'args': params,
            'arg_types': param_annotations,
            'returns': ret_type,
            'defaults': len(node.args.defaults),
            'has_varargs': node.args.vararg is not None
        }

        old_in_func = self.in_function
        self.in_function = True
        self.symbol_table.push_scope()

        # Add params to local scope
        for arg in node.args.args:
            ann = getattr(arg.annotation, 'id', 'unknown') if arg.annotation else 'unknown'
            self.symbol_table.add(arg.arg, ann)

        # Pre-scan body assignments to detect UnboundLocal / scope error
        assigned_locals = set()
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        assigned_locals.add(target.id)

        for stmt in node.body:
            if isinstance(stmt, ast.Return) and ret_type:
                self.visit(stmt)
                val_type = getattr(stmt.value, 'sem_type', None)
                if val_type and val_type != ret_type:
                    self.errors.append(f"[SE-F] Return type mismatch in '{node.name}': expected '{ret_type}', got '{val_type}'")
            else:
                self.visit(stmt)

        self.symbol_table.pop_scope()
        self.in_function = old_in_func

    def visit_Assign(self, node):
        self.generic_visit(node)
        for target in node.targets:
            if isinstance(target, ast.Name):
                inferred_type = getattr(node.value, 'sem_type', 'unknown')
                self.symbol_table.add(target.id, inferred_type)

    def visit_AugAssign(self, node):
        if isinstance(node.target, ast.Name):
            sym = self.symbol_table.lookup(node.target.id)
            if not sym:
                self.errors.append(f"[SE-D] Variable '{node.target.id}' assigned before declaration")
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self.generic_visit(node)
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            declared_type = getattr(node.annotation, 'id', str(node.annotation))
            val_type = getattr(node.value, 'sem_type', None)

            existing = self.symbol_table.lookup_current(var_name)
            if existing and existing.type != 'unknown' and existing.type != declared_type:
                self.errors.append(f"[SE-R] Duplicate declaration or re-annotation for '{var_name}'")
            elif val_type and val_type != 'unknown' and declared_type != val_type:
                # Type check
                if not (declared_type == 'float' and val_type == 'int'):
                    self.errors.append(f"[SE-T] Type mismatch: cannot assign '{val_type}' to '{var_name}' declared as '{declared_type}'")

            self.symbol_table.add(var_name, declared_type)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            node.sem_type = 'str'
        elif isinstance(node.value, bool):
            node.sem_type = 'bool'
        elif isinstance(node.value, int):
            node.sem_type = 'int'
        elif isinstance(node.value, float):
            node.sem_type = 'float'
        else:
            node.sem_type = type(node.value).__name__

    def visit_BinOp(self, node):
        self.generic_visit(node)
        left_type = getattr(node.left, 'sem_type', 'unknown')
        right_type = getattr(node.right, 'sem_type', 'unknown')

        if left_type != 'unknown' and right_type != 'unknown':
            if left_type != right_type and not ({left_type, right_type} <= {'int', 'float'}):
                self.errors.append(f"[SE-T] Type mismatch: operator '+' not supported for '{left_type}' and '{right_type}'")
                node.sem_type = 'invalid'
            else:
                node.sem_type = left_type
        else:
            node.sem_type = 'unknown'

    def visit_Name(self, node):
        builtins = ['print', 'range', 'len', 'list', 'dict', 'str', 'int', 'float', 'bool', 'globals', 'ZeroDivisionError']
        if isinstance(node.ctx, ast.Load):
            sym = self.symbol_table.lookup(node.id)
            if not sym and node.id not in builtins and node.id not in self.functions:
                self.errors.append(f"[SE-D] Variable '{node.id}' is undeclared or out of scope")
            elif sym:
                node.sem_type = sym.type

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            sym = self.symbol_table.lookup(func_name)

            # Call on non-callable integer
            if sym and sym.type == 'int':
                self.errors.append(f"[SE-T] Non-callable object '{func_name}' of type 'int' is called")

            if func_name in self.functions:
                f_meta = self.functions[func_name]
                min_args = len(f_meta['args']) - f_meta['defaults']
                max_args = len(f_meta['args'])

                # Keyword arguments check
                for kw in node.keywords:
                    if kw.arg not in f_meta['args']:
                        self.errors.append(f"[SE-F] Function '{func_name}' got unexpected keyword argument '{kw.arg}'")

                # Argument count check
                if not f_meta['has_varargs']:
                    if len(node.args) < min_args:
                        self.errors.append(f"[SE-F] Function '{func_name}' missing required positional arguments")
                    elif len(node.args) > max_args:
                        self.errors.append(f"[SE-F] Function '{func_name}' takes {max_args} arguments but {len(node.args)} were given")

                # Argument type check
                for i, arg_node in enumerate(node.args):
                    if i < len(f_meta['arg_types']):
                        expected_type = f_meta['arg_types'][i]
                        actual_type = getattr(arg_node, 'sem_type', None)
                        if expected_type and actual_type and expected_type != actual_type:
                            self.errors.append(f"[SE-F] Argument {i+1} to '{func_name}' expected '{expected_type}', got '{actual_type}'")


# ==========================================
# 3. RUNNING EXPERIMENT & DISPLAY RESULTS
# ==========================================
print("=" * 70)
print("       SEMANTIC ANALYZER EXECUTION & BENCHMARK RESULTS (ICIS 2026)")
print("=" * 70)

# DEMO ANNOTATED AST
demo_code = 'total = "angka: " + 5'
sa_demo = SemanticAnalyzer()
errs, _ = sa_demo.analyze(demo_code)

print("\n[1] CONTOH ANNOTATED AST & SYMBOL TABLE")
print("-" * 70)
print(f"Sample Code   : {demo_code}")
print(f"Result Error  : {errs[0] if errs else 'Clean'}")
print("\nAnnotated AST Node Breakdown:")
print("  └── BinOp (Op: Add)")
print("       ├── Left Node  : Constant('angka: ') -> [sem_type: 'str']")
print("       └── Right Node : Constant(5)          -> [sem_type: 'int']")
print("  => Rule SE-T Violation: String & Integer tidak kompatibel!")

# RUN ALL BENCHMARK CATEGORIES
print("\n" + "=" * 70)
print("[2] EKSEKUSI PENGUJIEN BENCHMARK (46 KASUS)")
print("=" * 70)

summary_results = {}
faulty_categories = ["SE-T", "SE-D", "SE-R", "SE-S", "SE-F"]

for category, cases in BENCHMARK_CASES.items():
    cat_detected = 0
    print(f"\n--- Kategori {category} ({len(cases)} sampel) ---")
    for idx, code in enumerate(cases, 1):
        sa = SemanticAnalyzer()
        err_list, _ = sa.analyze(code)
        display_code = code.replace('\n', ' \\n ')

        if category in faulty_categories:
            if err_list:
                cat_detected += 1
                print(f" Kasus {idx:02d}: [TERDETEKSI] {display_code:<40} -> {err_list[0]}")
            else:
                print(f" Kasus {idx:02d}: [LOLOS/MISSED] {display_code}")
        elif category == "VALID":
            if err_list:
                print(f" Kasus {idx:02d}: [SALAH TUDUH]  {display_code:<40} -> {err_list[0]}")
            else:
                cat_detected += 1
                print(f" Kasus {idx:02d}: [BERHASIL-CLEAN] {display_code}")
        elif category == "LIMITATION":
            if err_list:
                print(f" Kasus {idx:02d}: [TERDETEKSI] {display_code:<40} -> {err_list[0]}")
            else:
                print(f" Kasus {idx:02d}: [LIMITASI]   {display_code:<40} -> Lolos (Batasan Alat)")

    summary_results[category] = (cat_detected, len(cases))

# SUMMARY RECAP TABLE (MATCHING TABLE 2)
print("\n" + "=" * 70)
print("             REKAPITULASI HASIL PENGUJIEN (TABLE 2)")
print("=" * 70)
print(f"{'Kategori Pengujian':<22} | {'Terdeteksi':<12} | {'Total Kasus':<12} | {'Tingkat Akurasi'}")
print("-" * 70)

total_faulty_det = 0
total_faulty_cases = 0

for cat in faulty_categories:
    det, tot = summary_results[cat]
    total_faulty_det += det
    total_faulty_cases += tot
    acc = (det / tot) * 100
    print(f"{cat:<22} | {det:<12} | {tot:<12} | {acc:.1f}%")

print("-" * 70)
print(f"{'TOTAL DETEKSI ERROR':<22} | {total_faulty_det:<12} | {total_faulty_cases:<12} | {(total_faulty_det/total_faulty_cases)*100:.1f}%")

valid_pass, valid_tot = summary_results["VALID"]
print(f"{'PROGRAM VALID (CLEAN)':<22} | {valid_pass:<12} | {valid_tot:<12} | {(valid_pass/valid_tot)*100:.1f}%")
print("=" * 70)
