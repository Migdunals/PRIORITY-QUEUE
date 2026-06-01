import tkinter as tk
from tkinter import messagebox, simpledialog
import math
import random

class HeapUI(tk.Frame):
    def __init__(self, master, on_switch_callback, on_delete_callback):
        super().__init__(master, bg="#0B2439")
        self.on_switch_callback = on_switch_callback
        self.on_delete_callback = on_delete_callback
        self.node_radius = 24
        self.positions = {} 
        self.current_type = "min" 
        
        self.hovered_idx = None
        self.is_animating = False

        tk.Label(self, text="PRIORITY QUEUE VISUALIZER", font=("Segoe UI", 16, "bold"), bg="#0B2439",fg="white").pack(pady=(20, 5))
        
        self.status_label = tk.Label(self, text="Current Logic: Min Heap", font=("Segoe UI", 12, "italic"), bg="#0B2439", fg="#E2C752")
        self.status_label.pack(pady=(0, 10))

        self.canvas = tk.Canvas(self, bg="#293B5E", highlightthickness=5, highlightbackground="#000000")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_canvas_leave)
        
        tk.Label(self, text="💡 Tip: Double-click a node to delete it.", font=("Segoe UI", 10, "bold"), bg="#0B2439", fg="#E2C752").pack(pady=(5, 0))

        controls = tk.Frame(self, bg="#0B2439")
        controls.pack(anchor="w", padx=20, pady=20) 
        
        btn_row = tk.Frame(controls, bg="#0B2439")
        btn_row.pack(anchor="w", pady=(0, 8))
        
        tk.Button(btn_row, text="Generate", command=self.generate_numbers, bg="#28A745", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=8, activebackground="#1E7E34", activeforeground="white", cursor="hand2").pack(side=tk.LEFT, padx=(5, 10))
        tk.Button(btn_row, text="Min Heap", command=lambda: self.submit("min"), bg="#897306", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=8, activebackground="#4D4103", activeforeground="white", cursor="hand2" ).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_row, text="Max Heap", command=lambda: self.submit("max"), bg="#506EE8", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=8, activebackground="#39498A", activeforeground="white", cursor="hand2" ).pack(side=tk.LEFT, padx=10)
        
        input_row = tk.Frame(controls, bg="#0B2439")
        input_row.pack(anchor="w")
        
        self.input_entry = tk.Entry(input_row, width=80, font=("Segoe UI", 12), bg="#FFFFFF", fg="#333333", relief="flat", highlightthickness=2, highlightbackground="#CCCCCC", highlightcolor="#007ACC", insertbackground="#333333")
        self.input_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.setup_speed_slider(input_row)

    def setup_speed_slider(self, parent_frame):
        slider_frame = tk.Frame(parent_frame, bg="#0B2439")
        slider_frame.pack(side=tk.LEFT, padx=(20, 5))
        
        tk.Label(slider_frame, text="Speed:", font=("Segoe UI", 12, "bold"), bg="#0B2439", fg="white").pack(side=tk.LEFT, padx=2, pady=(15, 0))
        
        self.speed_slider = tk.Scale(
            slider_frame, 
            from_=1, 
            to=20,              
            orient=tk.HORIZONTAL, 
            bg="#0B2439", 
            fg="white", 
            troughcolor="#293B5E", 
            highlightthickness=0,
            activebackground="#506EE8",
            length=180,         
            width=13,           
            sliderlength=18,    
            showvalue=True      
        )
        self.speed_slider.set(5)  
        self.speed_slider.pack(side=tk.LEFT, padx=2)

    def update_status(self, heap_type):
        self.current_type = heap_type
        if heap_type == "min":
            color = "#E2C752" 
            self.status_label.config(text="Current Logic: Min Heap", fg=color)
        elif heap_type == "max":
            color = "#839BFF" 
            self.status_label.config(text="Current Logic: Max Heap", fg=color)
        else:
            return

        for item in self.canvas.find_all():
            if self.canvas.type(item) == "oval":
                self.canvas.itemconfig(item, fill=color)

    def calculate_positions(self, n):
        self.canvas.update()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        levels = math.ceil(math.log2(n + 1)) if n > 0 else 1
        self.positions = {}
        
        for i in range(n):
            level = int(math.log2(i + 1))
            num_nodes_in_level = 2**level
            x_interval = w / (num_nodes_in_level + 1)
            idx_in_level = i - (2**level - 1)
            
            x = x_interval * (idx_in_level + 1)
            y = 60 + level * (h / (levels + 1))
            self.positions[i] = (x, y)

    def draw_tree(self, arr):
        self.canvas.delete("all")
        self.hovered_idx = None
        self.is_animating = False
        
        n = len(arr)
        self.calculate_positions(n)

        node_color = "#839BFF" if self.current_type == "max" else "#9A8218"

        for i in range(n):
            l, r = 2*i + 1, 2*i + 2
            if l < n: self.canvas.create_line(self.positions[i], self.positions[l], fill="#FFFFFF", width=2, tags=f"line{l}")
            if r < n: self.canvas.create_line(self.positions[i], self.positions[r], fill="#FFFFFF", width=2, tags=f"line{r}")

        for i in range(n):
            x, y = self.positions[i]
            r = self.node_radius
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=node_color, outline="", tags=f"node{i}")
            self.canvas.create_text(x, y, text=str(arr[i]), fill="white", font=("Helvetica", 10, "bold"), tags=f"text{i}", state="disabled")

    def on_mouse_move(self, event):
        if self.is_animating or not self.positions: 
            return
            
        mx, my = event.x, event.y
        closest_idx = None
        hover_threshold = self.node_radius + 2
        
        for idx, (nx, ny) in self.positions.items():
            dist = math.sqrt((mx - nx)**2 + (my - ny)**2)
            if dist <= hover_threshold:
                closest_idx = idx
                break
                
        if closest_idx != self.hovered_idx:
            if self.hovered_idx is not None:
                self.unhighlight_node(self.hovered_idx)
            if closest_idx is not None:
                self.highlight_node(closest_idx)
            self.hovered_idx = closest_idx

    def on_canvas_leave(self, event):
        if self.hovered_idx is not None:
            self.unhighlight_node(self.hovered_idx)
            self.hovered_idx = None

    def highlight_node(self, idx):
        if idx not in self.positions: return
        x, y = self.positions[idx]
        r = self.node_radius + 4  
        
        self.canvas.coords(f"node{idx}", x-r, y-r, x+r, y+r)
        self.canvas.itemconfig(f"node{idx}", outline="#FFFFFF", width=3)  
        self.canvas.itemconfig(f"text{idx}", font=("Helvetica", 11, "bold"))

    def unhighlight_node(self, idx):
        if idx not in self.positions: return
        x, y = self.positions[idx]
        r = self.node_radius
        
        self.canvas.coords(f"node{idx}", x-r, y-r, x+r, y+r)
        self.canvas.itemconfig(f"node{idx}", outline="", width=1)
        self.canvas.itemconfig(f"text{idx}", font=("Helvetica", 10, "bold"))

    def animate_move(self, from_idx, to_idx, callback):
        self.is_animating = True
        self.canvas.delete(f"line{from_idx}")
        
        pos1 = self.positions.get(from_idx)
        pos2 = self.positions.get(to_idx)
        
        if not pos1 or not pos2:
            callback()
            return
            
        steps = 40 
        dx = (pos2[0] - pos1[0]) / steps
        dy = (pos2[1] - pos1[1]) / steps

        def step(count):
            if count < steps:
                self.canvas.move(f"node{from_idx}", dx, dy)
                self.canvas.move(f"text{from_idx}", dx, dy)
                
                delay = int(100 / self.speed_slider.get())
                self.after(delay, lambda: step(count + 1))
            else:
                self.canvas.itemconfig(f"node{from_idx}", tags=(f"node{to_idx}",))
                self.canvas.itemconfig(f"text{from_idx}", tags=(f"text{to_idx}",))
                
                tx, ty = self.positions[to_idx]
                r = self.node_radius
                self.canvas.coords(f"node{to_idx}", tx-r, ty-r, tx+r, ty+r)
                self.canvas.coords(f"text{to_idx}", tx, ty)
                
                callback()

        step(0)

    def animate_swap(self, idx1, idx2, val1, val2, callback):
        if self.hovered_idx is not None:
            self.unhighlight_node(self.hovered_idx)
            self.hovered_idx = None
            
        self.is_animating = True
        pos1 = self.positions.get(idx1)
        pos2 = self.positions.get(idx2)
        
        if not pos1 or not pos2:
            callback()
            return
        
        steps = 40 
        dx = (pos2[0] - pos1[0]) / steps
        dy = (pos2[1] - pos1[1]) / steps

        def step(count):
            if count < steps:
                self.canvas.move(f"node{idx1}", dx, dy)
                self.canvas.move(f"text{idx1}", dx, dy)
                self.canvas.move(f"node{idx2}", -dx, -dy)
                self.canvas.move(f"text{idx2}", -dx, -dy)
                
                delay = int(100 / self.speed_slider.get())
                self.after(delay, lambda: step(count + 1))
            else:
                self.canvas.itemconfig(f"node{idx1}", tags=("temp",))
                self.canvas.itemconfig(f"node{idx2}", tags=(f"node{idx1}",))
                self.canvas.itemconfig("temp", tags=(f"node{idx2}",))
                
                self.canvas.itemconfig(f"text{idx1}", tags=("temp_t",))
                self.canvas.itemconfig(f"text{idx2}", tags=(f"text{idx1}",))
                self.canvas.itemconfig("temp_t", tags=(f"text{idx2}",))
                
                x1, y1 = self.positions[idx1]
                x2, y2 = self.positions[idx2]
                r = self.node_radius
                
                self.canvas.coords(f"node{idx1}", x1-r, y1-r, x1+r, y1+r)
                self.canvas.coords(f"text{idx1}", x1, y1)
                
                self.canvas.coords(f"node{idx2}", x2-r, y2-r, x2+r, y2+r)
                self.canvas.coords(f"text{idx2}", x2, y2)
                
                callback()

        step(0)

    def animate_fade(self, idx, callback):
        self.is_animating = True
        self.canvas.delete(f"line{idx}")
        self.canvas.delete(f"line{2*idx + 1}")
        self.canvas.delete(f"line{2*idx + 2}")
        
        bg_r, bg_g, bg_b = 41, 59, 94 
        
        current_color = self.canvas.itemcget(f"node{idx}", "fill")
        if not current_color: current_color = "#839BFF"
            
        try:
            curr_r = int(current_color[1:3], 16)
            curr_g = int(current_color[3:5], 16)
            curr_b = int(current_color[5:7], 16)
        except:
            curr_r, curr_g, curr_b = 131, 155, 255 
            
        steps = 12
        coords = self.canvas.coords(f"node{idx}")
        if not coords:
            callback()
            return
            
        x1, y1, x2, y2 = coords
        cx, cy = (x1+x2)/2, (y1+y2)/2
        current_radius = (x2-x1)/2
        r_step = current_radius / steps

        def step(count):
            if count <= steps:
                progress = count / steps
                nr = int(curr_r + (bg_r - curr_r) * progress)
                ng = int(curr_g + (bg_g - curr_g) * progress)
                nb = int(curr_b + (bg_b - curr_b) * progress)
                new_color = f"#{nr:02x}{ng:02x}{nb:02x}"
                
                new_radius = max(1, current_radius - (r_step * count))
                
                self.canvas.coords(f"node{idx}", cx-new_radius, cy-new_radius, cx+new_radius, cy+new_radius)
                self.canvas.itemconfig(f"node{idx}", fill=new_color, outline="")
                
                if count == steps // 3:
                    self.canvas.delete(f"text{idx}")
                    
                delay = int(150 / self.speed_slider.get())
                self.after(delay, lambda: step(count + 1))
            else:
                self.canvas.delete(f"node{idx}")
                callback()

        step(0)

    def submit(self, heap_type):
        raw = self.input_entry.get()
        try:
            values = [int(x.strip()) for x in raw.split(",") if x.strip()]
            if not values:
                messagebox.showwarning("Warning", "Please enter some numbers first!")
                return
            self.on_switch_callback(raw, values, heap_type)
        except ValueError:
            messagebox.showerror("Input Error", "Please ensure your input is numbers separated by commas.\nExample: 15, 3, 22, 8")
        except Exception as e:
            messagebox.showerror("System Error", f"A code error occurred:\n{e}")

    def generate_numbers(self):
        count = random.randint(1, 15)
        numbers = [str(random.randint(1, 1000)) for _ in range(count)]
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, ", ".join(numbers))

    def on_double_click(self, event):
        item = self.canvas.find_withtag("current")
        if not item: return
        
        tags = self.canvas.gettags(item[0])
        for tag in tags:
            if tag.startswith("node") or tag.startswith("text"):
                try:
                    idx = int(tag.replace("node", "").replace("text", ""))
                    self.on_delete_callback(idx)
                except ValueError:
                    pass
                break