import tkinter as tk
from tkinter import messagebox, simpledialog, BooleanVar, Entry, Label, Button, Listbox, END
from password_manager import PasswordManager

# Crea una instancia del gestor de contraseñas
manager = PasswordManager()

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Password Manager")

def authenticate():
    def check_password():
        password = password_entry.get()
        if manager.verify_master_password_gui(password):
            auth_window.destroy()
            show_main_interface()
        else:
            messagebox.showerror("Error", "Contraseña maestra incorrecta.")
            auth_window.destroy()
            root.destroy()

    auth_window = tk.Toplevel(root)
    auth_window.title("Autenticación")
    auth_window.geometry("300x150")
    
    Label(auth_window, text="Ingrese su contraseña maestra:").pack(pady=10)
    password_entry = Entry(auth_window, show="*", width=25)
    password_entry.pack(pady=10)
    
    Button(auth_window, text="Ingresar", command=check_password).pack(pady=10)
    password_entry.bind("<Return>", lambda event: check_password())
    
    root.wait_window(auth_window)

def show_main_interface():
    root.geometry("300x300")
    
    add_button = tk.Button(root, text="Add Password", command=add_password)
    add_button.pack(pady=10)

    view_button = tk.Button(root, text="View Password", command=view_password)
    view_button.pack(pady=10)

    delete_button = tk.Button(root, text="Delete URL", command=delete_password)
    delete_button.pack(pady=10)

def add_password():
    url = simpledialog.askstring("Input", "Enter the URL:")
    username = simpledialog.askstring("Input", "Enter the Username:")

    if manager.check_duplicate(url, username):
        messagebox.showwarning("Duplicado", "Ya existe una entrada para esta URL con el mismo usuario.")
        return

    use_random_password = messagebox.askyesno("Random Password", "¿Desea generar una contraseña aleatoria?")
    
    if use_random_password:
        length = simpledialog.askinteger("Input", "Ingrese la longitud de la contraseña:", initialvalue=12)
        
        use_alpha = BooleanVar(value=True)
        use_numeric = BooleanVar(value=True)
        use_special = BooleanVar(value=True)

        options_window = tk.Toplevel(root)
        options_window.title("Opciones de Generación")

        tk.Label(options_window, text="Seleccione los tipos de caracteres a incluir:").pack(pady=10)

        tk.Checkbutton(options_window, text="Alfabéticos (a-z, A-Z)", variable=use_alpha).pack(anchor='w')
        tk.Checkbutton(options_window, text="Numéricos (0-9)", variable=use_numeric).pack(anchor='w')
        tk.Checkbutton(options_window, text="Especiales (@, #, $, etc.)", variable=use_special).pack(anchor='w')

        def generate_and_use_password():
            password = manager.generate_random_password(
                length=length,
                use_alpha=use_alpha.get(),
                use_numeric=use_numeric.get(),
                use_special=use_special.get()
            )
            options_window.destroy()
            messagebox.showinfo("Generated Password", f"Contraseña generada: {password}")
            if url and username and password:
                manager.add_password(url, username, password)
                messagebox.showinfo("Info", "Password added successfully!")

        tk.Button(options_window, text="Generar Contraseña", command=generate_and_use_password).pack(pady=10)

    else:
        password = simpledialog.askstring("Input", "Enter the Password:")
        if url and username and password:
            manager.add_password(url, username, password)
            messagebox.showinfo("Info", "Password added successfully!")

def view_password():
    matches = manager.load_passwords()
    if matches:
        def on_select(event):
            selection = event.widget.curselection()
            if selection:
                index = selection[0]
                url = list(matches.keys())[index]
                username = matches[url]['username']
                password = matches[url]['password']
                root.clipboard_clear()
                root.clipboard_append(password)
                messagebox.showinfo("Copied", f"Usuario: {username}\nContraseña: {password}\n\nLa contraseña ha sido copiada al portapapeles.")
                match_window.destroy()

        match_window = tk.Toplevel(root)
        match_window.title("Seleccione una URL")
        tk.Label(match_window, text="Seleccione la URL para ver el usuario y copiar la contraseña:").pack(pady=10)

        listbox = tk.Listbox(match_window, selectmode="single")
        for url in matches.keys():
            listbox.insert(END, url)
        listbox.pack(pady=10)

        listbox.bind('<<ListboxSelect>>', on_select)

    else:
        messagebox.showerror("Error", "No se encontraron URLs almacenadas.")

def delete_password():
    matches = manager.load_passwords()
    if matches:
        def on_select(event):
            selection = event.widget.curselection()
            if selection:
                index = selection[0]
                url = list(matches.keys())[index]
                confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Seguro que desea eliminar la URL: {url}?")
                if confirm:
                    manager.delete_password(url)
                    messagebox.showinfo("Eliminado", f"La URL {url} ha sido eliminada.")
                    match_window.destroy()

        match_window = tk.Toplevel(root)
        match_window.title("Eliminar URL")
        tk.Label(match_window, text="Seleccione la URL que desea eliminar:").pack(pady=10)

        listbox = tk.Listbox(match_window, selectmode="single")
        for url in matches.keys():
            listbox.insert(END, url)
        listbox.pack(pady=10)

        listbox.bind('<<ListboxSelect>>', on_select)

    else:
        messagebox.showerror("Error", "No se encontraron URLs almacenadas.")

# Solicitar autenticación
authenticate()

# Ejecuta la aplicación
root.mainloop()
