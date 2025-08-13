# advanced_calculator_ui.py
from __future__ import annotations
import ast
import math
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, List, Optional

# ========= Safe Evaluator (AST-based) =========
class SafeEvaluator(ast.NodeVisitor):
    def __init__(self, vars: Dict[str, float], angle_mode: str = "rad") -> None:
        self.vars = vars
        self.angle_mode = angle_mode  # "rad" or "deg"
        self.allowed_funcs = {
            "sin": self._wrap_angle(math.sin),
            "cos": self._wrap_angle(math.cos),
            "tan": self._wrap_angle(math.tan),
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "sqrt": math.sqrt,
            "exp": math.exp,
            "log": math.log,     # natural log
            "ln": math.log,      # alias
            "log10": math.log10,
            "pow": pow,
            "abs": abs,
            "floor": math.floor,
            "ceil": math.ceil,
            "round": round,
        }
        self.allowed_consts = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
        }

    def _wrap_angle(self, f):
        def inner(x):
            if self.angle_mode == "deg":
                x = math.radians(x)
            return f(x)
        return inner

    def generic_visit(self, node: ast.AST) -> Any:
        raise ValueError(f"Unsupported syntax: {node.__class__.__name__}")

    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Only numeric literals are allowed.")

    def visit_Name(self, node: ast.Name) -> Any:
        name = node.id
        if name in self.allowed_consts:
            return float(self.allowed_consts[name])
        if name in self.allowed_funcs:
            return self.allowed_funcs[name]
        if name in self.vars:
            return float(self.vars[name])
        raise ValueError(f"Unknown identifier: {name}")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ValueError("Unsupported unary operator.")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError("Unsupported binary operator.")

    def visit_Call(self, node: ast.Call) -> Any:
        func = self.visit(node.func)
        if func not in self.allowed_funcs.values():
            raise ValueError("Function not allowed.")
        if node.keywords:
            raise ValueError("Keyword arguments are not supported.")
        args = [self.visit(a) for a in node.args]
        return func(*args)

    def evaluate(self, expr: str) -> float:
        tree = ast.parse(expr, mode="eval")
        return float(self.visit(tree))

