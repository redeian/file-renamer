import os
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk


class FileRenamer:
    def __init__(self, master):
        self.master = master
        master.title("UTCC File Renamer")
        master.geometry("300x200")

        self.directory = ""
        self.files = []
        self.date_type = "created"
        self.add_date_prefix = True
        self.prefix = ""

        # Create the UI elements
        self.label = ttk.Label(master, text="Select a directory:")
        self.label.pack()

        self.browse_button = ttk.Button(
            master, text="Browse", command=self.browse_directory)
        self.browse_button.pack()

        self.prefix_checkbox_var = tk.BooleanVar(value=True)
        self.prefix_checkbox = ttk.Checkbutton(
            master, text="Use Date", variable=self.prefix_checkbox_var, command=self.toggle_date_prefix)
        self.prefix_checkbox.pack()

        # self.date_label = ttk.Label(master, text="Select date type:")
        # self.date_label.pack()

        self.date_var = tk.StringVar(value=self.date_type)
        # self.created_radio = ttk.Radiobutton(
        #     master, text="Created Date", variable=self.date_var, value="created")
        # self.created_radio.pack()

        # self.modified_radio = ttk.Radiobutton(
        #     master, text="Modified Date", variable=self.date_var, value="modified")
        # self.modified_radio.pack()

        self.prefix_label = ttk.Label(
            master, text="Enter a prefix (optional):")
        self.prefix_label.pack()

        self.prefix_entry = ttk.Entry(master, state="disabled")
        self.prefix_entry.pack()

        # self.remove_prefix_var = tk.BooleanVar(value=True)
        # self.remove_prefix_checkbox = ttk.Checkbutton(
        #     master, text="Remove existing prefix", variable=self.remove_prefix_var)
        # self.remove_prefix_checkbox.pack()

        self.rename_button = ttk.Button(
            master, text="Rename Files", command=self.rename_files, state="disabled")
        self.rename_button.pack()

        # Create the menu bar
        self.menu_bar = tk.Menu(master)
        self.master.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Quit", command=master.quit)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(
            label="Remove Prefix", command=self.remove_prefix)
        self.edit_menu.add_checkbutton(
            label="Use Modified Date", onvalue="", offvalue="created", variable=self.date_var)

        self.about_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="About", menu=self.about_menu)
        self.about_menu.add_command(
            label="About", command=self.show_about_dialog)

    def show_about_dialog(self):
        dialog = AboutDialog(self.master)

    def toggle_date_prefix(self):
        self.add_date_prefix = self.prefix_checkbox_var.get()
        if self.add_date_prefix:
            self.prefix_entry.config(state="disabled")
        else:
            self.prefix_entry.config(state="normal")

    def browse_directory(self):
        self.directory = filedialog.askdirectory()
        self.label.config(text=f"Selected directory: {self.directory}")
        self.files = os.listdir(self.directory)
        self.rename_button.config(state="normal")

    def remove_all_prefix(self):
        self.prefix_entry.delete(0, tk.END)

    def remove_prefix(self):
        for filename in self.files:
            if "_" in filename:
                new_filename = filename.split("_", 1)[1]
                os.rename(os.path.join(self.directory, filename),
                          os.path.join(self.directory, new_filename))
        messagebox.showinfo(
            "Success", "Prefix has been removed from all files")

        self.clear_files()

    def rename_files(self):
        if not self.directory:
            messagebox.showerror("Error", "Please select a directory")
            return

        self.date_type = self.date_var.get()
        self.prefix = self.prefix_entry.get()

        # Create a dialog to allow the user to select which files to rename
        dialog = FileDialog(self.master, self.files)
        selected_files = dialog.show()

        if not selected_files:
            return  # User cancelled

        for filename in selected_files:
            filepath = os.path.join(self.directory, filename)

            if os.path.isfile(filepath):
                # Get the selected date type
                if self.date_type == "created":
                    date_value = os.path.getctime(filepath)
                else:
                    date_value = os.path.getmtime(filepath)

                # Get the date as a string
                date_str = datetime.datetime.fromtimestamp(
                    date_value).strftime("%Y-%m-%d")

                # Remove the existing prefix, if requested
                # if self.remove_prefix_var.get():
                #     if "_" in filename:
                #         filename = filename.split("_", 1)[1]

                # Add the prefix to the filename
                new_filename = ""
                if self.prefix_checkbox_var.get():
                    new_filename = f"{date_str}_{filename}"
                else:
                    new_filename = f"{self.prefix}_{filename}"

                # Rename the file
                new_filepath = os.path.join(self.directory, new_filename)
                os.rename(filepath, new_filepath)

        messagebox.showinfo("Success", "Files have been renamed")
        self.clear_files()

    def clear_files(self):
        self.directory = ""
        self.label.config(text="Select a directory:")
        self.files = []
        self.rename_button.config(state="disabled")


class FileDialog:
    def __init__(self, parent, files):
        self.parent = parent
        self.files = files

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select files to rename")

        # Create a listbox to display the files
        self.listbox = tk.Listbox(self.dialog, selectmode="extended")
        for filename in files:
            self.listbox.insert(tk.END, filename)
        self.listbox.pack(expand=True, fill=tk.BOTH)

        self.listbox.select_set(0, tk.END)

        # Create OK and Cancel buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(side=tk.BOTTOM, padx=5, pady=5)

        ok_button = ttk.Button(button_frame, text="OK", command=self.ok)
        ok_button.pack(side=tk.LEFT)

        cancel_button = ttk.Button(
            button_frame, text="Cancel", command=self.cancel)
        cancel_button.pack(side=tk.LEFT)

        self.dialog.transient(parent)
        self.dialog.grab_set()

    def ok(self):
        # Get the selected filenames and close the dialog
        self.selected_files = [
            self.files[i] for i in self.listbox.curselection()]
        self.dialog.destroy()

    def cancel(self):
        # Close the dialog without returning any filenames
        self.selected_files = []
        self.dialog.destroy()

    def show(self):
        self.parent.wait_window(self.dialog)
        return self.selected_files


class AboutDialog:
    def __init__(self, parent):
        self.parent = parent

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About")

        self.label = ttk.Label(
            self.dialog, text="UTCC File Renamer version 1.0 is created by \n Chatchai Wangwiwattana (MarkDigital) @ UTCC")
        self.label.pack(padx=5, pady=5)

        # Create OK and Cancel buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(side=tk.BOTTOM, padx=5, pady=5)

        ok_button = ttk.Button(button_frame, text="OK", command=self.ok)
        ok_button.pack(side=tk.LEFT)

    def ok(self):
        self.dialog.destroy()


# root = tk.Tk()
root = ThemedTk(theme='breeze')
renamer = FileRenamer(root)
root.mainloop()
