"""Independent re-evaluation of explicit numeric equality chains ('a op b = c [= d]') in answer text.
Handles thousands separators, ½, ×, ÷, −. Pure numbers only. Mismatch = candidate error for human check."""
from __future__ import annotations
import ast, operator, re

OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
       ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}
NUM = r"(?:½|\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
TERM = rf"\(?\s*-?{NUM}\s*\)?"
SEG = rf"{TERM}(?:\s*[+\-−×*/÷^]\s*{TERM})*"
CHAIN = re.compile(rf"(?<![\w.,^/%])({SEG}(?:\s*=\s*{SEG})+)(?![\d.,%]|\s*[×*/÷^]|\s*[가-힣]{{0,1}}%)")

def _ev(n):
    if isinstance(n, ast.Expression): return _ev(n.body)
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
    if isinstance(n, ast.BinOp) and type(n.op) in OPS:
        if isinstance(n.op, ast.Pow) and abs(_ev(n.right)) > 10: raise ValueError
        return OPS[type(n.op)](_ev(n.left), _ev(n.right))
    if isinstance(n, ast.UnaryOp) and type(n.op) in OPS: return OPS[type(n.op)](_ev(n.operand))
    raise ValueError("unsupported")

def _seg(s):
    py = s.replace(",", "").replace("½", "(1/2)").replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")
    py = re.sub(r"(?<=[\d)])\s*\(", "*(", py)
    return _ev(ast.parse(py.strip(), mode="eval"))

def _dec(s):
    m = re.fullmatch(r"\s*-?([\d,]+)(?:\.(\d+))?\s*", s)
    return (len(m.group(2)) if m.group(2) else 0) if m else None

def check(text: str):
    out = []
    for m in CHAIN.finditer(text):
        before = text[max(0, m.start() - 2): m.start()]; after = text[m.end(): m.end() + 1]
        if re.search(r"[A-Za-zα-ωΑ-Ω_)(]", after) or re.search(r"[A-Za-zα-ωΑ-Ω_]\s*[(=+\-−×*/]?\s*$", before):
            continue
        segs = m.group(1).split("=")
        if not any(re.search(r"[+\-−×*/÷^½]", s) for s in segs): continue
        try: vals = [_seg(s) for s in segs]
        except Exception: continue
        decs = [_dec(s) for s in segs]
        ok = True
        for i in range(1, len(vals)):
            d = decs[i] if decs[i] is not None else (decs[i-1] if decs[i-1] is not None else 6)
            tol = 0.5 * 10 ** (-d) * 1.0001 + 1e-9
            if abs(vals[i] - vals[i-1]) > tol and not (vals[i] and abs(vals[i]-vals[i-1]) / abs(vals[i]) < 1e-6):
                ok = False
        ctx = text[max(0, m.start() - 40): m.end() + 20].replace("\n", " ")
        out.append({"expr": m.group(1).strip(), "evaluated": [round(v, 6) for v in vals], "ok": ok, "context": ctx})
    return out

# ---- symbolic identity chains 'LABEL=expr=expr' with single-letter variables (SymPy) ----
SCHAIN = re.compile(r"(?<![\w.])([A-Za-z][A-Za-z0-9_]{0,3}=[^=\s가-힣,;:·]+(?:=[^=\s가-힣,;:·]+)+)")

def check_symbolic(text: str):
    import sympy as sp
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, rationalize
    tr = standard_transformations + (implicit_multiplication_application, rationalize)
    out = []
    for m in SCHAIN.finditer(text.replace(" = ", "=")):
        segs = m.group(1).rstrip(".)").split("=")[1:]
        if len(segs) < 2 or not any(re.search(r"[A-Za-z]", x) for x in segs): continue
        try:
            ex = []
            for x in segs:
                py = x.replace("²", "**2").replace(",", "").replace("½", "(1/2)").replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")
                if not re.fullmatch(r"[A-Za-z0-9\s.+\-*/()]+", py) or py.count("(") != py.count(")"): raise ValueError
                if re.search(r"[A-Za-z]{2,}", py): raise ValueError
                names = set(re.findall(r"[A-Za-z]", py))
                ex.append(parse_expr(py, local_dict={n: sp.Symbol(n) for n in names}, transformations=tr))
        except Exception:
            continue
        res = [sp.simplify(a - b) == 0 for a, b in zip(ex, ex[1:])
               if a.free_symbols and a.free_symbols == b.free_symbols]
        if not res: continue
        out.append({"expr": m.group(1), "ok": all(res), "pairsCompared": len(res),
                    "context": text[max(0, m.start() - 40): m.end() + 20].replace("\n", " ")})
    return out
