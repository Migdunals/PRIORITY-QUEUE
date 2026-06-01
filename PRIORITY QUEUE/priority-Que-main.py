import tkinter as tk
from heap import Heap
from gui_components import HeapUI

class PriorityQueueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Priority Queue Visualizer")
        self.root.geometry("1000x700")
        
        self.heap_logic = Heap()
        self.last_input = ""
        self.ui = HeapUI(self.root, self.handle_submission, self.handle_deletion)
        self.ui.pack(fill=tk.BOTH, expand=True)
        self.animating = False

    def handle_submission(self, raw, values, h_type):
        if self.animating: return
        
        self.ui.update_status(h_type)
        
        if raw != self.last_input or not self.heap_logic.arr:
            self.last_input = raw
            self.heap_logic.type = h_type
            self.heap_logic.build_heap_instant(values)
            self.ui.draw_tree(self.heap_logic.arr)
        elif self.heap_logic.type != h_type:
            self.animate_logic_switch(h_type)

    def animate_logic_switch(self, new_type):
        self.animating = True
        gen = self.heap_logic.convert_heap_gen(new_type)

        def next_step():
            try:
                idx1, idx2 = next(gen)
                v1, v2 = self.heap_logic.arr[idx1], self.heap_logic.arr[idx2]
                self.ui.animate_swap(idx1, idx2, v1, v2, next_step)
            except StopIteration:
                self.animating = False
                self.ui.draw_tree(self.heap_logic.arr) 

        next_step()

    def handle_deletion(self, index):
        if self.animating: return
        if index >= len(self.heap_logic.arr): return
        
        self.animating = True
        gen = self.heap_logic.delete_node_gen(index)

        def next_step():
            try:
                step_data = next(gen)
                
                if isinstance(step_data, tuple):
                    if step_data[0] == "fade":
                        self.ui.animate_fade(step_data[1], next_step)
                    
                    elif step_data[0] == "move":
                        self.ui.animate_move(step_data[1], step_data[2], next_step)
                    
                    else: 
                        idx1, idx2 = step_data
                        v1 = self.heap_logic.arr[idx1]
                        v2 = self.heap_logic.arr[idx2]
                        self.ui.animate_swap(idx1, idx2, v1, v2, next_step)
                        
            except StopIteration:
                self.animating = False
                self.ui.draw_tree(self.heap_logic.arr)

        next_step()

if __name__ == "__main__":
    root = tk.Tk()
    app = PriorityQueueApp(root)
    root.mainloop()