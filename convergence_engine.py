import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt

# --- Configuration & Theme ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Matplotlib Dark Theme
plt.style.use('dark_background')

# Colors
COLOR_BG = "#1a1a1a"  # Dark Grey/Black
COLOR_ACCENT = "#1f6aa5" # CTK Blue
COLOR_TEXT = "#ffffff"
COLOR_PLOT_BG = "#2b2b2b"
COLOR_LINE_Y_X = "#00ff00" # Green
COLOR_LINE_G_X = "#00ffff" # Cyan
COLOR_COBWEB = "#ffff00" # Yellow

class IterationEngine:
    """
    Handles the mathematical logic and state of the Fixed Point Iteration.
    """
    def __init__(self):
        self.g_func = None
        self.g_str = ""
        self.x_current = 0.0
        self.history = [] # List of (x, y) tuples for plotting
        self.step_count = 0
        self.error = None

    def initialize(self, g_expression, x0):
        """
        Parses the function and sets initial state.
        """
        try:
            # Create a safe context for eval, including numpy functions
            context = {k: v for k, v in np.__dict__.items() if callable(v) or isinstance(v, (int, float, np.number))}
            context['x'] = 0 # Test variable
            
            # Test if expression is valid
            self.g_str = g_expression
            # Lambda to evaluate g(x)
            self.g_func = lambda x: eval(g_expression, {"__builtins__": None}, context | {'x': x})
            
            # Test call
            self.g_func(float(x0))
            
            self.x_current = float(x0)
            self.history = [(self.x_current, 0)] # Start at (x0, 0)
            self.step_count = 0
            self.error = None
            return True, "Initialization Successful."
        except Exception as e:
            return False, f"Error parsing function: {e}"

    def step(self):
        """
        Performs one iteration step: x_{n+1} = g(x_n).
        Returns details for logging and plotting.
        """
        if not self.g_func:
            return None

        x_in = self.x_current
        try:
            x_out = self.g_func(x_in)
        except Exception as e:
            return {"error": str(e)}

        # Calculate Error (Relative Approximate Error)
        if x_out != 0:
            self.error = abs((x_out - x_in) / x_out) * 100
        else:
            self.error = 0.0

        # Update State
        # Cobweb path: (x_in, 0) -> (x_in, x_out) -> (x_out, x_out)
        # But we already have (x_in, 0) or (x_in, x_in) from previous step.
        # Let's define the segments to draw for this step.
        
        # Segment 1: Vertical from x_in to curve g(x)
        p1 = (x_in, x_in) if self.step_count > 0 else (x_in, 0) 
        # Actually, standard cobweb usually keeps y=x as reference.
        # If we are at x_in, we are effectively at (x_in, x_in) on the diagonal (or (x_in, 0) for start).
        # We go VERTICALLY to (x_in, g(x_in)).
        
        # Segment 2: Horizontally to y=x line
        # From (x_in, g(x_in)) to (g(x_in), g(x_in))
        
        # Wait, if we start at (x0, 0), first move is to (x0, g(x0)).
        # Then we move to (g(x0), g(x0)).
        # This (g(x0), g(x0)) is the new point on diagonal, representing x1.
        
        prev_pt = self.history[-1]
        
        # Vertical move
        pt_curve = (x_in, x_out)
        
        # Horizontal move
        pt_diag = (x_out, x_out)
        
        self.history.append(pt_curve)
        self.history.append(pt_diag)
        
        self.x_current = x_out
        self.step_count += 1
        
        return {
            "step": self.step_count,
            "x_in": x_in,
            "x_out": x_out,
            "error": self.error,
            "points": [prev_pt, pt_curve, pt_diag]
        }

    def run_auto(self, tolerance, max_iter):
        """
        Runs the iteration automatically until error < tolerance or max_iter reached.
        Returns a list of step data.
        """
        if not self.g_func:
            return None

        results = []
        
        # If we haven't started, do the first step? 
        # Or just continue from where we are?
        # Let's assume we continue from current state.
        
        while self.step_count < max_iter:
            step_data = self.step()
            if not step_data or "error" in step_data and isinstance(step_data["error"], str):
                 results.append(step_data)
                 break
            
            results.append(step_data)
            
            if step_data["error"] < tolerance:
                break
                
        return results

    def reset(self):
        self.g_func = None
        self.x_current = 0.0
        self.history = []
        self.step_count = 0
        self.error = None


import tkinter.ttk as ttk

class ConvergenceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("The Convergence Engine: Fixed Point Iteration")
        self.geometry("1200x800")
        self.engine = IterationEngine()

        # Grid Layout Configuration
        self.grid_columnconfigure(0, weight=0) # Sidebar (Fixed width)
        self.grid_columnconfigure(1, weight=1) # Main Content
        self.grid_rowconfigure(0, weight=1)

        # --- Left Side: Sidebar (Configuration) ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.init_sidebar()

        # --- Right Side: Main Content (Tabs) ---
        self.tabview = ctk.CTkTabview(self, fg_color="transparent")
        self.tabview.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.tab_graph = self.tabview.add("Visualization")
        self.tab_table = self.tabview.add("Data Table")
        
        self.init_graph_tab()
        self.init_table_tab()

    def init_sidebar(self):
        self.sidebar.grid_rowconfigure(10, weight=1) # Push log to bottom if needed, or just let it expand

        # Header
        lbl_title = ctk.CTkLabel(self.sidebar, text="CONFIGURATION", font=("Roboto", 20, "bold"))
        lbl_title.pack(padx=20, pady=(20, 10), anchor="w")

        # 1. Inputs
        self.frame_inputs = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_inputs.pack(padx=20, pady=10, fill="x")
        
        # Function g(x)
        ctk.CTkLabel(self.frame_inputs, text="Function g(x):", font=("Roboto", 14)).pack(anchor="w")
        self.entry_g = ctk.CTkEntry(self.frame_inputs, placeholder_text="e.g., np.cos(x)")
        self.entry_g.pack(fill="x", pady=(0, 10))
        
        # Initial Guess x0
        ctk.CTkLabel(self.frame_inputs, text="Initial Guess x0:", font=("Roboto", 14)).pack(anchor="w")
        self.entry_x0 = ctk.CTkEntry(self.frame_inputs, placeholder_text="e.g., 0.5")
        self.entry_x0.pack(fill="x", pady=(0, 10))

        # Tolerance
        ctk.CTkLabel(self.frame_inputs, text="Tolerance:", font=("Roboto", 14)).pack(anchor="w")
        self.entry_tol = ctk.CTkEntry(self.frame_inputs, placeholder_text="e.g., 0.0001")
        self.entry_tol.insert(0, "0.0001")
        self.entry_tol.pack(fill="x", pady=(0, 10))

        # Max Iterations
        ctk.CTkLabel(self.frame_inputs, text="Max Iterations:", font=("Roboto", 14)).pack(anchor="w")
        self.entry_max_iter = ctk.CTkEntry(self.frame_inputs, placeholder_text="e.g., 100")
        self.entry_max_iter.insert(0, "100")
        self.entry_max_iter.pack(fill="x", pady=(0, 10))

        # 2. Control Deck
        self.frame_buttons = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_buttons.pack(padx=20, pady=10, fill="x")
        
        self.btn_init = ctk.CTkButton(self.frame_buttons, text="INITIALIZE", command=self.on_initialize, fg_color=COLOR_ACCENT)
        self.btn_init.pack(fill="x", pady=5)
        
        self.btn_step = ctk.CTkButton(self.frame_buttons, text="NEXT STEP", command=self.on_step, state="disabled")
        self.btn_step.pack(fill="x", pady=5)

        self.btn_auto = ctk.CTkButton(self.frame_buttons, text="RUN AUTO", command=self.on_run_auto, state="disabled", fg_color="#2ecc71", hover_color="#27ae60")
        self.btn_auto.pack(fill="x", pady=5)
        
        self.btn_reset = ctk.CTkButton(self.frame_buttons, text="RESET", command=self.on_reset, fg_color="#c0392b", hover_color="#e74c3c")
        self.btn_reset.pack(fill="x", pady=5)

        # 3. System Log
        ctk.CTkLabel(self.sidebar, text="System Log", font=("Roboto", 14, "bold")).pack(padx=20, pady=(20, 0), anchor="w")
        self.log_box = ctk.CTkTextbox(self.sidebar, font=("Consolas", 12), height=200)
        self.log_box.pack(padx=20, pady=(5, 20), fill="both", expand=True)
        self.log_box.configure(state="disabled")

    def init_graph_tab(self):
        self.tab_graph.grid_columnconfigure(0, weight=1)
        self.tab_graph.grid_rowconfigure(0, weight=1)

        # Create Figure
        self.fig = Figure(figsize=(5, 5), dpi=100, facecolor=COLOR_PLOT_BG)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(COLOR_PLOT_BG)
        self.ax.set_title("Fixed Point Iteration Visualization", color=COLOR_TEXT)
        self.ax.set_xlabel("x", color=COLOR_TEXT)
        self.ax.set_ylabel("y", color=COLOR_TEXT)
        self.ax.tick_params(axis='x', colors=COLOR_TEXT)
        self.ax.tick_params(axis='y', colors=COLOR_TEXT)
        
        # Initial empty plot
        self.ax.grid(True, linestyle='--', alpha=0.3)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_graph)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.tab_graph)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def init_table_tab(self):
        self.tab_table.grid_columnconfigure(0, weight=1)
        self.tab_table.grid_rowconfigure(0, weight=1)

        # Treeview Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background=COLOR_BG, 
                        foreground=COLOR_TEXT, 
                        fieldbackground=COLOR_BG,
                        rowheight=25)
        style.configure("Treeview.Heading", 
                        background="#333333", 
                        foreground=COLOR_TEXT, 
                        font=("Roboto", 10, "bold"))
        style.map("Treeview", background=[('selected', COLOR_ACCENT)])

        # Treeview
        columns = ("step", "x_current", "x_next", "error")
        self.tree = ttk.Treeview(self.tab_table, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("step", text="Step")
        self.tree.heading("x_current", text="Current X")
        self.tree.heading("x_next", text="Next X")
        self.tree.heading("error", text="Error (%)")
        
        self.tree.column("step", width=50, anchor="center")
        self.tree.column("x_current", width=150, anchor="center")
        self.tree.column("x_next", width=150, anchor="center")
        self.tree.column("error", width=150, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tab_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def on_initialize(self):
        g_str = self.entry_g.get()
        x0_str = self.entry_x0.get()
        
        if not g_str or not x0_str:
            self.log("[ERROR] Please fill in Function and Initial Guess.")
            return

        success, msg = self.engine.initialize(g_str, x0_str)
        if success:
            self.log(f"[SYSTEM] {msg}")
            self.log(f"[INIT] g(x) = {g_str}")
            self.log(f"[INIT] x0 = {x0_str}")
            
            self.entry_g.configure(state="disabled")
            self.entry_x0.configure(state="disabled")
            self.btn_init.configure(state="disabled")
            self.btn_step.configure(state="normal")
            self.btn_auto.configure(state="normal")
            
            self.plot_base_functions()
            
            # Switch to graph tab initially
            self.tabview.set("Visualization")
        else:
            self.log(f"[ERROR] {msg}")

    def plot_base_functions(self):
        self.ax.clear()
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.set_title(f"Fixed Point Iteration: x = {self.engine.g_str}", color=COLOR_TEXT)
        
        x0 = self.engine.x_current
        # Dynamic range based on x0?
        # Let's try to be smart. If x0 is 100, range [-2, 2] is bad.
        # Let's do [x0 - 5, x0 + 5] roughly.
        span = 5
        x_min, x_max = x0 - span, x0 + span
        
        x_vals = np.linspace(x_min, x_max, 400)
        
        # Plot y = x
        self.ax.plot(x_vals, x_vals, color=COLOR_LINE_Y_X, label="y = x", linewidth=1.5)
        
        # Plot y = g(x)
        try:
            y_vals = [self.engine.g_func(x) for x in x_vals]
            self.ax.plot(x_vals, y_vals, color=COLOR_LINE_G_X, label=f"y = {self.engine.g_str}", linewidth=1.5)
        except Exception as e:
            self.log(f"[PLOT ERROR] Could not plot g(x): {e}")
        
        self.ax.legend()
        self.canvas.draw()
        
        # Plot initial point
        self.ax.plot(x0, 0, 'o', color='white', markersize=4)
        self.canvas.draw()

    def on_step(self):
        result = self.engine.step()
        if not result:
            return
        
        if "error" in result and isinstance(result["error"], str):
            self.log(f"[ERROR] {result['error']}")
            return

        step_num = result["step"]
        x_in = result["x_in"]
        x_out = result["x_out"]
        err = result["error"]
        
        self.log(f"[STEP {step_num}] x: {x_in:.4f} -> g(x): {x_out:.4f}")
        self.log(f"         Error: {err:.4f}%")
        
        # Draw Cobweb
        points = result["points"]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        
        self.ax.plot(xs, ys, color=COLOR_COBWEB, linewidth=1, alpha=0.8)
        self.ax.plot(x_out, x_out, 'o', color=COLOR_COBWEB, markersize=3)
        self.canvas.draw()

    def on_run_auto(self):
        try:
            tol = float(self.entry_tol.get())
            max_iter = int(self.entry_max_iter.get())
        except ValueError:
            self.log("[ERROR] Invalid Tolerance or Max Iterations.")
            return

        self.log(f"[AUTO] Running until error < {tol} or iter >= {max_iter}...")
        
        results = self.engine.run_auto(tol, max_iter)
        
        if not results:
            self.log("[AUTO] No results generated.")
            return

        # Switch to Table Tab
        self.tabview.set("Data Table")
        
        # Clear existing table
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Populate Table
        for res in results:
            if "error" in res and isinstance(res["error"], str):
                self.log(f"[AUTO ERROR] {res['error']}")
                break
                
            self.tree.insert("", "end", values=(
                res["step"],
                f"{res['x_in']:.6f}",
                f"{res['x_next'] if 'x_next' in res else res['x_out']:.6f}", # Handle key name mismatch if any
                f"{res['error']:.6f}"
            ))
            
        last_res = results[-1]
        self.log(f"[AUTO] Finished at Step {last_res['step']}. Final Error: {last_res['error']:.6f}%")

    def on_reset(self):
        self.engine.reset()
        self.log("[SYSTEM] Resetting...")
        
        self.entry_g.configure(state="normal")
        self.entry_x0.configure(state="normal")
        self.btn_init.configure(state="normal")
        self.btn_step.configure(state="disabled")
        self.btn_auto.configure(state="disabled")
        
        self.ax.clear()
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.canvas.draw()
        
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        
        for item in self.tree.get_children():
            self.tree.delete(item)

if __name__ == "__main__":
    app = ConvergenceApp()
    app.mainloop()
