def textlite():
    import tkinter as tk
    from tkinter import filedialog, messagebox, font, colorchooser

    class FontPicker(tk.Toplevel):
        def __init__(self, parent, current_font_family, current_font_size, apply_font_callback):
            super().__init__(parent)
            self.title("Font")
            self.geometry("350x360")
            self.resizable(False, False)

            self.apply_font_callback = apply_font_callback
            self.current_font_family = current_font_family
            self.current_font_size = current_font_size

            tk.Label(self, text="Font:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            self.font_listbox = tk.Listbox(self, height=10, exportselection=False)
            self.font_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

            available_fonts = sorted(font.families())
            for f in available_fonts:
                self.font_listbox.insert(tk.END, f)

            if self.current_font_family in available_fonts:
                self.font_listbox.selection_set(available_fonts.index(self.current_font_family))

            self.font_listbox.bind("<<ListboxSelect>>", lambda event: self.update_sample())

            tk.Label(self, text="Size:").grid(row=0, column=1, padx=10, pady=5, sticky="w")
            self.size_listbox = tk.Listbox(self, height=10, exportselection=False)
            self.size_listbox.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

            available_sizes = list(range(8, 33, 2))
            for size in available_sizes:
                self.size_listbox.insert(tk.END, size)

            if self.current_font_size in available_sizes:
                self.size_listbox.selection_set(available_sizes.index(self.current_font_size))

            self.size_listbox.bind("<<ListboxSelect>>", lambda event: self.update_sample())

            self.sample_text = tk.Label(self, text="AaBbZz", font=(self.current_font_family, self.current_font_size))
            self.sample_text.grid(row=2, column=0, columnspan=2, pady=10)

            tk.Button(self, text="Apply", command=self.apply_font).grid(row=3, column=0, columnspan=2, pady=10)

        def update_sample(self):
            selected_font = self.get_selected_font()
            selected_size = self.get_selected_size()
            self.sample_text.config(font=(selected_font, selected_size))

        def apply_font(self):
            selected_font = self.get_selected_font()
            selected_size = self.get_selected_size()
            self.apply_font_callback(selected_font, selected_size)
            self.destroy()

        def get_selected_font(self):
            selection = self.font_listbox.curselection()
            return self.font_listbox.get(selection[0]) if selection else self.current_font_family

        def get_selected_size(self):
            selection = self.size_listbox.curselection()
            return int(self.size_listbox.get(selection[0])) if selection else self.current_font_size

    class TextEditor:
        def __init__(self, root):
            self.root = root
            self.root.title("Untitled - TextLite")
            self.root.geometry("800x600")
            self.current_file = None
            self.unsaved_changes = False
            self.dark_mode = False
            self.ui_font = ("Segoe UI", 9)
            self.status_font = ("Segoe UI", 9)

            self.current_font_family = "Consolas"
            self.current_font_size = 11
            self.current_font_colour = "black"

            self.scrollbar = tk.Scrollbar(root)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.text_area = tk.Text(root, font=(self.current_font_family, self.current_font_size), wrap=tk.WORD,
                                     undo=True, yscrollcommand=self.scrollbar.set)
            self.text_area.pack(fill=tk.BOTH, expand=True)
            self.scrollbar.config(command=self.text_area.yview)
            self.text_area.bind("<<Modified>>", self.on_change)
            self.text_area.bind("<KeyRelease>", self.update_status_bar)

            self.status_bar = tk.Label(
                root,
                text=" " * 291 + "|   Ln 1, Col 1          | 100%    | Windows (CRLF)    | UTF-8            ",
                anchor="w",
                font=self.status_font)
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

            menubar = tk.Menu(root)
            self.root.config(menu=menubar)

            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
            filemenu.add_command(label="Open", accelerator="Ctrl+O", command=self.open_file)
            filemenu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
            filemenu.add_command(label="Save As...", command=self.save_as_file)
            filemenu.add_separator()
            filemenu.add_command(label="Exit", command=self.exit_editor)
            menubar.add_cascade(label="File", menu=filemenu)

            editmenu = tk.Menu(menubar, tearoff=0)
            editmenu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
            editmenu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
            editmenu.add_separator()
            editmenu.add_command(label="Cut", accelerator="Ctrl+X", command=self.cut)
            editmenu.add_command(label="Copy", accelerator="Ctrl+C", command=self.copy)
            editmenu.add_command(label="Paste", accelerator="Ctrl+V", command=self.paste)
            editmenu.add_command(label="Delete", command=self.delete)
            editmenu.add_separator()
            editmenu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)
            menubar.add_cascade(label="Edit", menu=editmenu)

            formatmenu = tk.Menu(menubar, tearoff=0)
            formatmenu.add_command(label="Word Wrap", command=self.toggle_word_wrap)
            formatmenu.add_command(label="Font", command=self.choose_font)
            formatmenu.add_command(label="Font Colour", command=self.choose_font_colour)
            menubar.add_cascade(label="Format", menu=formatmenu)

            viewmenu = tk.Menu(menubar, tearoff=0)
            viewmenu.add_command(label="Zoom In", command=self.zoom_in)
            viewmenu.add_command(label="Zoom Out", command=self.zoom_out)
            viewmenu.add_command(label="Dark / Light Mode", command=self.toggle_dark_mode)
            menubar.add_cascade(label="View", menu=viewmenu)

            helpmenu = tk.Menu(menubar, tearoff=0)
            helpmenu.add_command(label="About", command=self.show_about)
            helpmenu.add_command(label="License", command=self.show_license)
            helpmenu.add_command(label="Disclaimer", command=self.show_disclaimer)
            helpmenu.add_command(label="Copyright", command=self.show_copyright)
            helpmenu.add_command(label="Credits", command=self.show_credits)
            helpmenu.add_command(label="Readme", command=self.open_readme)
            menubar.add_cascade(label="Help", menu=helpmenu)

            self.root.bind('<Control-n>', lambda event: self.new_file())
            self.root.bind('<Control-o>', lambda event: self.open_file())
            self.root.bind('<Control-s>', lambda event: self.save_file())
            self.root.bind('<Control-a>', lambda event: self.select_all())
            self.root.bind('<Control-z>', lambda event: self.undo())
            self.root.bind('<Control-y>', lambda event: self.redo())
            self.root.bind('<Control-x>', lambda event: self.cut())
            self.root.bind('<Control-c>', lambda event: self.copy())
            self.root.bind('<Control-v>', lambda event: self.paste())
            self.root.bind('<Control-d>', lambda event: self.toggle_dark_mode())

        def new_file(self):
            if self.unsaved_changes:
                discard = self.confirm_discard_changes()
                if not discard:
                    return
            self.text_area.delete(1.0, tk.END)
            self.current_file = None
            self.unsaved_changes = False
            self.root.title("Untitled - TextLite")
            self.update_status_bar()
            self.text_area.edit_modified(False)

        def open_file(self):
            if not self.confirm_discard_changes():
                return
            file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                   filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        self.text_area.delete(1.0, tk.END)
                        self.text_area.insert(1.0, file.read())
                    self.current_file = file_path
                    self.unsaved_changes = False
                    self.root.title(f"TextLite - {file_path}")
                    self.update_status_bar()
                    self.text_area.edit_modified(False)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file:\n{e}")

        def save_file(self):
            if self.current_file:
                try:
                    with open(self.current_file, 'w', encoding='utf-8') as file:
                        text = self.text_area.get(1.0, 'end-1c')
                        file.write(text)
                    self.unsaved_changes = False
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file:\n{e}")
            else:
                self.save_as_file()

        def save_as_file(self):
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        text = self.text_area.get(1.0, 'end-1c')
                        file.write(text)
                    self.current_file = file_path
                    self.unsaved_changes = False
                    self.root.title(f"TextLite - {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file:\n{e}")

        def on_change(self, event=None):
            self.unsaved_changes = self.text_area.edit_modified()
            self.text_area.edit_modified(False)
            self.update_status_bar()

        def confirm_discard_changes(self):
            if self.unsaved_changes:
                result = messagebox.askyesnocancel(
                    "Unsaved Changes",
                    "Do you want to save your changes before closing?"
                )

                if result is None:
                    return False
                elif result:
                    self.save_file()
                    return True
                else:
                    return True
            return True

        def exit_editor(self):
            if self.unsaved_changes:
                if not self.confirm_discard_changes():
                    return
            self.root.destroy()

        def undo(self):
            self.text_area.event_generate("<<Undo>>")

        def redo(self):
            self.text_area.event_generate("<<Redo>>")

        def cut(self):
            self.text_area.event_generate("<<Cut>>")

        def copy(self):
            self.text_area.event_generate("<<Copy>>")

        def paste(self):
            self.text_area.event_generate("<<Paste>>")

        def delete(self):
            self.text_area.delete("sel.first", "sel.last")

        def select_all(self):
            self.text_area.tag_add('sel', '1.0', 'end')

        def toggle_word_wrap(self):
            wrap_mode = self.text_area.cget('wrap')
            self.text_area.config(wrap=tk.NONE if wrap_mode == tk.WORD else tk.WORD)

        def toggle_dark_mode(self):
            self.dark_mode = not self.dark_mode

            if self.dark_mode:
                bg_color = "black"
                fg_color = "#00FF00"
                menu_bg = "black"
                menu_fg = "#00FF00"
            else:
                bg_color = "white"
                fg_color = "black"
                menu_bg = None
                menu_fg = None

            self.text_area.config(
                bg=bg_color,
                fg=fg_color,
                insertbackground=fg_color)

            self.status_bar.config(
                bg=bg_color,
                fg=fg_color)
            self.root.config(bg=bg_color)
            try:
                self.root.option_add("*Menu.background", menu_bg if menu_bg else "SystemMenu")
                self.root.option_add("*Menu.foreground", menu_fg if menu_fg else "SystemMenuText")
                self.root.option_add("*Menu.activeBackground", "#003300" if self.dark_mode else "SystemMenuHighlight")
                self.root.option_add("*Menu.activeForeground", "#00FF00" if self.dark_mode else "SystemMenuText")
            except:
                pass

        def zoom_in(self):
            self.current_font_size += 2
            self.text_area.config(font=(self.current_font_family, self.current_font_size))

        def zoom_out(self):
            self.current_font_size -= 2
            self.text_area.config(font=(self.current_font_family, self.current_font_size))

        def choose_font(self):
            FontPicker(self.root, self.current_font_family, self.current_font_size, self.apply_font)

        def apply_font(self, font_family, font_size):
            self.current_font_family = font_family
            self.current_font_size = font_size
            self.text_area.config(font=(self.current_font_family, self.current_font_size))

        def choose_font_colour(self):
            colour = colorchooser.askcolor(title="Choose Font Colour")
            if colour[1]:
                self.current_font_colour = colour[1]
                self.text_area.config(fg=self.current_font_colour)

        def show_about(self):
            messagebox.showinfo("About", "TextLite - A simple text editor made with Tkinter. © 2025 Aditya Vardhan")

        def show_copyright(self):
            messagebox.showinfo("Copyright", "© 2025 Aditya Vardhan. All rights reserved.")

        def show_credits(self):
            credits_text = """
This software, TextLite, was developed independently for educational and personal use. 
Special thanks to the open-source community for providing tools and libraries such as Tkinter for GUI development.
Inspired by classic text editors, TextLite was created to offer a simple yet powerful writing experience. 
All trademarks and copyrights belong to their respective owners.
Developer: Aditya Vardhan
Version: 5.7
Year: 2025
"""
            messagebox.showinfo("Credits", credits_text)

        def show_disclaimer(self):
            disclaimer_text = """
This software is an independent text editor developed for educational and personal use. 
It is not affiliated, endorsed, or associated with Microsoft Corporation or its products, including Windows Notepad. 
All trademarks and copyrights belong to their respective owners.
"""
            messagebox.showinfo("Disclaimer", disclaimer_text)

        def show_license(self):
            license_text = """
MIT License

© 2025 Aditya Vardhan. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
            messagebox.showinfo("License", license_text)

        def open_readme(self, event=None):
            try:
                with open('Readme.txt', 'r', encoding='utf-8') as file:
                    readme_content = file.read()
                    readme_window = tk.Toplevel(self.root)
                    readme_window.title("Readme")
                    readme_window.geometry("600x400")

                    text_widget = tk.Text(readme_window, wrap=tk.WORD, font=("Arial", 12))
                    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                    scrollbar = tk.Scrollbar(readme_window, command=text_widget.yview)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    text_widget.config(yscrollcommand=scrollbar.set)
                    text_widget.insert(tk.END, readme_content)
                    text_widget.config(state=tk.DISABLED)
            except FileNotFoundError:
                messagebox.showerror("Error", "Readme.txt not found. There may be an error in your installation.")

        def update_status_bar(self, event=None):
            line, column = self.text_area.index(tk.INSERT).split('.')
            self.status_bar.config(text=f" " * 291 + f"|   Ln {line}, Col {int(column) + 1}          | 100%    | Windows (CRLF)    | UTF-8            ")

    if __name__ == "__main__":
        root = tk.Tk()
        TextEditor(root)
        root.mainloop()

textlite()
