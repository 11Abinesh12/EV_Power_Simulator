import tkinter as tk
from tkinter import ttk, messagebox

class SimulationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulation Control Panel")
        self.geometry("700x400")

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Tabs
        self.create_home_tab()
        self.create_simulation_tab()

    def create_home_tab(self):
        self.home_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.home_tab, text="⚙️ Parameters")

        # Default parameters (can later come from Excel)
        self.defaults = {
            "IP Address": "192.168.1.10",
            "Target RPM": "1500",
            "Voltage": "24V",
            "Current Limit": "10A",
            "Firmware Version": "v1.2.3",
        }

        ttk.Label(self.home_tab, text="Simulation Parameters", font=("Segoe UI", 12, "bold")).pack(pady=10)

        # Frame for entries
        self.param_frame = ttk.Frame(self.home_tab)
        self.param_frame.pack(pady=10)

        self.entries = {}
        for i, (key, val) in enumerate(self.defaults.items()):
            ttk.Label(self.param_frame, text=f"{key}:").grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(self.param_frame, width=30)
            entry.insert(0, val)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[key] = entry

        # Button to run simulation
        ttk.Button(self.home_tab, text="▶ Run Simulation", command=self.run_simulation).pack(pady=20)

    def create_simulation_tab(self):
        self.sim_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sim_tab, text="📊 Simulation Output")

        ttk.Label(self.sim_tab, text="Simulation Output Log", font=("Segoe UI", 12, "bold")).pack(pady=10)

        self.output_text = tk.Text(self.sim_tab, height=15, wrap="word")
        self.output_text.pack(fill="both", expand=True, padx=20, pady=10)

    def run_simulation(self):
        # Read user values
        params = {k: e.get() for k, e in self.entries.items()}

        # Simulated log output
        log = "\n--- Running Simulation ---\n"
        for k, v in params.items():
            log += f"{k}: {v}\n"
        log += "\n✅ Simulation completed successfully!"

        # Display log
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, log)

        # Switch to output tab
        self.notebook.select(self.sim_tab)

# Run app
if __name__ == "__main__":
    app = SimulationApp()
    app.mainloop()
