"""
semantic_analyzer.py
====================
Proposed analyzer: Semantic Error Detection Using a Semantic Analyzer in a Python Compiler.

Desain (sesuai Bab 3 makalah):
  * ast.parse            -> analisis leksikal + sintaks
  * Pass 1               -> membangun kerangka symbol table hierarkis (module/class/function/lambda/comprehension)
  * Pass 2               -> traversal sesuai urutan sumber, menempelkan atribut `sem_type` pada tiap node ekspresi
                            dan `sem_symbol` pada tiap node Name  (= Annotated AST)
  * Tipe                 -> int, float, str, bool, list, dict, tuple, set, None, any (gradual)
  * Persamaan (1)        -> compat(td, ta)

Kelas galat:
  SE-T  type mismatch            SE-D  undeclared variable      SE-R  duplicate declaration
  SE-S  scope error              SE-F  function rules
"""
import ast
import builtins
from collections import deque
from dataclasses import dataclass, field

TYPES = {"int", "float", "str", "bool", "list", "dict", "tuple", "set", "None", "any"}
CONCRETE = TYPES - {"any"}
NUMERIC = {"int", "float", "bool"}
SEQ = {"str", "list", "tuple"}
BUILTINS = set(dir(builtins)) | {"__file__", "__name__", "__doc__"}
BUILTIN_CALL_TYPES = {"int": "int", "float": "float", "str": "str", "bool": "bool", "len": "int",
                      "list": "list", "dict": "dict", "set": "set", "tuple": "tuple",
                      "input": "str", "print": "None", "repr": "str", "abs": "any"}


def compat(td: str, ta: str) -> bool:
    """Persamaan (1): apakah nilai bertipe ta boleh dipakai di tempat bertipe td."""
    return (td == ta or "any" in (td, ta)
            or (td, ta) in {("float", "int"), ("float", "bool"), ("int", "bool")})


@dataclass
class Diagnostic:
    line: int
    code: str
    message: str

    def __str__(self):
        return f"line {self.line}: [{self.code}] {self.message}"


@dataclass
class Symbol:
    name: str
    kind: str                      # variable | function | class | param | import
    type: str = "any"
    line: int = 0
    annotated: bool = False
    node: ast.AST = None           # FunctionDef untuk kind == function
    ambiguous: bool = False        # dideklarasi ulang -> tanda tangan tidak dipercaya


class Scope:
    def __init__(self, kind, name, parent=None):
        self.kind, self.name, self.parent = kind, name, parent
        self.bound = set()         # nama yang terikat langsung di scope ini (hasil Pass 1)
        self.declared = set()      # nama yang sudah terikat sampai titik saat ini (Pass 2)
        self.symbols = {}
        self.globals_decl, self.nonlocal_decl = set(), set()
        self.star_import = False
        self.ret_type = None       # tipe return terdeklarasi (fungsi)

    @property
    def is_function_like(self):
        return self.kind in ("function", "lambda", "comp")


