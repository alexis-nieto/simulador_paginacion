import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
from memory_manager import MemoryManager

class PaginationSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Paginación")
        self.root.geometry("1200x800")
        
        self.memory_manager = MemoryManager(total_memory=16384)
        
        self.setup_ui()
        self.update_memory_map()
        self.update_process_list()

    def setup_ui(self):
        # Main Layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel - Controls
        left_panel = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Button(left_panel, text="Agregar Proceso", command=self.add_process_dialog).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Eliminar Proceso", command=self.remove_process_dialog).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Reiniciar Memoria", command=self.reset_memory).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Demo Automático", command=self.run_demo).pack(fill=tk.X, pady=5)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        self.stats_label = ttk.Label(left_panel, text="Memoria Libre: ...")
        self.stats_label.pack(anchor=tk.W)
        
        self.frag_label = ttk.Label(left_panel, text="Fragmentación Interna: 0 KB")
        self.frag_label.pack(anchor=tk.W)

        # Center Panel - Memory Map
        center_panel = ttk.LabelFrame(main_frame, text="Mapa de Memoria Física", padding="10")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.canvas = tk.Canvas(center_panel, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right Panel - Process List
        right_panel = ttk.LabelFrame(main_frame, text="Tabla de Procesos", padding="10")
        right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        columns = ("PID", "Tamaño", "Páginas")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings")
        self.tree.heading("PID", text="PID")
        self.tree.heading("Tamaño", text="Tamaño (KB)")
        self.tree.heading("Páginas", text="Páginas")
        self.tree.column("PID", width=50)
        self.tree.column("Tamaño", width=80)
        self.tree.column("Páginas", width=60)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def update_memory_map(self):
        self.canvas.delete("all")
        frames = self.memory_manager.get_memory_status()
        
        # Grid configuration
        cols = 8
        rows = len(frames) // cols
        if len(frames) % cols != 0:
            rows += 1
            
        w = 60
        h = 40
        start_x = 20
        start_y = 20
        
        for i, status in enumerate(frames):
            r = i // cols
            c = i % cols
            
            x1 = start_x + c * w
            y1 = start_y + r * h
            x2 = x1 + w
            y2 = y1 + h
            
            color = "white"
            text = f"F{i}"
            
            if status == "OS":
                color = "gray"
                text += "\nOS"
            elif status is not None:
                # Find process color
                process = self.memory_manager.processes.get(status)
                if process:
                    color = process.color
                    text += f"\nP{status}"
            
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=text, font=("Arial", 8))

        # Update stats
        free_frames = frames.count(None)
        free_mem = free_frames * self.memory_manager.page_size
        self.stats_label.config(text=f"Memoria Libre: {free_mem} KB")
        
        frag_info = self.memory_manager.get_fragmentation_info()
        self.frag_label.config(text=f"Fragmentación Interna: {frag_info['total_internal_fragmentation']} KB")

    def update_process_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for pid, process in self.memory_manager.processes.items():
            self.tree.insert("", tk.END, values=(pid, f"{process.size} KB", len(process.pages)))

    def add_process_dialog(self):
        pid = simpledialog.askinteger("Nuevo Proceso", "Ingrese ID del Proceso:")
        if pid is None: return
        
        size = simpledialog.askinteger("Nuevo Proceso", "Ingrese Tamaño (KB):")
        if size is None: return
        
        # Random pastel color
        r = lambda: random.randint(128, 255)
        color = '#%02X%02X%02X' % (r(),r(),r())
        
        try:
            self.memory_manager.allocate(pid, size, color)
            self.update_memory_map()
            self.update_process_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_process_dialog(self):
        pid = simpledialog.askinteger("Eliminar Proceso", "Ingrese ID del Proceso a eliminar:")
        if pid is None: return
        
        try:
            self.memory_manager.deallocate(pid)
            self.update_memory_map()
            self.update_process_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset_memory(self):
        self.memory_manager = MemoryManager(total_memory=16384)
        self.update_memory_map()
        self.update_process_list()

    def run_demo(self):
        self.reset_memory()
        
        # Sequence of actions
        steps = [
            (1000, lambda: self.memory_manager.allocate(101, 2000, "#FFB3BA")), # P1 (Pink)
            (2000, lambda: self.memory_manager.allocate(102, 3000, "#BAFFC9")), # P2 (Green)
            (3000, lambda: self.memory_manager.allocate(103, 1500, "#BAE1FF")), # P3 (Blue)
            (4000, lambda: self.memory_manager.allocate(104, 2500, "#FFFFBA")), # P4 (Yellow)
            (5000, lambda: self.memory_manager.deallocate(102)), # Remove P2
            (6000, lambda: self.memory_manager.allocate(105, 1000, "#E2BAFF")), # P5 (Purple)
            (7000, lambda: self.memory_manager.allocate(106, 1800, "#FFDFBA")), # P6 (Orange)
            (8000, lambda: self.memory_manager.deallocate(101)), # Remove P1
            (9000, lambda: self.memory_manager.deallocate(104)), # Remove P4
            (10000, lambda: self.memory_manager.allocate(107, 4000, "#BAFFFF")), # P7 (Cyan)
        ]
        
        for delay, action in steps:
            def step_wrapper(act=action):
                try:
                    act()
                    self.update_memory_map()
                    self.update_process_list()
                except Exception as e:
                    print(f"Demo Error: {e}")
            
            self.root.after(delay, step_wrapper)

def main():
    root = tk.Tk()
    app = PaginationSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
