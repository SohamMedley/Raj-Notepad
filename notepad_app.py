import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import json
import os

class AutoCorrect:
    def __init__(self, custom_dict_path=None):
        self.corrections = self.load_corrections(custom_dict_path)

    def load_corrections(self, path=None):
        default_corrections = {
            "hellow": "hello",
            "teh": "the",
            "adn": "and",
            "mu": "my",
            "namu": "name",
            "iimprove": "improve"
        }
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print("Error loading custom dictionary:", e)
        return default_corrections

    def correct_text(self, text):
        def replacer(match):
            word = match.group(0)
            lower_word = word.lower()
            if lower_word in self.corrections:
                corrected = self.corrections[lower_word]
                if word[0].isupper():
                    corrected = corrected.capitalize()
                return corrected
            return word
        return re.sub(r'\b\w+\b', replacer, text)


class NotepadApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📝 Autocorrect Notepad")
        self.geometry("900x600")
        self.configure(bg="#f5f5f5")
        self.current_file = None

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 10), padding=6)
        self.style.configure("TFrame", background="#f5f5f5")
        
        self.create_widgets()
        self.autocorrect = AutoCorrect()
        self.autocorrect_enabled = True
        self.full_text_timer = None

    def create_widgets(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="🆕 New", command=self.new_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="📂 Open", command=self.open_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="💾 Save", command=self.save_file).pack(side=tk.LEFT, padx=4)

        # Autocorrect toggle
        self.ac_label = ttk.Label(toolbar, text="✅ Autocorrect ON", foreground="green")
        self.ac_label.pack(side=tk.RIGHT, padx=10)
        self.ac_label.bind("<Button-1>", self.toggle_autocorrect)

        # Text Editor
        self.text_widget = tk.Text(self, wrap="word", undo=True, font=("Segoe UI", 13), bg="white", relief=tk.FLAT)
        self.text_widget.pack(expand=True, fill="both", padx=10, pady=5)

        self.text_widget.bind("<KeyRelease>", self.on_key_release)

    def on_key_release(self, event=None):
        if self.full_text_timer is not None:
            self.after_cancel(self.full_text_timer)
        self.full_text_timer = self.after(1000, self.full_autocorrect)

    def full_autocorrect(self):
        if not self.autocorrect_enabled:
            return
        cursor_index = self.text_widget.index(tk.INSERT)
        text = self.text_widget.get("1.0", tk.END)
        corrected_text = self.autocorrect.correct_text(text)
        if corrected_text != text:
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", corrected_text)
            try:
                self.text_widget.mark_set(tk.INSERT, cursor_index)
            except Exception:
                pass

    def toggle_autocorrect(self, event=None):
        self.autocorrect_enabled = not self.autocorrect_enabled
        if self.autocorrect_enabled:
            self.ac_label.config(text="✅ Autocorrect ON", foreground="green")
        else:
            self.ac_label.config(text="❌ Autocorrect OFF", foreground="red")

    def new_file(self):
        if self.confirm_discard_changes():
            self.text_widget.delete("1.0", tk.END)
            self.current_file = None
            self.title("📝 Autocorrect Notepad")

    def open_file(self):
        if not self.confirm_discard_changes():
            return
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert("1.0", content)
                self.current_file = file_path
                self.title(f"📝 {os.path.basename(file_path)} - Autocorrect Notepad")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_file(self):
        if self.current_file:
            self._save_to_path(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self._save_to_path(file_path)

    def _save_to_path(self, path):
        try:
            content = self.text_widget.get("1.0", tk.END)
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
            self.title(f"📝 {os.path.basename(path)} - Autocorrect Notepad")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def confirm_discard_changes(self):
        return messagebox.askyesno("Confirm", "Any unsaved changes will be lost. Continue?")

if __name__ == "__main__":
    app = NotepadApp()
    app.mainloop()