# ----------------------------------------------------------------------------------------------
def stored_names(nodes):
    """Nama yang diikat oleh sekumpulan statement tanpa masuk ke scope bersarang (untuk pra-ikat loop)."""
    out = set()

    def walk(n):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            out.add(n.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
            return
        elif isinstance(n, (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            return
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                out.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, ast.ExceptHandler) and n.name:
            out.add(n.name)
        for c in ast.iter_child_nodes(n):
            walk(c)

    for n in nodes:
        walk(n)
    return out


class SemanticAnalyzer:
    def __init__(self):
        self.diags, self.scopes, self.registry = [], {}, {}
        self.module = None
        self.deferred = deque()

    # ------------------------------------------------------------------ util
    def report(self, node, code, msg):
        d = Diagnostic(getattr(node, "lineno", 0), code, msg)
        if all((x.line, x.code, x.message) != (d.line, d.code, d.message) for x in self.diags):
            self.diags.append(d)

    def ann_type(self, a):
        if a is None:
            return "any"
        if isinstance(a, ast.Constant) and a.value is None:
            return "None"
        if isinstance(a, ast.Name):
            return a.id if a.id in TYPES and a.id != "any" else "any"
        if isinstance(a, ast.Subscript):
            return self.ann_type(a.value)
        return "any"

    # ------------------------------------------------------------------ PASS 1
    def build_scope(self, node, kind, name, parent):
        sc = Scope(kind, name, parent)
        self.scopes[node] = sc

        def bind(n):
            sc.bound.add(n)

        if kind in ("function", "lambda"):
            a = node.args
            for p in a.posonlyargs + a.args + a.kwonlyargs + ([a.vararg] if a.vararg else []) + \
                     ([a.kwarg] if a.kwarg else []):
                bind(p.arg)
            body = node.body if kind == "function" else [node.body]
        elif kind == "comp":
            for g in node.generators:
                for n in ast.walk(g.target):
                    if isinstance(n, ast.Name):
                        bind(n.id)
            body = []
        else:
            body = node.body

        def walk(n):
            if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
                bind(n.id)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                bind(n.name)
                self.build_scope(n, "function", n.name, sc)
                return
            elif isinstance(n, ast.ClassDef):
                bind(n.name)
                self.build_scope(n, "class", n.name, sc)
                return
            elif isinstance(n, ast.Lambda):
                self.build_scope(n, "lambda", "<lambda>", sc)
                return
            elif isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                self.build_scope(n, "comp", "<comprehension>", sc)
                return
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for al in n.names:
                    if al.name == "*":
                        sc.star_import = True
                    else:
                        bind((al.asname or al.name).split(".")[0])
            elif isinstance(n, ast.ExceptHandler) and n.name:
                bind(n.name)
            elif isinstance(n, ast.Global):
                sc.globals_decl.update(n.names)
            elif isinstance(n, ast.Nonlocal):
                sc.nonlocal_decl.update(n.names)
            elif isinstance(n, (ast.MatchAs, ast.MatchStar)) and n.name:
                bind(n.name)
            for c in ast.iter_child_nodes(n):
                walk(c)

        for n in body:
            walk(n)
        if kind == "comp":                       # elemen/kondisi comprehension
            for c in ast.iter_child_nodes(node):
                if not isinstance(c, ast.comprehension):
                    walk(c)
            for g in node.generators:
                walk(g.iter)
                for i in g.ifs:
                    walk(i)
        sc.bound -= sc.globals_decl | sc.nonlocal_decl
        return sc

    def pass1(self, tree):
        self.module = self.build_scope(tree, "module", "<module>", None)
        for node, sc in list(self.scopes.items()):
            for g in sc.globals_decl:
                self.module.bound.add(g)
        for sc in self.scopes.values():
            for n in sc.bound:
                self.registry.setdefault(n, []).append(sc)

    # ------------------------------------------------------------------ simbol
    def declare(self, sc, name, kind, typ="any", line=0, annotated=False, node=None):
        if name in sc.globals_decl:
            sc = self.module
        sc.declared.add(name)
        old = sc.symbols.get(name)
        if old is None:
            sc.symbols[name] = Symbol(name, kind, typ, line, annotated, node)
            return sc.symbols[name]
        if kind != old.kind or kind == "function":
            old.ambiguous = True
        if kind == "variable" and old.kind == "variable":
            if not old.annotated:
                old.type = typ if old.type == typ else "any"
        else:
            old.kind, old.type, old.node = kind, "any" if kind == "variable" else typ, node
        old.annotated = old.annotated or annotated
        return old

    # ------------------------------------------------------------------ resolusi nama
    def resolve(self, name, sc):
        """Urutan: lokal -> enclosing -> modul -> built-in. Mengembalikan (scope, Symbol|None) atau status."""
        if name in sc.globals_decl:
            return ("ok", self.module, self.module.symbols.get(name)) if name in self.module.bound else ("none",)
        if name in sc.bound:
            if name in sc.declared:
                return ("ok", sc, sc.symbols.get(name))
            if sc.kind != "class":
                return ("unbound", sc)
        p = sc.parent
        while p:
            if p.kind != "class" and name in p.bound:
                return ("ok", p, p.symbols.get(name))
            p = p.parent
        if name in BUILTINS:
            return ("builtin",)
        q = sc
        while q:
            if q.star_import:
                return ("star",)
            q = q.parent
        return ("none",)

    def load_name(self, node, sc):
        r = self.resolve(node.id, sc)
        if r[0] == "ok":
            sym = r[2]
            node.sem_symbol = sym
            return sym.type if sym and sym.kind in ("variable", "param") else "any"
        if r[0] == "unbound":
            owner = r[1]
            if owner.is_function_like:
                self.report(node, "SE-S", f"local name '{node.id}' is read before it is assigned in '{owner.name}'")
            else:
                self.report(node, "SE-D", f"name '{node.id}' is used before it is declared")
            owner.declared.add(node.id)
            return "any"
        if r[0] == "none":
            others = [s for s in self.registry.get(node.id, []) if s is not sc]
            if others:
                self.report(node, "SE-S",
                            f"'{node.id}' is not visible in '{sc.name}' (declared in '{others[0].name}')")
            else:
                self.report(node, "SE-D", f"name '{node.id}' is not declared")
        return "any"

    # ------------------------------------------------------------------ ekspresi
    def expr(self, n, sc):
        t = self._expr(n, sc)
        n.sem_type = t
        return t

    def _expr(self, n, sc):
        if n is None:
            return "any"
        if isinstance(n, ast.Constant):
            v = n.value
            if isinstance(v, bool): return "bool"
            if isinstance(v, int): return "int"
            if isinstance(v, float): return "float"
            if isinstance(v, str): return "str"
            if v is None: return "None"
            return "any"
        if isinstance(n, ast.Name):
            return self.load_name(n, sc) if isinstance(n.ctx, ast.Load) else "any"
        if isinstance(n, ast.BinOp):
            return self.binop(n, self.expr(n.left, sc), self.expr(n.right, sc))
        if isinstance(n, ast.UnaryOp):
            t = self.expr(n.operand, sc)
            if isinstance(n.op, ast.Not): return "bool"
            return t if t in NUMERIC else "any"
        if isinstance(n, ast.Compare):
            self.expr(n.left, sc)
            for c in n.comparators: self.expr(c, sc)
            return "bool"
        if isinstance(n, ast.BoolOp):
            ts = {self.expr(v, sc) for v in n.values}
            return ts.pop() if len(ts) == 1 else "any"
        if isinstance(n, ast.IfExp):
            self.expr(n.test, sc)
            a, b = self.expr(n.body, sc), self.expr(n.orelse, sc)
            return a if a == b else "any"
        if isinstance(n, ast.Call):
            return self.call(n, sc)
        if isinstance(n, ast.Lambda):
            for d in n.args.defaults + [x for x in n.args.kw_defaults if x]:
                self.expr(d, sc)
            self.check_dup_params(n)
            self.deferred.append((self.scopes[n], n))
            return "any"
        if isinstance(n, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            csc = self.scopes[n]
            for g in n.generators:
                self.expr(g.iter, csc)
                for nm in ast.walk(g.target):
                    if isinstance(nm, ast.Name):
                        self.declare(csc, nm.id, "variable", "any", n.lineno)
                for i in g.ifs: self.expr(i, csc)
            if isinstance(n, ast.DictComp):
                self.expr(n.key, csc); self.expr(n.value, csc)
            else:
                self.expr(n.elt, csc)
            return {ast.ListComp: "list", ast.SetComp: "set", ast.DictComp: "dict"}.get(type(n), "any")
        if isinstance(n, ast.NamedExpr):
            t = self.expr(n.value, sc)
            self.declare(sc, n.target.id, "variable", t, n.lineno)
            return t
        if isinstance(n, (ast.List, ast.Set, ast.Tuple)):
            for e in n.elts: self.expr(e, sc)
            return {ast.List: "list", ast.Set: "set", ast.Tuple: "tuple"}[type(n)]
        if isinstance(n, ast.Dict):
            for e in n.keys + n.values:
                if e is not None: self.expr(e, sc)
            return "dict"
        if isinstance(n, ast.JoinedStr):
            for v in n.values: self.expr(v, sc)
            return "str"
        for c in ast.iter_child_nodes(n):          # Attribute, Subscript, Starred, Await, ...
            if isinstance(c, ast.expr):
                self.expr(c, sc)
        return "any"

    def binop(self, n, l, r):
        if "any" in (l, r):
            return "any"
        op = type(n.op)
        sym = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "//",
               ast.Mod: "%", ast.Pow: "**", ast.BitOr: "|", ast.BitAnd: "&", ast.BitXor: "^",
               ast.LShift: "<<", ast.RShift: ">>", ast.MatMult: "@"}.get(op, "?")
        if l in NUMERIC and r in NUMERIC:
            if op is ast.Div: return "float"
            if op is ast.Pow: return "any"
            return "float" if "float" in (l, r) else "int"
        if op is ast.Add and l == r and l in SEQ: return l
        if op is ast.Mult and ((l in SEQ and r in ("int", "bool")) or (r in SEQ and l in ("int", "bool"))):
            return l if l in SEQ else r
        if op is ast.Mod and l == "str": return "str"
        if l == r == "set" and op in (ast.Sub, ast.BitOr, ast.BitAnd, ast.BitXor): return "set"
        if l == r == "dict" and op is ast.BitOr: return "dict"
        self.report(n, "SE-T", f"unsupported operand types for {sym}: '{l}' and '{r}'")
        return "any"

    # ------------------------------------------------------------------ pemanggilan
    def call(self, n, sc):
        arg_types = [self.expr(a.value if isinstance(a, ast.Starred) else a, sc) for a in n.args]
        kw_types = {k.arg: self.expr(k.value, sc) for k in n.keywords}
        if not isinstance(n.func, ast.Name):
            self.expr(n.func, sc)
            return "any"
        r = self.resolve(n.func.id, sc)
        if r[0] == "builtin":
            return BUILTIN_CALL_TYPES.get(n.func.id, "any")
        n.func.sem_type = "any"
        if r[0] != "ok":
            self.load_name(n.func, sc)
            return "any"
        sym = r[2]
        n.func.sem_symbol = sym
        if sym is None:
            return "any"
        if sym.kind in ("variable", "param") and sym.type in CONCRETE:
            self.report(n, "SE-T", f"'{sym.name}' of type '{sym.type}' is not callable")
            return "any"
        if sym.kind != "function" or sym.ambiguous:
            return "any"
        fn = sym.node
        ret = self.ann_type(fn.returns)
        if any(isinstance(a, ast.Starred) for a in n.args) or any(k.arg is None for k in n.keywords):
            return ret
        self.check_signature(n, sym.name, fn, arg_types, kw_types)
        return ret

    def check_signature(self, n, fname, fn, arg_types, kw_types):
        a = fn.args
        positional = [p.arg for p in a.posonlyargs + a.args]
        posonly = {p.arg for p in a.posonlyargs}
        kwonly = [p.arg for p in a.kwonlyargs]
        ann = {p.arg: self.ann_type(p.annotation) for p in a.posonlyargs + a.args + a.kwonlyargs}
        n_def = len(a.defaults)
        required = set(positional[:len(positional) - n_def])
        required |= {p.arg for p, d in zip(a.kwonlyargs, a.kw_defaults) if d is None}
        if len(arg_types) > len(positional) and not a.vararg:
            self.report(n, "SE-F", f"'{fname}' takes {len(positional)} positional argument(s) "
                                   f"but {len(arg_types)} were given")
        filled = set(positional[:len(arg_types)])
        for i, t in enumerate(arg_types[:len(positional)]):
            if not compat(ann[positional[i]], t):
                self.report(n, "SE-F", f"'{fname}' argument '{positional[i]}' expects "
                                       f"{ann[positional[i]]}, got {t}")
        for k, t in kw_types.items():
            if (k in positional and k not in posonly) or k in kwonly:
                if k in filled:
                    self.report(n, "SE-F", f"'{fname}' got multiple values for argument '{k}'")
                filled.add(k)
                if not compat(ann[k], t):
                    self.report(n, "SE-F", f"'{fname}' argument '{k}' expects {ann[k]}, got {t}")
            elif not a.kwarg:
                self.report(n, "SE-F", f"'{fname}' got an unexpected keyword argument '{k}'")
        missing = [m for m in positional + kwonly if m in required and m not in filled]
        if missing:
            self.report(n, "SE-F", f"'{fname}' missing required argument(s): {', '.join(missing)}")

    # ------------------------------------------------------------------ statement
    def check_dup_params(self, fn):
        a = fn.args
        seen = set()
        for p in a.posonlyargs + a.args + a.kwonlyargs + ([a.vararg] if a.vararg else []) + \
                 ([a.kwarg] if a.kwarg else []):
            if p.arg in seen:
                self.report(fn, "SE-R", f"duplicate parameter name '{p.arg}'")
            seen.add(p.arg)

    def assign_name(self, target, vtype, sc, node):
        r_sc = self.module if target.id in sc.globals_decl else sc
        sym = r_sc.symbols.get(target.id)
        if sym is not None and sym.annotated and sym.kind in ("variable", "param"):
            if not compat(sym.type, vtype):
                self.report(node, "SE-T", f"cannot assign {vtype} to '{target.id}' declared as {sym.type}")
            r_sc.declared.add(target.id)
        else:
            sym = self.declare(sc, target.id, "variable", vtype, node.lineno)
        target.sem_symbol, target.sem_type = sym, vtype

    def assign_target(self, t, vtype, sc, node):
        if isinstance(t, ast.Name):
            self.assign_name(t, vtype, sc, node)
        elif isinstance(t, (ast.Tuple, ast.List)):
            for e in t.elts: self.assign_target(e, "any", sc, node)
        elif isinstance(t, ast.Starred):
            self.assign_target(t.value, "any", sc, node)
        else:                                     # atribut / subscript: periksa ekspresi dasarnya
            for c in ast.iter_child_nodes(t):
                if isinstance(c, ast.expr): self.expr(c, sc)

    def body(self, stmts, sc):
        seen_defs = set()
        for s in stmts:
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not s.decorator_list:
                if s.name in seen_defs:
                    what = "class" if isinstance(s, ast.ClassDef) else "function"
                    self.report(s, "SE-R", f"{what} '{s.name}' is already declared in '{sc.name}'")
                seen_defs.add(s.name)
            self.stmt(s, sc)

    def stmt(self, s, sc):
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in s.decorator_list: self.expr(d, sc)
            for d in s.args.defaults + [x for x in s.args.kw_defaults if x]: self.expr(d, sc)
            self.check_dup_params(s)
            self.declare(sc, s.name, "function", "any", s.lineno, node=s)
            self.deferred.append((self.scopes[s], s))
        elif isinstance(s, ast.ClassDef):
            for b in s.bases: self.expr(b, sc)
            for d in s.decorator_list: self.expr(d, sc)
            self.declare(sc, s.name, "class", "any", s.lineno, node=s)
            csc = self.scopes[s]
            self.body(s.body, csc)
        elif isinstance(s, ast.Return):
            vt = self.expr(s.value, sc) if s.value else "None"
            if sc.kind != "function":
                self.report(s, "SE-F", "'return' outside function")
            elif sc.ret_type and s.value is not None and not compat(sc.ret_type, vt):
                self.report(s, "SE-F", f"return value of type {vt} does not match declared return type {sc.ret_type}")
        elif isinstance(s, ast.Assign):
            vt = self.expr(s.value, sc)
            for t in s.targets: self.assign_target(t, vt, sc, s)
        elif isinstance(s, ast.AnnAssign):
            vt = self.expr(s.value, sc) if s.value else None
            if isinstance(s.target, ast.Name):
                dt = self.ann_type(s.annotation)
                old = sc.symbols.get(s.target.id)
                if old is not None and old.annotated and old.type != dt and old.kind == "variable":
                    self.report(s, "SE-R", f"'{s.target.id}' re-declared as {dt}; previously declared as {old.type}")
                elif vt is not None and not compat(dt, vt):
                    self.report(s, "SE-T", f"cannot assign {vt} to '{s.target.id}' declared as {dt}")
                sym = self.declare(sc, s.target.id, "variable", dt, s.lineno, annotated=True)
                if sym.type != dt and not (old and old.annotated):
                    sym.type = dt
                if s.value is None:
                    sc.declared.discard(s.target.id) if old is None else None
                    sc.declared.add(s.target.id)
            else:
                self.assign_target(s.target, vt or "any", sc, s)
        elif isinstance(s, ast.AugAssign):
            if isinstance(s.target, ast.Name):
                lt = self.load_name(ast.copy_location(ast.Name(s.target.id, ast.Load()), s.target), sc)
                vt = self.expr(s.value, sc)
                res = self.binop(ast.copy_location(ast.BinOp(s.target, s.op, s.value), s), lt, vt)
                self.assign_name(s.target, res, sc, s)
            else:
                self.assign_target(s.target, "any", sc, s); self.expr(s.value, sc)
        elif isinstance(s, (ast.For, ast.AsyncFor)):
            self.expr(s.iter, sc)
            sc.declared |= stored_names(s.body + s.orelse) - sc.globals_decl     # tidak flow-sensitive
            self.assign_target(s.target, "any", sc, s)
            self.body(s.body, sc); self.body(s.orelse, sc)
        elif isinstance(s, ast.While):
            sc.declared |= stored_names(s.body + s.orelse) - sc.globals_decl
            self.expr(s.test, sc); self.body(s.body, sc); self.body(s.orelse, sc)
        elif isinstance(s, ast.If):
            self.expr(s.test, sc); self.body(s.body, sc); self.body(s.orelse, sc)
        elif isinstance(s, (ast.With, ast.AsyncWith)):
            for it in s.items:
                self.expr(it.context_expr, sc)
                if it.optional_vars is not None: self.assign_target(it.optional_vars, "any", sc, s)
            self.body(s.body, sc)
        elif isinstance(s, ast.Try) or s.__class__.__name__ == "TryStar":
            self.body(s.body, sc)
            for h in s.handlers:
                if h.type is not None: self.expr(h.type, sc)
                if h.name: self.declare(sc, h.name, "variable", "any", h.lineno)
                self.body(h.body, sc)
            self.body(s.orelse, sc); self.body(s.finalbody, sc)
        elif isinstance(s, (ast.Import, ast.ImportFrom)):
            for al in s.names:
                if al.name != "*":
                    self.declare(sc, (al.asname or al.name).split(".")[0], "import", "any", s.lineno)
        elif isinstance(s, (ast.Global, ast.Nonlocal, ast.Pass, ast.Break, ast.Continue)):
            pass
        elif isinstance(s, ast.Expr):
            self.expr(s.value, sc)
        else:
            for c in ast.iter_child_nodes(s):
                if isinstance(c, ast.expr): self.expr(c, sc)
                elif isinstance(c, ast.stmt): self.stmt(c, sc)

    # ------------------------------------------------------------------ PASS 2
    def pass2(self, tree):
        self.body(tree.body, self.module)
        while self.deferred:                      # badan fungsi diperiksa setelah modul selesai
            sc, node = self.deferred.popleft()
            a = node.args
            for p in a.posonlyargs + a.args + a.kwonlyargs + ([a.vararg] if a.vararg else []) + \
                     ([a.kwarg] if a.kwarg else []):
                t = self.ann_type(p.annotation)
                self.declare(sc, p.arg, "param", t, node.lineno, annotated=p.annotation is not None)
            if isinstance(node, ast.Lambda):
                self.expr(node.body, sc)
            else:
                sc.ret_type = self.ann_type(node.returns) if node.returns is not None else None
                self.body(node.body, sc)

    def analyze(self, source: str):
        self.__init__()
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return [Diagnostic(e.lineno or 0, "SYNTAX", str(e.msg))]
        self.pass1(tree)
        self.pass2(tree)
        self.tree = tree                         # Annotated AST
        return sorted(self.diags, key=lambda d: d.line)


def analyze(source: str):
    return SemanticAnalyzer().analyze(source)


if __name__ == "__main__":
    demo = ('def area(w: float, h: float) -> float:\n    return w * h\ncount: int = "ten"\n'
            'total = count + undefined_value\narea(2)\ndef helper():\n    tmp = 1\nprint(tmp)\n')
    for d in analyze(demo):
        print(d)
