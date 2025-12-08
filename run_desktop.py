try:
    import customtkinter as ctk
    import matplotlib.pyplot as plt
except ImportError:
    ctk = None
    plt = None

from convergence_engine import ConvergenceApp

if __name__ == "__main__":
    if ctk:
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")
        plt.style.use('dark_background')
        app = ConvergenceApp()
        app.mainloop()
    else:
        print("CustomTkinter not installed or Tkinter not supported. Cannot run desktop GUI.")
