import json
import os
import sys
from src.encryption import encrypt_data, decrypt_data, verify_password, load_salt

def _data_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(_data_dir(), "data.enc")


class DataStore:
    """Handles encrypted storage of password entries."""

    def __init__(self, filepath: str = DATA_FILE):
        self.filepath = filepath
        self._password = None
        self._salt = None
        self._entries = []
        self._categories = ["默认", "工作", "个人", "金融", "社交", "游戏"]

    def has_data(self) -> bool:
        """Check if encrypted data file exists."""
        return os.path.exists(self.filepath)

    def unlock(self, password: str) -> bool:
        """Unlock and load data with password."""
        if not self.has_data():
            return False
        with open(self.filepath, "rb") as f:
            encrypted = f.read()
        salt = load_salt()
        if not verify_password(password, salt, encrypted):
            return False
        decrypted = decrypt_data(encrypted, password, salt)
        data = json.loads(decrypted)
        self._password = password
        self._salt = salt
        self._entries = data.get("entries", [])
        self._categories = data.get("categories", self._categories)
        return True

    def save(self):
        """Save data to encrypted file."""
        if self._password is None or self._salt is None:
            raise RuntimeError("Not unlocked")
        data = json.dumps(
            {"entries": self._entries, "categories": self._categories},
            ensure_ascii=False,
            indent=2,
        )
        encrypted = encrypt_data(data, self._password, self._salt)
        with open(self.filepath, "wb") as f:
            f.write(encrypted)

    def create_new(self, password: str):
        """Create a new data store."""
        from src.encryption import derive_key

        salt = os.urandom(16)
        key, _ = derive_key(password, salt)
        self._password = password
        self._salt = salt
        self._entries = []
        self._categories = ["默认", "工作", "个人", "金融", "社交", "游戏"]
        with open("data.salt", "wb") as f:
            f.write(salt)
        self.save()

    def get_entries(self) -> list:
        return list(self._entries)

    def get_categories(self) -> list:
        return list(self._categories)

    def add_entry(self, entry: dict) -> str:
        import uuid

        entry["id"] = str(uuid.uuid4())
        self._entries.append(entry)
        self.save()
        return entry["id"]

    def update_entry(self, entry_id: str, updates: dict):
        for entry in self._entries:
            if entry["id"] == entry_id:
                entry.update(updates)
                self.save()
                return

    def delete_entry(self, entry_id: str):
        self._entries = [e for e in self._entries if e["id"] != entry_id]
        self.save()

    def add_category(self, name: str):
        if name not in self._categories:
            self._categories.append(name)
            self.save()

    def delete_category(self, name: str):
        if name in self._categories and name != "默认":
            self._categories.remove(name)
            self.save()