# ========= GUI App =========
class CalculatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Advanced Calculator")
        self.vars: Dict[str, float] = {}
        self.angle_mode = tk.StringVar(value="rad")  # "rad" or "deg"
        self.history: List[str] = []
        self.last_result: Optional[float] = None

        # Top: expression entry
        self.expr = tk.StringVar()
        entry = ttk.Entry(root, textvariable=self.expr, font=("Menlo", 14))
        entry.grid(row=0, column=0, columnspan=6, sticky="nsew", padx=8, pady=(8,4))
        entry.focus()

        # Angle mode toggle
        ttk.Label(root, text="Angle:").grid(row=1, column=0, sticky="w", padx=(8,2))
        ttk.Radiobutton(root, text="Rad", variable=self.angle_mode, value="rad").grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(root, text="Deg", variable=self.angle_mode, value="deg").grid(row=1, column=2, sticky="w")

        # Buttons
        btns = [
            ("7",), ("8",), ("9",), ("/",), ("//",), ("%",),
            ("4",), ("5",), ("6",), ("*",), ("(",), (")",),
            ("1",), ("2",), ("3",), ("-",), ("pi",), ("e",),
            ("0",), (".",), ("**",), ("+",), ("tau",), ("CLR",),
        ]
        row = 2
        col = 0
        for label, in btns:
            action = (lambda L=label: self.insert_token(L)) if label not in {"CLR"} \
                     else self.clear_expr
            b = ttk.Button(root, text=label, command=action)
            b.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            col += 1
            if col == 6:
                col = 0
                row += 1

        # Scientific buttons
        sci = [
            "sin(", "cos(", "tan(", "asin(", "acos(", "atan(",
            "sqrt(", "exp(", "log(", "ln(", "log10(", "abs(",
            "floor(", "ceil(", "round(", "pow(",
        ]
        for i, label in enumerate(sci):
            b = ttk.Button(root, text=label[:-1], command=(lambda L=label: self.insert_token(L)))
            b.grid(row=row + i//6, column=i%6, sticky="nsew", padx=4, pady=4)

        # Evaluate & Backspace
        ttk.Button(root, text="=", command=self.evaluate).grid(row=row+3, column=4, sticky="nsew", padx=4, pady=4)
        ttk.Button(root, text="⌫", command=self.backspace).grid(row=row+3, column=5, sticky="nsew", padx=4, pady=4)

        # Multi-number frame
        self.multi_frame = ttk.LabelFrame(root, text="Multi-number ops (+, -, *, /)")
        self.multi_frame.grid(row=row+4, column=0, columnspan=6, sticky="nsew", padx=8, pady=(8,6))
        ttk.Label(self.multi_frame, text="Numbers (comma-separated):").grid(row=0, column=0, sticky="w")
        self.multi_entry = ttk.Entry(self.multi_frame)
        self.multi_entry.grid(row=0, column=1, columnspan=3, sticky="nsew", padx=4)
        self.multi_op = tk.StringVar(value="+")
        ttk.OptionMenu(self.multi_frame, self.multi_op, "+", "+", "-", "*", "/").grid(row=0, column=4, padx=4)
        ttk.Button(self.multi_frame, text="Compute", command=self.compute_multi).grid(row=0, column=5, padx=4)

        # History panel
        self.hist_frame = ttk.LabelFrame(root, text="History (double-click to reuse)")
        self.hist_frame.grid(row=row+5, column=0, columnspan=6, sticky="nsew", padx=8, pady=(0,8))
        self.hist_list = tk.Listbox(self.hist_frame, height=6)
        self.hist_list.grid(row=0, column=0, sticky="nsew")
        self.hist_list.bind("<Double-1>", self.use_history)
        ttk.Button(self.hist_frame, text="Clear History", command=self.clear_history).grid(row=0, column=1, padx=6)

        # Grid weights
        for r in range(row+6):
            root.grid_rowconfigure(r, weight=0)
        root.grid_rowconfigure(row+5, weight=1)
        for c in range(6):
            root.grid_columnconfigure(c, weight=1)

        # Keyboard: Enter = evaluate
        root.bind("<Return>", lambda e: self.evaluate())

    # ----- UI helpers -----
    def insert_token(self, tok: str):
        self.expr.set(self.expr.get() + tok)

    def clear_expr(self):
        self.expr.set("")

    def backspace(self):
        self.expr.set(self.expr.get()[:-1])

    def add_history(self, expr: str, result: float):
        entry = f"{expr} = {result}"
        self.history.append(entry)
        self.hist_list.insert(tk.END, entry)

    def use_history(self, _event=None):
        sel = self.hist_list.curselection()
        if not sel: return
        item = self.hist_list.get(sel[0])
        # put left side back into expr
        if " = " in item:
            self.expr.set(item.split(" = ", 1)[0])

    def clear_history(self):
        self.history.clear()
        self.hist_list.delete(0, tk.END)

    # ----- compute -----
    def evaluate(self):
        expr = self.expr.get().strip()
        if not expr:
            return
        try:
            ev = SafeEvaluator(vars={}, angle_mode=self.angle_mode.get())
            result = ev.evaluate(expr)
            self.add_history(expr, result)
            self.expr.set(str(result))
        except ZeroDivisionError:
            messagebox.showerror("Math Error", "Division by zero.")
        except Exception as e:
            messagebox.showerror("Error", f"{e}")

    def compute_multi(self):
        raw = self.multi_entry.get().strip()
        if not raw:
            messagebox.showinfo("Input needed", "Please enter numbers separated by commas.")
            return
        try:
            nums = [float(x) for x in raw.split(",")]
        except Exception:
            messagebox.showerror("Error", "Please enter valid comma-separated numbers.")
            return
        if len(nums) < 2:
            messagebox.showerror("Error", "Please enter at least two numbers.")
            return

        op = self.multi_op.get()
        try:
            if op == "+":
                result = sum(nums)
            elif op == "-":
                res = nums[0]
                for n in nums[1:]:
                    res -= n
                result = res
            elif op == "*":
                res = 1.0
                for n in nums:
                    res *= n
                result = res
            elif op == "/":
                res = nums[0]
                for n in nums[1:]:
                    if n == 0:
                        messagebox.showerror("Math Error", "Division by zero.")
                        return
                    res /= n
                result = res
            else:
                messagebox.showerror("Error", "Unknown operation.")
                return
            # show & log result
            show = f"multi({op}): {raw}"
            self.add_history(show, result)
            self.expr.set(str(result))
        except Exception as e:
            messagebox.showerror("Error", f"{e}")

# ========= Run =========
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    CalculatorApp(root)
    root.minsize(680, 520)
    root.mainloop()