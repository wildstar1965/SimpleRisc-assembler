'''
This project is made by:
Krishna Teja -- 2401EC29,
J.N. Lohithaswan -- 2401EC44
'''

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from AssemblyToBinaryConverter import Engine 

BG_VOID = "#0F0F1A"          
BG_SURFACE = "#1A1A2E"      
FG_STARLIGHT = "#E0E0E0"    
ACCENT_NEON = "#5AD64C"     
ACCENT_MUTED = "#E23D93"    

class LineNumberedEditor(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, bg=BG_VOID, *args, **kwargs)
        self.text_font = ("Roboto", 15)
        
        self.line_numbers = tk.Text(self, width=4, padx=5, takefocus=0, border=0,
                                    background=BG_VOID, foreground=ACCENT_NEON, 
                                    font=self.text_font, state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.editor = tk.Text(self, wrap=tk.NONE, border=0,
                              background=BG_SURFACE, foreground=FG_STARLIGHT, 
                              insertbackground=ACCENT_NEON, font=self.text_font, undo=True)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.sync_scroll)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=self.sync_scroll_update)
        
        self.editor.bind("<KeyRelease>", self.update_line_numbers)
        self.editor.bind("<MouseWheel>", self.update_line_numbers)
        self.editor.bind("<Configure>", self.update_line_numbers)
        
        self.update_line_numbers()

    def sync_scroll(self, *args):
        self.editor.yview(*args)
        self.line_numbers.yview(*args)
        
    def sync_scroll_update(self, *args):
        self.scrollbar.set(*args)
        self.line_numbers.yview_moveto(args[0])
        
    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        lines = self.editor.get('1.0', tk.END).count('\n')
        line_num_string = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.insert('1.0', line_num_string)
        self.line_numbers.config(state='disabled')
        
    def get(self, *args, **kwargs): return self.editor.get(*args, **kwargs)
    def insert(self, *args, **kwargs): 
        self.editor.insert(*args, **kwargs)
        self.update_line_numbers()
    def delete(self, *args, **kwargs): 
        self.editor.delete(*args, **kwargs)
        self.update_line_numbers()

class AssemblerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RISC Assembler - Orbital Interface")
        self.root.geometry("1100x650")
        self.root.configure(bg=BG_VOID)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TPanedwindow", background=BG_VOID)
        style.configure("Sash", background=ACCENT_MUTED, sashthickness=4)

        # --- Top Control Frame ---
        control_frame = tk.Frame(root, bg=BG_VOID, pady=15)
        control_frame.pack(fill=tk.X)

        btn_style = {"font": ("Arial", 10, "bold"), "fg": BG_VOID, "bg": ACCENT_MUTED, 
                     "activebackground": ACCENT_NEON, "activeforeground": BG_VOID, "relief": tk.FLAT, "cursor": "hand2"}

        tk.Button(control_frame, text="LOAD ASSEMBLY FILE", command=self.load_file, width=20, **btn_style).pack(side=tk.LEFT, padx=15)
        
        # Base Input Field
        tk.Label(control_frame, text="BASE:", font=("Arial", 10, "bold"), bg=BG_VOID, fg=FG_STARLIGHT).pack(side=tk.LEFT, padx=(10, 2))
        self.base_input = tk.Entry(control_frame, width=5, font=("Arial", 11, "bold"), bg=BG_SURFACE, fg=ACCENT_NEON, insertbackground=ACCENT_NEON, borderwidth=0, justify="center")
        self.base_input.insert(0, "10")
        self.base_input.pack(side=tk.LEFT, padx=(0, 15))

        tk.Button(control_frame, text="COMPILE", command=self.compile_code, width=22, 
                  font=("Arial", 10, "bold"), fg=BG_VOID, bg=ACCENT_NEON, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="SAVE HEX FILE", command=self.save_hex, width=15, **btn_style).pack(side=tk.RIGHT, padx=15)

        # --- Split Screen Layout ---
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        self.left_frame = tk.Frame(self.paned_window, bg=BG_VOID)
        tk.Label(self.left_frame, text="> ASSEMBLY_INPUT", font=("Courier", 15, "bold"), bg=BG_VOID, fg=ACCENT_NEON).pack(anchor=tk.W, pady=(0, 5))
        self.asm_editor = LineNumberedEditor(self.left_frame)
        self.asm_editor.pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(self.left_frame, weight=1)

        self.right_frame = tk.Frame(self.paned_window, bg=BG_VOID)
        tk.Label(self.right_frame, text="> BINARY_OUTPUT", font=("Courier", 15, "bold"), bg=BG_VOID, fg=ACCENT_MUTED).pack(anchor=tk.W, pady=(0, 5))
        
        self.hex_viewer = tk.Text(self.right_frame, wrap=tk.NONE, font=("Consolas", 12), 
                                  background=BG_SURFACE, foreground=ACCENT_NEON, border=0)
        self.hex_viewer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        hex_scroll = tk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.hex_viewer.yview)
        hex_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.hex_viewer.config(yscrollcommand=hex_scroll.set, state=tk.DISABLED)
        
        self.paned_window.add(self.right_frame, weight=1)

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Assembly Files", "*.asm *.txt"), ("All Files", "*.*")])
        if not filepath: return
        with open(filepath, 'r') as file:
            content = file.read()
        self.asm_editor.delete('1.0', tk.END)
        self.asm_editor.insert('1.0', content)

    def save_hex(self):
        self.hex_viewer.config(state=tk.NORMAL)
        hex_content = self.hex_viewer.get('1.0', tk.END).strip()
        self.hex_viewer.config(state=tk.DISABLED)
        
        if not hex_content:
            messagebox.showwarning("Warning", "No compiled binary to save.")
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("Hex Files", "*.hex")])
        if not filepath: return
        with open(filepath, 'w') as file:
            file.write(hex_content)

    def compile_code(self):
        # 1. Base Validation
        try:
            target_base = int(self.base_input.get().strip())
            if target_base <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Parameter", "Base must be a valid integer greater than 0.")
            return

        # 2. Extract Code
        asm_code = self.asm_editor.get('1.0', tk.END).strip()
        if not asm_code:
            messagebox.showerror("Fault", "Assembly editor is empty.")
            return

        temp_asm = "temp_asm.txt"
        temp_hex = "temp_hex.txt"
        
        with open(temp_asm, 'w') as f:
            f.write(asm_code)

        try:
            # 3. Execution (Injecting the dynamic base)
            engine = Engine(assemblyFileName=temp_asm, hexFileName=temp_hex, baseUsed=target_base)
            engine.run()

            # 4. Display output
            with open(temp_hex, 'r') as f:
                hex_output = f.read()

            self.hex_viewer.config(state=tk.NORMAL)
            self.hex_viewer.delete('1.0', tk.END)
            self.hex_viewer.insert('1.0', hex_output)
            self.hex_viewer.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Compilation/System Error", str(e))
        finally:
            for file in [temp_asm, temp_hex, 'processedAssembly.txt']:
                if os.path.exists(file): os.remove(file)

if __name__ == "__main__":
    root = tk.Tk()
    app = AssemblerGUI(root)
    root.mainloop()

