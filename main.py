import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
from memory_manager import MemoryManager

class PaginationSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Paginación")
        self.root.geometry("1450x400")
        
        self.memory_manager = MemoryManager(total_memory=65536)
        
        self.demo_running = False
        self.demo_paused = False
        self.demo_task = None
        
        self.setup_ui()
        self.update_memory_map()
        self.update_process_list()

    def setup_ui(self):
        # Theme Setup
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        bg_color = "#1E1E1E"
        fg_color = "#E0E0E0"
        accent_color = "#007ACC"
        darker_bg = "#121212"
        panel_bg = "#252526"
        
        self.root.configure(bg=bg_color)
        
        # Configure Styles
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=panel_bg, foreground=fg_color, font=("Segoe UI", 10))
        style.configure("TLabelframe", background=panel_bg, foreground=accent_color, relief="flat")
        style.configure("TLabelframe.Label", background=panel_bg, foreground=accent_color, font=("Segoe UI", 11, "bold"))
        
        style.configure("TButton", background=accent_color, foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0, focuscolor="none")
        style.map("TButton", background=[('active', '#005A9E')])
        
        style.configure("Horizontal.TScale", background=panel_bg, troughcolor=darker_bg, sliderthickness=15)
        
        style.configure("Treeview", background=darker_bg, foreground=fg_color, fieldbackground=darker_bg, font=("Consolas", 10), rowheight=25)
        style.configure("Treeview.Heading", background=panel_bg, foreground=fg_color, font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3E3E42')])
        
        # Main Layout
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel - Controls
        left_panel = ttk.LabelFrame(main_frame, text="CONTROLES", padding="15")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Custom button style for left panel
        btn_style = {"fill": tk.X, "pady": 8}
        
        ttk.Button(left_panel, text="AGREGAR PROCESO", command=self.add_process_dialog).pack(**btn_style)
        ttk.Button(left_panel, text="ELIMINAR PROCESO", command=self.remove_process_dialog).pack(**btn_style)
        ttk.Button(left_panel, text="REINICIAR MEMORIA", command=self.reset_memory).pack(**btn_style)
        
        self.btn_demo = ttk.Button(left_panel, text="INICIAR SIMULACIÓN", command=self.toggle_demo)
        self.btn_demo.pack(**btn_style)
        
        self.btn_pause = ttk.Button(left_panel, text="PAUSAR", command=self.toggle_pause, state=tk.DISABLED)
        self.btn_pause.pack(**btn_style)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Speed Control
        ttk.Label(left_panel, text="VELOCIDAD SIMULACIÓN").pack(anchor=tk.W, pady=(5,5))
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(left_panel, from_=0.1, to=2.0, variable=self.speed_var, orient=tk.HORIZONTAL)
        self.speed_scale.pack(fill=tk.X, pady=5)
        
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        self.stats_label = ttk.Label(left_panel, text="MEMORIA LIBRE: ...", font=("Consolas", 10))
        self.stats_label.pack(anchor=tk.W, pady=2)
        
        self.frag_label = ttk.Label(left_panel, text="FRAGMENTACIÓN: 0 KB", font=("Consolas", 10))
        self.frag_label.pack(anchor=tk.W, pady=2)

        # Center Panel - Memory Map
        center_panel = ttk.LabelFrame(main_frame, text="MAPA DE MEMORIA", padding="10")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.canvas = tk.Canvas(center_panel, bg=darker_bg, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right Panel - Process List
        right_panel = ttk.LabelFrame(main_frame, text="PROCESOS ACTIVOS", padding="10")
        right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        columns = ("PID", "Tamaño", "Páginas")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings")
        self.tree.heading("PID", text="PID")
        self.tree.heading("Tamaño", text="TAMAÑO")
        self.tree.heading("Páginas", text="PÁGINAS")
        self.tree.column("PID", width=60, anchor=tk.CENTER)
        self.tree.column("Tamaño", width=100, anchor=tk.CENTER)
        self.tree.column("Páginas", width=80, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def update_memory_map(self):
        self.canvas.delete("all")
        frames = self.memory_manager.get_memory_status()
        
        # Grid configuration
        cols = 16
        rows = len(frames) // cols
        if len(frames) % cols != 0:
            rows += 1
            
        w = 50
        h = 35
        start_x = 20
        start_y = 20
        
        for i, status in enumerate(frames):
            r = i // cols
            c = i % cols
            
            x1 = start_x + c * w
            y1 = start_y + r * h
            x2 = x1 + w - 2 # Gap
            y2 = y1 + h - 2 # Gap
            
            color = "#2D2D2D" # Empty frame color
            outline = "#3E3E42"
            text = f"{i}"
            text_color = "#666666"
            
            if status == "OS":
                color = "#FF3366" # Neon Pink
                outline = "#FF3366"
                text = "OS"
                text_color = "white"
            elif status is not None:
                # Find process color
                process = self.memory_manager.processes.get(status)
                if process:
                    color = process.color
                    outline = color
                    text = f"P{status}"
                    text_color = "black" # Contrast for bright neon colors
            
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline, width=1)
            self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=text, font=("Consolas", 8), fill=text_color)

        # Update stats
        free_frames = frames.count(None)
        free_mem = free_frames * self.memory_manager.page_size
        self.stats_label.config(text=f"MEMORIA LIBRE: {free_mem} KB")
        
        frag_info = self.memory_manager.get_fragmentation_info()
        self.frag_label.config(text=f"FRAGMENTACIÓN: {frag_info['total_internal_fragmentation']} KB")

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
        
        # Neon color
        import colorsys
        hue = random.random()
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
        color = '#%02X%02X%02X' % (int(r*255), int(g*255), int(b*255))
        
        try:
            self.memory_manager.allocate(pid, size, color)
            self.update_memory_map()
            self.update_process_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_process_dialog(self):
        if not self.memory_manager.processes:
            messagebox.showinfo("Info", "No hay procesos para eliminar.")
            return

        # Custom dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Eliminar Proceso")
        dialog.geometry("300x400")
        
        lbl = ttk.Label(dialog, text="Seleccione un proceso para eliminar:")
        lbl.pack(pady=5)
        
        # Listbox with scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox
        pids = []
        for pid, process in self.memory_manager.processes.items():
            text = f"PID: {pid} | Size: {process.size} KB"
            listbox.insert(tk.END, text)
            listbox.itemconfig(tk.END, {'bg': process.color})
            pids.append(pid)
            
        def on_delete():
            selection = listbox.curselection()
            if not selection:
                return
            
            index = selection[0]
            pid_to_remove = pids[index]
            
            try:
                self.memory_manager.deallocate(pid_to_remove)
                self.update_memory_map()
                self.update_process_list()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        btn = ttk.Button(dialog, text="Eliminar", command=on_delete)
        btn.pack(pady=10)

    def reset_memory(self):
        if self.demo_running:
            self.toggle_demo() # Stop demo if running
            
        self.memory_manager = MemoryManager(total_memory=65536)
        self.update_memory_map()
        self.update_process_list()

    def toggle_demo(self):
        if self.demo_running:
            # Stop
            self.demo_running = False
            self.demo_paused = False
            if self.demo_task:
                self.root.after_cancel(self.demo_task)
                self.demo_task = None
            self.btn_demo.config(text="Iniciar Demo Random")
            self.btn_pause.config(state=tk.DISABLED, text="Pausar")
        else:
            # Start
            self.demo_running = True
            self.demo_paused = False
            self.btn_demo.config(text="Detener")
            self.btn_pause.config(state=tk.NORMAL, text="Pausar")
            self.demo_step()

    def toggle_pause(self):
        if not self.demo_running: return
        
        if self.demo_paused:
            self.demo_paused = False
            self.btn_pause.config(text="Pausar")
            self.demo_step()
        else:
            self.demo_paused = True
            self.btn_pause.config(text="Continuar")
            if self.demo_task:
                self.root.after_cancel(self.demo_task)
                self.demo_task = None

    def demo_step(self):
        if not self.demo_running or self.demo_paused:
            return

        try:
            # 70% chance to add, 30% to remove (if any exist)
            action = "add"
            if self.memory_manager.processes and random.random() < 0.3:
                action = "remove"
            
            if action == "add":
                # Generate random process
                pid = random.randint(100, 999)
                while pid in self.memory_manager.processes:
                    pid = random.randint(100, 999)
                
                size = random.randint(200, 3000)
                # Generate Neon Colors (High Saturation, High Brightness)
                # HSV to RGB conversion simplified:
                # Pick a random hue, high saturation, high value
                import colorsys
                hue = random.random()
                r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
                color = '#%02X%02X%02X' % (int(r*255), int(g*255), int(b*255))
                
                self.memory_manager.allocate(pid, size, color)
            else:
                # Remove random process
                pid = random.choice(list(self.memory_manager.processes.keys()))
                self.memory_manager.deallocate(pid)
                
            self.update_memory_map()
            self.update_process_list()
            
        except Exception as e:
            # Ignore memory errors in demo, just try again later
            pass
            
        # Schedule next step (base delay 1000ms * speed factor)
        # Lower value on slider = Faster (smaller delay)
        # But slider is 0.1 to 2.0. Let's say 1.0 is normal.
        # Actually, usually slider "Speed" means higher is faster.
        # But here I implemented "Delay Multiplier" effectively.
        # Let's invert it for UX: Higher slider = Faster speed = Lower delay.
        # Wait, the plan said "Range: 0.1 (Fast) to 2.0 (Slow)". So it's a "Delay Factor".
        # I'll stick to that.
        
        base_delay = 1000
        delay = int(base_delay * self.speed_var.get())
        self.demo_task = self.root.after(delay, self.demo_step)

def main():
    root = tk.Tk()
    app = PaginationSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
