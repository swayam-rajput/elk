from models.entry import Entry
from models.email import Email
from models.vault import Vault

class VaultManager:
    """
    Responsible for managing the decrypted vault in memory
    """

    def __init__(self, vault: Vault):
        self.vault = vault
        
    def add_email(self, email: Email) -> None:
        self.vault.emails.append(email)
    
    def get_email(self, email_id: str) -> Email | None:
        for email in self.vault.emails:
            if email.id == email_id:
                return email
        
        return None
    


    def add_entry(self, entry: Entry) -> None:
        self.vault.entries.append(entry)
    
    def get_entry(self, entry_id: str) -> Entry | None:
        for entry in self.vault.entries:
            if entry.id == entry_id:
                return entry

        return None

    def delete_entry(self, entry_id: str) -> bool:
        for i, entry in enumerate(self.vault.entries):
            if entry.id == entry_id:
                del self.vault.entries[i]
                return True
        return False
    
    def list_entries(self) -> list[Entry]:
        return self.vault.entries
    

