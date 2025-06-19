import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import ast
import re
import json
from datetime import datetime

class PyjamaConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_gui()
        self.conversion_history = []
        self.current_theme = "light"
        
    def setup_gui(self):
        self.root.title("Pyjama - Python to Java Converter")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.setup_themes()
        
        # Menu bar
        self.setup_menu()
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Toolbar
        self.setup_toolbar(main_container)
        
        # Code editors section
        editor_frame = ttk.Frame(main_container)
        editor_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Left side - Python editor
        python_frame = ttk.LabelFrame(editor_frame, text="Python Code", padding=5)
        python_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Python editor toolbar
        py_toolbar = ttk.Frame(python_frame)
        py_toolbar.pack(fill="x", pady=(0, 5))
        
        ttk.Button(py_toolbar, text="📁 Load", command=self.load_python_file).pack(side="left", padx=(0, 5))
        ttk.Button(py_toolbar, text="💾 Save", command=self.save_python_file).pack(side="left", padx=(0, 5))
        ttk.Button(py_toolbar, text="🗑️ Clear", command=self.clear_python).pack(side="left", padx=(0, 5))
        
        # Line numbers and Python text
        py_text_frame = ttk.Frame(python_frame)
        py_text_frame.pack(fill="both", expand=True)
        
        self.python_text = scrolledtext.ScrolledText(
            py_text_frame, wrap="none", height=25, width=50,
            font=("Consolas", 11), insertbackground="blue"
        )
        self.python_text.pack(fill="both", expand=True)
        self.python_text.bind('<KeyRelease>', self.on_python_change)
        
        # Right side - Java output
        java_frame = ttk.LabelFrame(editor_frame, text="Java Code", padding=5)
        java_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Java editor toolbar
        java_toolbar = ttk.Frame(java_frame)
        java_toolbar.pack(fill="x", pady=(0, 5))
        
        ttk.Button(java_toolbar, text="💾 Save Java", command=self.save_java_file).pack(side="left", padx=(0, 5))
        ttk.Button(java_toolbar, text="📋 Copy", command=self.copy_java).pack(side="left", padx=(0, 5))
        
        self.java_text = scrolledtext.ScrolledText(
            java_frame, wrap="none", height=25, width=50,
            font=("Consolas", 11), bg="#f8f8f8", state="disabled"
        )
        self.java_text.pack(fill="both", expand=True)
        
        # Bottom section - Controls and explanations
        bottom_frame = ttk.Frame(main_container)
        bottom_frame.pack(fill="x", pady=(10, 0))
        
        # Convert button and options
        control_frame = ttk.Frame(bottom_frame)
        control_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(control_frame, text="🔄 Convert", command=self.convert, 
                  style="Accent.TButton").pack(side="left", padx=(0, 10))
        
        # Conversion options
        options_frame = ttk.LabelFrame(control_frame, text="Options", padding=5)
        options_frame.pack(side="left", fill="x", expand=True)
        
        self.auto_convert_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Auto-convert", 
                       variable=self.auto_convert_var).pack(side="left", padx=(0, 10))
        
        self.add_main_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Add main method", 
                       variable=self.add_main_var).pack(side="left", padx=(0, 10))
        
        self.add_imports_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Add imports", 
                       variable=self.add_imports_var).pack(side="left", padx=(0, 10))
        
        ttk.Label(options_frame, text="Class name:").pack(side="left", padx=(10, 5))
        self.class_name_var = tk.StringVar(value="Main")
        ttk.Entry(options_frame, textvariable=self.class_name_var, width=15).pack(side="left")
        
        # Explanation section
        explanation_frame = ttk.LabelFrame(bottom_frame, text="Conversion Explanation", padding=5)
        explanation_frame.pack(fill="both", expand=True)
        
        self.explanation_text = scrolledtext.ScrolledText(
            explanation_frame, height=8, wrap="word", font=("Segoe UI", 10)
        )
        self.explanation_text.pack(fill="both", expand=True)
        self.explanation_text.config(state="disabled")
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken")
        status_bar.pack(side="bottom", fill="x")
        
        # Load sample code
        self.load_sample_code()
        
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Python...", command=self.load_python_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save Python...", command=self.save_python_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save Java...", command=self.save_java_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy Java", command=self.copy_java, accelerator="Ctrl+C")
        edit_menu.add_command(label="Clear Python", command=self.clear_python)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        view_menu.add_command(label="Conversion History", command=self.show_history)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate Python", command=self.validate_python)
        tools_menu.add_command(label="Format Python", command=self.format_python)
        tools_menu.add_command(label="Load Sample", command=self.load_sample_code)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Supported Features", command=self.show_features)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.load_python_file())
        self.root.bind('<Control-s>', lambda e: self.save_python_file())
        self.root.bind('<Control-Return>', lambda e: self.convert())
        self.root.bind('<F5>', lambda e: self.convert())
        
    def setup_toolbar(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill="x", pady=(0, 5))
        
        ttk.Button(toolbar, text="🆕 New", command=self.new_file).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="📁 Open", command=self.load_python_file).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="💾 Save", command=self.save_python_file).pack(side="left", padx=(0, 5))
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(toolbar, text="🔄 Convert", command=self.convert).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="✅ Validate", command=self.validate_python).pack(side="left", padx=(0, 5))
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=10)
        ttk.Button(toolbar, text="🎨 Theme", command=self.toggle_theme).pack(side="left", padx=(0, 5))
        ttk.Button(toolbar, text="📊 History", command=self.show_history).pack(side="left", padx=(0, 5))
        
    def setup_themes(self):
        # Configure custom styles
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        
    def indent(self, code, level):
        """Indent code by specified level"""
        return "\n".join("    " * level + line for line in code.splitlines() if line.strip())
    
    def infer_type_and_reason(self, value_node):
        """Enhanced type inference with better reasoning"""
        if isinstance(value_node, ast.Constant):
            value = value_node.value
            if isinstance(value, bool):
                return "boolean", f"Boolean literal `{value}` → `boolean`"
            elif isinstance(value, int):
                if -2147483648 <= value <= 2147483647:
                    return "int", f"Integer literal `{value}` fits in int range → `int`"
                else:
                    return "long", f"Integer literal `{value}` requires long → `long`"
            elif isinstance(value, float):
                return "double", f"Float literal `{value}` → `double`"
            elif isinstance(value, str):
                return "String", f"String literal → `String`"
            elif value is None:
                return "Object", "`None` → `null`, using `Object` type"
        elif isinstance(value_node, ast.List):
            return "ArrayList<Object>", "List literal → `ArrayList<Object>`"
        elif isinstance(value_node, ast.Dict):
            return "HashMap<Object, Object>", "Dictionary literal → `HashMap<Object, Object>`"
        elif isinstance(value_node, ast.BinOp):
            return "Object", "Binary operation result → `Object` (type depends on operands)"
        
        return "Object", "Complex expression → defaulting to `Object`"
    
    def expr_to_java(self, expr):
        """Enhanced expression conversion"""
        if isinstance(expr, ast.Constant):
            value = expr.value
            if isinstance(value, str):
                return f'"{value}"'
            elif isinstance(value, bool):
                return "true" if value else "false"
            elif value is None:
                return "null"
            else:
                return str(value)
        elif isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.BinOp):
            left = self.expr_to_java(expr.left)
            right = self.expr_to_java(expr.right)
            op_map = {
                ast.Add: "+", ast.Sub: "-", ast.Mult: "*",
                ast.Div: "/", ast.Mod: "%", ast.Pow: "Math.pow",
                ast.FloorDiv: "/"
            }
            if isinstance(expr.op, ast.Pow):
                return f"Math.pow({left}, {right})"
            op = op_map.get(type(expr.op), "?")
            return f"({left} {op} {right})"
        elif isinstance(expr, ast.Compare):
            left = self.expr_to_java(expr.left)
            right = self.expr_to_java(expr.comparators[0])
            op_map = {
                ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<",
                ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
                ast.In: ".contains", ast.NotIn: "!.contains"
            }
            op = op_map.get(type(expr.ops[0]), "==")
            if op in [".contains", "!.contains"]:
                contains = "!" if op.startswith("!") else ""
                return f"{contains}{right}.contains({left})"
            return f"{left} {op} {right}"
        elif isinstance(expr, ast.Call):
            return self.call_to_java(expr)
        elif isinstance(expr, ast.List):
            elements = [self.expr_to_java(el) for el in expr.elts]
            return f"Arrays.asList({', '.join(elements)})"
        elif isinstance(expr, ast.Subscript):
            value = self.expr_to_java(expr.value)
            slice_value = self.expr_to_java(expr.slice)
            return f"{value}.get({slice_value})"
        else:
            return f"/* Unsupported expression: {ast.dump(expr)} */"
    
    def call_to_java(self, call_node):
        """Convert function calls to Java"""
        if isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id
            args = [self.expr_to_java(arg) for arg in call_node.args]
            
            if func_name == "print":
                return f"System.out.println({', '.join(args) if args else ''})"
            elif func_name == "len":
                return f"{args[0]}.size()" if args else "0"
            elif func_name == "str":
                return f"String.valueOf({args[0]})" if args else '""'
            elif func_name == "int":
                return f"Integer.parseInt({args[0]})" if args else "0"
            elif func_name == "float":
                return f"Double.parseDouble({args[0]})" if args else "0.0"
            elif func_name == "abs":
                return f"Math.abs({args[0]})" if args else "0"
            elif func_name == "max":
                return f"Math.max({', '.join(args)})" if len(args) >= 2 else args[0] if args else "0"
            elif func_name == "min":
                return f"Math.min({', '.join(args)})" if len(args) >= 2 else args[0] if args else "0"
            elif func_name == "range":
                return self.handle_range(call_node.args)
            else:
                return f"{func_name}({', '.join(args)})"
        
        return "/* Unsupported function call */"
    
    def handle_range(self, args):
        """Handle Python range() function"""
        if len(args) == 1:
            return f"0; i < {self.expr_to_java(args[0])}; i++"
        elif len(args) == 2:
            return f"{self.expr_to_java(args[0])}; i < {self.expr_to_java(args[1])}; i++"
        elif len(args) == 3:
            start = self.expr_to_java(args[0])
            end = self.expr_to_java(args[1])
            step = self.expr_to_java(args[2])
            return f"{start}; i < {end}; i += {step}"
        return "0; i < 10; i++"
    
    def convert_node(self, node, level=0):
        """Enhanced node conversion with better error handling"""
        java_lines = []
        explanations = []
        
        try:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                java_type, reason = self.infer_type_and_reason(node.value)
                value = self.expr_to_java(node.value)
                java_lines.append(f"{java_type} {var_name} = {value};")
                explanations.append(f"Variable assignment: `{var_name}` → {reason}")
                
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                var_name = node.target.id
                op_map = {ast.Add: "+=", ast.Sub: "-=", ast.Mult: "*=", ast.Div: "/="}
                op = op_map.get(type(node.op), "=")
                value = self.expr_to_java(node.value)
                java_lines.append(f"{var_name} {op} {value};")
                explanations.append(f"Augmented assignment: `{var_name} {op} {value}`")
                
            elif isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Call):
                    java_lines.append(f"{self.call_to_java(node.value)};")
                    explanations.append("Function call converted")
                else:
                    expr = self.expr_to_java(node.value)
                    java_lines.append(f"{expr};")
                    explanations.append("Expression statement")
                    
            elif isinstance(node, ast.If):
                test = self.expr_to_java(node.test)
                java_lines.append(f"if ({test}) {{")
                
                for stmt in node.body:
                    sub_lines, sub_expl = self.convert_node(stmt, level + 1)
                    if sub_lines:
                        java_lines.append(self.indent(sub_lines, 1))
                    explanations.extend(sub_expl)
                
                if node.orelse:
                    java_lines.append("} else {")
                    for stmt in node.orelse:
                        sub_lines, sub_expl = self.convert_node(stmt, level + 1)
                        if sub_lines:
                            java_lines.append(self.indent(sub_lines, 1))
                        explanations.extend(sub_expl)
                
                java_lines.append("}")
                explanations.append("Conditional statement: `if/else` → Java if/else block")
                
            elif isinstance(node, ast.For):
                if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                    loop_var = node.target.id
                    range_params = self.handle_range(node.iter.args)
                    java_lines.append(f"for (int {loop_var} = {range_params}) {{")
                    
                    for stmt in node.body:
                        sub_lines, sub_expl = self.convert_node(stmt, level + 1)
                        if sub_lines:
                            java_lines.append(self.indent(sub_lines, 1))
                        explanations.extend(sub_expl)
                    
                    java_lines.append("}")
                    explanations.append("For loop with range() → Java for loop")
                else:
                    # Enhanced for loop for iterables
                    loop_var = node.target.id
                    iterable = self.expr_to_java(node.iter)
                    java_lines.append(f"for (Object {loop_var} : {iterable}) {{")
                    
                    for stmt in node.body:
                        sub_lines, sub_expl = self.convert_node(stmt, level + 1)
                        if sub_lines:
                            java_lines.append(self.indent(sub_lines, 1))
                        explanations.extend(sub_expl)
                    
                    java_lines.append("}")
                    explanations.append("For-each loop → Java enhanced for loop")
                    
            elif isinstance(node, ast.While):
                condition = self.expr_to_java(node.test)
                java_lines.append(f"while ({condition}) {{")
                
                for stmt in node.body:
                    sub_lines, sub_expl = self.convert_node(stmt, level + 1)
                    if sub_lines:
                        java_lines.append(self.indent(sub_lines, 1))
                    explanations.extend(sub_expl)
                
                java_lines.append("}")
                explanations.append("While loop → Java while loop")
                
            elif isinstance(node, ast.FunctionDef):
                params = []
                for arg in node.args.args:
                    params.append(f"Object {arg.arg}")
                
                param_str = ", ".join(params)
                java_lines.append(f"public static void {node.name}({param_str}) {{")
                
                for stmt in node.body:
                    sub_lines, sub_expl = self.convert_node(stmt, level + 1)
                    if sub_lines:
                        java_lines.append(self.indent(sub_lines, 1))
                    explanations.extend(sub_expl)
                
                java_lines.append("}")
                explanations.append(f"Function definition: `def {node.name}()` → Java static method")
                
            elif isinstance(node, ast.Return):
                if node.value:
                    value = self.expr_to_java(node.value)
                    java_lines.append(f"return {value};")
                else:
                    java_lines.append("return;")
                explanations.append("Return statement")
                
            elif isinstance(node, ast.Break):
                java_lines.append("break;")
                explanations.append("Break statement")
                
            elif isinstance(node, ast.Continue):
                java_lines.append("continue;")
                explanations.append("Continue statement")
                
            else:
                java_lines.append(f"/* Unsupported: {type(node).__name__} */")
                explanations.append(f"Unsupported AST node: {type(node).__name__}")
                
        except Exception as e:
            java_lines.append(f"/* Error converting {type(node).__name__}: {str(e)} */")
            explanations.append(f"Error processing {type(node).__name__}: {str(e)}")
        
        return "\n".join(java_lines), explanations
    
    def convert_python_to_java(self, python_code):
        """Main conversion function with enhanced features"""
        try:
            # Parse the Python code
            tree = ast.parse(python_code)
            java_lines = []
            explanations = []
            
            # Add imports if requested
            if self.add_imports_var.get():
                imports = [
                    "import java.util.*;",
                    "import java.io.*;",
                    "import java.math.*;"
                ]
                java_lines.extend(imports)
                java_lines.append("")
                explanations.append("Added common Java imports")
            
            # Add class declaration
            class_name = self.class_name_var.get() or "Main"
            java_lines.append(f"public class {class_name} {{")
            
            # Convert each top-level statement
            main_body = []
            static_methods = []
            
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    method_code, method_expl = self.convert_node(node, 1)
                    static_methods.append(self.indent(method_code, 1))
                    explanations.extend(method_expl)
                else:
                    stmt_code, stmt_expl = self.convert_node(node, 2)
                    if stmt_code:
                        main_body.append(stmt_code)
                    explanations.extend(stmt_expl)
            
            # Add main method if requested
            if self.add_main_var.get() and main_body:
                java_lines.append("    public static void main(String[] args) {")
                for stmt in main_body:
                    java_lines.append(self.indent(stmt, 2))
                java_lines.append("    }")
                explanations.append("Wrapped main code in main() method")
            
            # Add static methods
            if static_methods:
                java_lines.append("")
                java_lines.extend(static_methods)
            
            java_lines.append("}")
            
            return "\n".join(java_lines), "\n".join(explanations)
            
        except SyntaxError as e:
            error_msg = f"Python syntax error at line {e.lineno}: {e.msg}"
            return f"/* {error_msg} */", error_msg
        except Exception as e:
            error_msg = f"Conversion error: {str(e)}"
            return f"/* {error_msg} */", error_msg
    
    def convert(self):
        """Perform the conversion"""
        python_code = self.python_text.get("1.0", "end-1c").strip()
        
        if not python_code:
            self.status_var.set("No Python code to convert")
            return
        
        self.status_var.set("Converting...")
        
        try:
            java_code, explanation = self.convert_python_to_java(python_code)
            
            # Update Java text
            self.java_text.config(state="normal")
            self.java_text.delete("1.0", "end")
            self.java_text.insert("1.0", java_code)
            self.java_text.config(state="disabled")
            
            # Update explanation
            self.explanation_text.config(state="normal")
            self.explanation_text.delete("1.0", "end")
            self.explanation_text.insert("1.0", explanation)
            self.explanation_text.config(state="disabled")
            
            # Add to history
            self.conversion_history.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'python_code': python_code[:100] + "..." if len(python_code) > 100 else python_code,
                'java_code': java_code,
                'explanation': explanation
            })
            
            # Keep only last 20 conversions
            if len(self.conversion_history) > 20:
                self.conversion_history.pop(0)
            
            self.status_var.set(f"Conversion completed - {len(java_code.splitlines())} lines generated")
            
        except Exception as e:
            messagebox.showerror("Conversion Error", f"An error occurred during conversion:\n{str(e)}")
            self.status_var.set("Conversion failed")
    
    def on_python_change(self, event=None):
        """Auto-convert if enabled"""
        if self.auto_convert_var.get():
            self.root.after(1000, self.convert)  # Delay to avoid too frequent conversions
    
    def load_python_file(self):
        """Load Python file"""
        filename = filedialog.askopenfilename(
            title="Open Python File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.python_text.delete("1.0", "end")
                    self.python_text.insert("1.0", content)
                    self.status_var.set(f"Loaded: {filename}")
                    if self.auto_convert_var.get():
                        self.convert()
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file:\n{str(e)}")
    
    def save_python_file(self):
        """Save Python code"""
        filename = filedialog.asksaveasfilename(
            title="Save Python File",
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(self.python_text.get("1.0", "end-1c"))
                    self.status_var.set(f"Saved: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
    
    def save_java_file(self):
        """Save Java code"""
        filename = filedialog.asksaveasfilename(
            title="Save Java File",
            defaultextension=".java",
            filetypes=[("Java files", "*.java"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(self.java_text.get("1.0", "end-1c"))
                    self.status_var.set(f"Saved: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}")
    
    def copy_java(self):
        """Copy Java code to clipboard"""
        java_code = self.java_text.get("1.0", "end-1c")
        if java_code.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(java_code)
            self.status_var.set("Java code copied to clipboard")
        else:
            self.status_var.set("No Java code to copy")
    
    def clear_python(self):
        """Clear Python editor"""
        self.python_text.delete("1.0", "end")
        self.java_text.config(state="normal")
        self.java_text.delete("1.0", "end")
        self.java_text.config(state="disabled")
        self.explanation_text.config(state="normal")
        self.explanation_text.delete("1.0", "end")
        self.explanation_text.config(state="disabled")
        self.status_var.set("Cleared")
    
    def new_file(self):
        """Create new file"""
        self.clear_python()
        self.load_sample_code()
    
    def validate_python(self):
        """Validate Python syntax"""
        python_code = self.python_text.get("1.0", "end-1c").strip()
        if not python_code:
            messagebox.showwarning("Validation", "No Python code to validate")
            return
        
        try:
            ast.parse(python_code)
            messagebox.showinfo("Validation", "✅ Python syntax is valid!")
            self.status_var.set("Python syntax validated successfully")
        except SyntaxError as e:
            messagebox.showerror("Validation Error", 
                               f"❌ Python syntax error:\nLine {e.lineno}: {e.msg}")
            self.status_var.set(f"Syntax error at line {e.lineno}")
    
    def format_python(self):
        """Basic Python code formatting"""
        python_code = self.python_text.get("1.0", "end-1c")
        if not python_code.strip():
            return
        
        try:
            # Simple formatting - remove extra blank lines and normalize indentation
            lines = python_code.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    if formatted_lines and formatted_lines[-1].strip():
                        formatted_lines.append('')
                    continue
                
                # Adjust indent level
                if stripped.endswith(':'):
                    formatted_lines.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped in ['else:', 'elif', 'except:', 'finally:']:
                    indent_level = max(0, indent_level - 1)
                    formatted_lines.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped.startswith(('return', 'break', 'continue', 'pass')) and indent_level > 0:
                    formatted_lines.append('    ' * indent_level + stripped)
                else:
                    formatted_lines.append('    ' * indent_level + stripped)
            
            formatted_code = '\n'.join(formatted_lines)
            self.python_text.delete("1.0", "end")
            self.python_text.insert("1.0", formatted_code)
            self.status_var.set("Python code formatted")
            
        except Exception as e:
            messagebox.showerror("Format Error", f"Could not format code:\n{str(e)}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme == "light":
            # Dark theme
            self.style.configure("TFrame", background="#2d2d2d")
            self.style.configure("TLabel", background="#2d2d2d", foreground="#ffffff")
            self.style.configure("TButton", background="#404040", foreground="#ffffff")
            self.python_text.config(bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
            self.java_text.config(bg="#1e1e1e", fg="#ffffff")
            self.explanation_text.config(bg="#1e1e1e", fg="#ffffff")
            self.current_theme = "dark"
            self.status_var.set("Switched to dark theme")
        else:
            # Light theme
            self.style.configure("TFrame", background="#f0f0f0")
            self.style.configure("TLabel", background="#f0f0f0", foreground="#000000")
            self.style.configure("TButton", background="#e1e1e1", foreground="#000000")
            self.python_text.config(bg="#ffffff", fg="#000000", insertbackground="#000000")
            self.java_text.config(bg="#f8f8f8", fg="#000000")
            self.explanation_text.config(bg="#ffffff", fg="#000000")
            self.current_theme = "light"
            self.status_var.set("Switched to light theme")
    
    def show_history(self):
        """Show conversion history"""
        if not self.conversion_history:
            messagebox.showinfo("History", "No conversion history available")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("Conversion History")
        history_window.geometry("800x600")
        
        # History listbox
        frame = ttk.Frame(history_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Conversion History:", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")
        
        history_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=("Consolas", 10))
        history_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=history_listbox.yview)
        
        # Populate history
        for i, entry in enumerate(reversed(self.conversion_history)):
            history_listbox.insert(0, f"{entry['timestamp']}: {entry['python_code']}")
        
        def on_select(event):
            selection = history_listbox.curselection()
            if selection:
                index = len(self.conversion_history) - 1 - selection[0]
                entry = self.conversion_history[index]
                
                # Show details
                details_window = tk.Toplevel(history_window)
                details_window.title(f"Conversion Details - {entry['timestamp']}")
                details_window.geometry("1000x700")
                
                notebook = ttk.Notebook(details_window)
                notebook.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Python tab
                py_frame = ttk.Frame(notebook)
                notebook.add(py_frame, text="Python Code")
                py_text = scrolledtext.ScrolledText(py_frame, font=("Consolas", 10))
                py_text.pack(fill="both", expand=True)
                py_text.insert("1.0", entry['python_code'])
                py_text.config(state="disabled")
                
                # Java tab
                java_frame = ttk.Frame(notebook)
                notebook.add(java_frame, text="Java Code")
                java_text = scrolledtext.ScrolledText(java_frame, font=("Consolas", 10))
                java_text.pack(fill="both", expand=True)
                java_text.insert("1.0", entry['java_code'])
                java_text.config(state="disabled")
                
                # Explanation tab
                expl_frame = ttk.Frame(notebook)
                notebook.add(expl_frame, text="Explanation")
                expl_text = scrolledtext.ScrolledText(expl_frame, font=("Segoe UI", 10))
                expl_text.pack(fill="both", expand=True)
                expl_text.insert("1.0", entry['explanation'])
                expl_text.config(state="disabled")
        
        history_listbox.bind('<Double-1>', on_select)
        
        ttk.Label(frame, text="Double-click an entry to view details", 
                 font=("Segoe UI", 9)).pack(pady=(10, 0))
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Pyjama Pro - Advanced Python to Java Converter
Version 2.0

Features:
• Enhanced Python to Java conversion
• Syntax validation and formatting
• Dark/Light theme support
• Conversion history
• File operations (load/save)
• Auto-conversion mode
• Comprehensive error handling

Supported Python constructs:
• Variables and assignments
• Functions and methods
• Control flow (if/else, loops)
• Basic data types
• Mathematical operations
• Print statements and more

Created with ❤️ using Python and Tkinter
        """
        messagebox.showinfo("About Pyjama Pro", about_text)
    
    def show_features(self):
        """Show supported features"""
        features_window = tk.Toplevel(self.root)
        features_window.title("Supported Python Features")
        features_window.geometry("700x500")
        
        notebook = ttk.Notebook(features_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Basic constructs
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Constructs")
        
        basic_text = scrolledtext.ScrolledText(basic_frame, wrap="word", font=("Segoe UI", 10))
        basic_text.pack(fill="both", expand=True)
        basic_text.insert("1.0", """
✅ Variables and Assignments
- Simple assignments: x = 5
- Augmented assignments: x += 1
- Type inference: int, double, String, boolean

✅ Data Types
- Integers: 42 → int
- Floats: 3.14 → double  
- Strings: "hello" → String
- Booleans: True/False → true/false
- None → null

✅ Operators
- Arithmetic: +, -, *, /, %
- Comparison: ==, !=, <, <=, >, >=
- Power: ** → Math.pow()

✅ Print Statements
- print("hello") → System.out.println("hello")
- print(variable) → System.out.println(variable)
        """)
        basic_text.config(state="disabled")
        
        # Control flow
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Control Flow")
        
        control_text = scrolledtext.ScrolledText(control_frame, wrap="word", font=("Segoe UI", 10))
        control_text.pack(fill="both", expand=True)
        control_text.insert("1.0", """
✅ Conditional Statements
- if/else statements
- elif chains
- Nested conditions

✅ Loops
- for i in range(n) → for (int i = 0; i < n; i++)
- for item in list → for (Object item : list)
- while loops
- break and continue statements

✅ Functions
- def function_name() → public static void function_name()
- Parameters and return values
- Function calls
        """)
        control_text.config(state="disabled")
        
        # Built-in functions
        builtin_frame = ttk.Frame(notebook)
        notebook.add(builtin_frame, text="Built-in Functions")
        
        builtin_text = scrolledtext.ScrolledText(builtin_frame, wrap="word", font=("Segoe UI", 10))
        builtin_text.pack(fill="both", expand=True)
        builtin_text.insert("1.0", """
✅ Supported Built-in Functions
- len() → .size()
- str() → String.valueOf()
- int() → Integer.parseInt()
- float() → Double.parseDouble()
- abs() → Math.abs()
- max() → Math.max()
- min() → Math.min()
- range() → for loop conversion

❌ Not Yet Supported
- List comprehensions
- Lambda functions
- Classes and objects
- Exception handling (try/catch)
- Import statements
- File I/O operations
        """)
        builtin_text.config(state="disabled")
    
    def load_sample_code(self):
        """Load sample Python code"""
        sample_code = '''# Sample Python code for conversion
def calculate_factorial(n):
    if n <= 1:
        return 1
    else:
        return n * calculate_factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Main execution
num = 5
print("Factorial of", num, "is", calculate_factorial(num))

print("Fibonacci sequence:")
for i in range(10):
    print(fibonacci(i), end=" ")

# Variables and operations
x = 10
y = 20
result = x + y * 2
print("\\nResult:", result)

# Conditional logic
if result > 50:
    print("Result is large")
elif result > 25:
    print("Result is medium")
else:
    print("Result is small")

# Loop example
count = 0
while count < 3:
    print("Count:", count)
    count += 1
'''
        
        self.python_text.delete("1.0", "end")
        self.python_text.insert("1.0", sample_code)
        if self.auto_convert_var.get():
            self.root.after(500, self.convert)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = PyjamaConverter()
    app.run()