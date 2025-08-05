import os
import json
import shutil
import hashlib
import readline  # For input history
from getpass import getpass
from cryptography.fernet import Fernet
import base64
from datetime import datetime  # Added for dynamic date

class RE_startBase:
    def __init__(self):
        self.current_db = None
        self.db_path = ""
        self.key = None
        self.unsaved_changes = False
        self.setup()

    def setup(self):
        """Initialize environment and encryption"""
        os.makedirs("data_vaults", exist_ok=True)
        self.load_or_create_key()
        print(self.style_text("\n[+] RE_start Base initialized - Secure your digital footprint\n", "red"))

    def style_text(self, text, color="white", style="normal"):
        """Add terminal styling to text"""
        styles = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "bold": "\033[1m",
            "underline": "\033[4m",
            "end": "\033[0m"
        }
        # Only apply style if not 'normal'
        color_code = styles.get(color, "")
        style_code = styles.get(style, "") if style != "normal" else ""
        return f"{color_code}{style_code}{text}{styles['end']}"

    def load_or_create_key(self):
        """Handle encryption key management"""
        key_file = ".crypto_key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(self.key)
            try:
                os.chmod(key_file, 0o600)  # Restrict permissions (may fail on Windows)
            except Exception:
                pass

    def encrypt_data(self, data):
        """Encrypt sensitive database content"""
        fernet = Fernet(self.key)
        return fernet.encrypt(json.dumps(data).encode()).decode()

    def decrypt_data(self, encrypted_data):
        """Decrypt database content"""
        fernet = Fernet(self.key)
        return json.loads(fernet.decrypt(encrypted_data.encode()).decode())

    def hash_password(self, password):
        """Create secure password hash (salted)"""
        # Store salt with hash for verification
        salt = os.urandom(16)
        hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return base64.b64encode(salt + hash_bytes).decode()

    def verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        decoded = base64.b64decode(stored_hash.encode())
        salt = decoded[:16]
        hash_bytes = decoded[16:]
        test_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return test_hash == hash_bytes

    def create_db(self):
        """Create a new encrypted database"""
        print(self.style_text("\n[+] Creating new data vault", "cyan"))
        db_name = input(self.style_text("[?] Enter vault name: ", "yellow")).strip()

        if not db_name:
            print(self.style_text("[-] Operation canceled", "red"))
            return

        self.db_path = f"data_vaults/{db_name}.vault"

        if os.path.exists(self.db_path):
            print(self.style_text("[-] Vault already exists!", "red"))
            return

        password = getpass(self.style_text("[?] Set master key: ", "yellow"))
        confirm = getpass(self.style_text("[?] Confirm master key: ", "yellow"))

        if password != confirm:
            print(self.style_text("[-] Keys do not match!", "red"))
            return

        self.current_db = {
            "meta": {
                "name": db_name,
                "password_hash": self.hash_password(password),
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "tables": {}
        }
        self.save_db()
        print(self.style_text(f"[+] Vault '{db_name}' created successfully!", "green"))

    def authenticate(self):
        """Verify master key access"""
        password = getpass(self.style_text("[?] Enter master key: ", "yellow"))
        if not self.verify_password(password, self.current_db["meta"]["password_hash"]):
            print(self.style_text("[-] Access denied! Invalid credentials", "red"))
            return False
        return True

    def open_db(self):
        """Access an existing database"""
        print(self.style_text("\n[+] Available data vaults:", "cyan"))
        vaults = [f for f in os.listdir("data_vaults") if f.endswith(".vault")]

        if not vaults:
            print(self.style_text("[-] No vaults found", "red"))
            return

        for i, vault in enumerate(vaults, 1):
            print(self.style_text(f"{i}. {vault[:-6]}", "blue"))

        choice = input(self.style_text("\n[?] Select vault (1-" + str(len(vaults)) + "): ", "yellow"))

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(vaults):
                self.db_path = f"data_vaults/{vaults[idx]}"
                with open(self.db_path, "r") as f:
                    encrypted = f.read()
                self.current_db = self.decrypt_data(encrypted)

                if not self.authenticate():
                    self.current_db = None
                    return

                print(self.style_text(f"\n[+] Access granted to '{vaults[idx][:-6]}'", "green"))
                self.unsaved_changes = False
            else:
                print(self.style_text("[-] Invalid selection", "red"))
        except (ValueError, IndexError):
            print(self.style_text("[-] Invalid input", "red"))

    def save_db(self):
        """Save database with encryption"""
        if not self.current_db:
            print(self.style_text("[-] No vault is open", "red"))
            return

        encrypted = self.encrypt_data(self.current_db)
        with open(self.db_path, "w") as f:
            f.write(encrypted)
        self.unsaved_changes = False
        print(self.style_text("[+] Vault secured successfully", "green"))

    def edit_db(self):
        """Edit database structure and content"""
        if not self.current_db:
            print(self.style_text("[-] Open a vault first", "red"))
            return

        while True:
            print(self.style_text("\n[+] Vault Operations:", "cyan"))
            print(self.style_text("1. Create new table", "blue"))
            print(self.style_text("2. List tables", "blue"))
            print(self.style_text("3. Add record", "blue"))
            print(self.style_text("4. Search records", "blue"))
            print(self.style_text("5. Backup vault", "blue"))
            print(self.style_text("6. Return to main menu", "blue"))

            choice = input(self.style_text("\n[?] Operation: ", "yellow")).strip()

            if choice == "1":
                self.create_table()
            elif choice == "2":
                self.list_tables()
            elif choice == "3":
                self.add_record()
            elif choice == "4":
                self.search_records()
            elif choice == "5":
                self.backup_vault()
            elif choice == "6":
                if self.unsaved_changes:
                    save = input(self.style_text("[?] Save changes? (y/N): ", "yellow")).lower()
                    if save == "y":
                        self.save_db()
                return
            else:
                print(self.style_text("[-] Invalid choice", "red"))

    def create_table(self):
        """Create a new table structure"""
        table_name = input(self.style_text("\n[?] Table name: ", "yellow")).strip()
        if not table_name:
            return

        if table_name in self.current_db["tables"]:
            print(self.style_text("[-] Table already exists", "red"))
            return

        fields = input(self.style_text("[?] Enter field names (comma separated): ", "yellow")).split(",")
        fields = [f.strip() for f in fields if f.strip()]

        if not fields:
            print(self.style_text("[-] No fields provided", "red"))
            return

        self.current_db["tables"][table_name] = {
            "fields": fields,
            "records": []
        }
        self.unsaved_changes = True
        print(self.style_text(f"[+] Table '{table_name}' created", "green"))

    def list_tables(self):
        """Show available tables"""
        print(self.style_text("\n[+] Tables in vault:", "cyan"))
        for table in self.current_db["tables"]:
            record_count = len(self.current_db["tables"][table]["records"])
            print(self.style_text(f"- {table} ({record_count} records)", "blue"))

    def add_record(self):
        """Add data to a table"""
        self.list_tables()
        table_name = input(self.style_text("\n[?] Select table: ", "yellow")).strip()

        if table_name not in self.current_db["tables"]:
            print(self.style_text("[-] Table not found", "red"))
            return

        table = self.current_db["tables"][table_name]
        record = {}

        print(self.style_text("\n[+] Enter record data:", "cyan"))
        for field in table["fields"]:
            value = input(self.style_text(f"{field}: ", "yellow")).strip()
            record[field] = value

        table["records"].append(record)
        self.unsaved_changes = True
        print(self.style_text("[+] Record added successfully", "green"))

    def search_records(self):
        """Search database content"""
        self.list_tables()
        table_name = input(self.style_text("\n[?] Select table: ", "yellow")).strip()

        if table_name not in self.current_db["tables"]:
            print(self.style_text("[-] Table not found", "red"))
            return

        table = self.current_db["tables"][table_name]
        search_term = input(self.style_text("[?] Search term: ", "yellow")).lower()

        print(self.style_text("\n[+] Search results:", "cyan"))
        found = False

        for record in table["records"]:
            for value in record.values():
                if search_term in str(value).lower():
                    print(self.style_text("-" * 50, "magenta"))
                    for k, v in record.items():
                        print(self.style_text(f"{k}: ", "blue") + self.style_text(f"{v}", "white"))
                    found = True
                    break

        if not found:
            print(self.style_text("[-] No matching records found", "red"))

    def backup_vault(self):
        """Create a backup of the current vault"""
        if not self.current_db:
            print(self.style_text("[-] No vault open", "red"))
            return

        backup_dir = "vault_backups"
        os.makedirs(backup_dir, exist_ok=True)

        shutil.copy2(self.db_path, os.path.join(backup_dir, os.path.basename(self.db_path)))
        print(self.style_text(f"[+] Backup created in '{backup_dir}'", "green"))

    def wipe_vault(self):
        """Securely delete a database"""
        vaults = [f for f in os.listdir("data_vaults") if f.endswith(".vault")]
        if not vaults:
            print(self.style_text("[-] No vaults available", "red"))
            return

        for i, vault in enumerate(vaults, 1):
            print(self.style_text(f"{i}. {vault[:-6]}", "blue"))

        choice = input(self.style_text("\n[?] Select vault to wipe (1-" + str(len(vaults)) + "): ", "yellow"))

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(vaults):
                target = f"data_vaults/{vaults[idx]}"
                confirm = input(self.style_text(f"[!] WARNING: PERMANENTLY DELETE '{vaults[idx][:-6]}'? (type CONFIRM): ", "red"))
                if confirm == "CONFIRM":
                    os.remove(target)
                    print(self.style_text("[+] Vault obliterated", "green"))
                else:
                    print(self.style_text("[-] Operation canceled", "yellow"))
            else:
                print(self.style_text("[-] Invalid selection", "red"))
        except (ValueError, IndexError):
            print(self.style_text("[-] Invalid input", "red"))

    def main_menu(self):
        """Command-line interface"""
        art = r"""
        ██████╗ ███████╗    ███████╗████████╗ █████╗ ██████╗ ████████╗
        ██╔══██╗██╔════╝    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝
        ██████╔╝█████╗█████╗███████╗   ██║   ███████║██████╔╝   ██║   
        ██╔══██╗██╔══╝╚════╝╚════██║   ██║   ██╔══██║██╔══██╗   ██║   
        ██║  ██║███████╗    ███████║   ██║   ██║  ██║██║  ██║   ██║   
        ╚═╝  ╚═╝╚══════╝    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
        """
        print(self.style_text(art, "red", "bold"))

        while True:
            print(self.style_text("\n[+] Main Menu:", "cyan", "bold"))
            print(self.style_text("1. Create new vault", "blue"))
            print(self.style_text("2. Access existing vault", "blue"))
            print(self.style_text("3. Secure vault (save)", "blue"))
            print(self.style_text("4. Wipe vault", "red"))
            print(self.style_text("5. Exit", "yellow"))

            choice = input(self.style_text("\n[?] Operation: ", "yellow", "bold")).strip()

            if choice == "1":
                self.create_db()
            elif choice == "2":
                self.open_db()
                if self.current_db:
                    self.edit_db()
            elif choice == "3":
                self.save_db()
            elif choice == "4":
                self.wipe_vault()
            elif choice == "5":
                if self.unsaved_changes:
                    save = input(self.style_text("[?] Save changes before exiting? (y/N): ", "yellow")).lower()
                    if save == "y":
                        self.save_db()
                print(self.style_text("\n[+] Connection terminated securely", "green"))
                break
            else:
                print(self.style_text("[-] Invalid selection", "red"))

if __name__ == "__main__":
    try:
        app = RE_startBase()
        app.main_menu()
    except KeyboardInterrupt:
        print("\n\n[-] Operation aborted by user")
    except Exception as e:
        print(f"\n[-] CRITICAL FAILURE: {str(e)}")