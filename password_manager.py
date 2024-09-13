import bcrypt
import json
import os
from cryptography.fernet import Fernet

class PasswordManager:
    def __init__(self, master_password_file="master_password.hash", key_file="key_file.key"):
        self.password_file = "passwords.json"
        self.master_password_file = master_password_file
        self.key_file = key_file

        if not os.path.exists(self.password_file):
            with open(self.password_file, 'wb') as f:
                f.write(b'')  # Crea un archivo vacío si no existe

        if not os.path.exists(self.master_password_file):
            self.set_master_password()

        if not os.path.exists(self.key_file):
            self.generate_key()

        self.key = self.load_key()
        self.cipher_suite = Fernet(self.key)

    def set_master_password(self):
        password = input("Establezca una nueva contraseña maestra: ").encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        with open(self.master_password_file, 'wb') as f:
            f.write(hashed)

    def verify_master_password(self):
        password = input("Ingrese su contraseña maestra: ").encode('utf-8')
        with open(self.master_password_file, 'rb') as f:
            stored_password = f.read()
        return bcrypt.checkpw(password, stored_password)

    def verify_master_password_gui(self, password):
        with open(self.master_password_file, 'rb') as f:
            stored_password = f.read()
        return bcrypt.checkpw(password.encode('utf-8'), stored_password)

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as key_file:
            key_file.write(key)

    def load_key(self):
        return open(self.key_file, 'rb').read()

    def load_passwords(self):
        with open(self.password_file, 'rb') as file:
            encrypted_data = file.read()
            if encrypted_data:
                decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode('utf-8'))
            else:
                return {}

    def save_passwords(self, data):
        with open(self.password_file, 'wb') as file:
            encrypted_data = self.cipher_suite.encrypt(json.dumps(data).encode('utf-8'))
            file.write(encrypted_data)

    def add_password(self, url, username, password):
        passwords = self.load_passwords()
        passwords[url] = {"username": username, "password": password}
        self.save_passwords(passwords)

    def delete_password(self, url):
        passwords = self.load_passwords()
        if url in passwords:
            del passwords[url]
            self.save_passwords(passwords)

    def check_duplicate(self, url, username):
        passwords = self.load_passwords()
        if url in passwords and passwords[url]['username'] == username:
            return True
        return False
    
    def search_passwords(self, search_term):
        passwords = self.load_passwords()
        matches = {url: data for url, data in passwords.items() if search_term.lower() in url.lower()}
        return matches
    
    def generate_random_password(self, length=12, use_alpha=True, use_numeric=True, use_special=True):
        import random
        import string

        characters = ''
        if use_alpha:
            characters += string.ascii_letters  # a-z, A-Z
        if use_numeric:
            characters += string.digits  # 0-9
        if use_special:
            characters += string.punctuation  # Special characters

        if not characters:
            raise ValueError("Debe seleccionar al menos un tipo de carácter para generar la contraseña.")

        random_password = ''.join(random.choice(characters) for i in range(length))
        return random_password
