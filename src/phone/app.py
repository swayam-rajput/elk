import os
from phone.commands import (
    copy_password,
    prompt_add_entry,
    prompt_edit_entry,
    prompt_delete_entry
)

class PhoneApp:
    def __init__(self, service):
        self.service = service
        self.locked_by_user = False
        self.current_query = ""
        self.results = []

    def clear_screen(self):
        """
        Clears the terminal screen for a clean, app-like UI.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        """
        Main application run loop. Prompts for search immediately upon startup.
        """
        # Step 1: Immediate Search on Startup
        self.current_query = input("Search query (press Enter to show all): ").strip()
        
        while True:
            self.results = self.service.search_entries(self.current_query)
            self.clear_screen()
            
            print("=" * 40)
            print("Elk")
            print("=" * 40)
            if not self.results:
                print("No entries found.")
            else:
                for idx, entry in enumerate(self.results, 1):
                    detail_str = []
                    if entry.username:
                        detail_str.append(entry.username)
                    if entry.email_id:
                        detail_str.append(entry.email_id)
                    details = f" ({' | '.join(detail_str)})" if detail_str else ""
                    print(f"{idx:2d}. {entry.site.name}{details}")
            print("-" * 40)
            print("[S] Search | [A] Add | [Y] Sync | [L] Lock | [X] Exit")
            print("-" * 40)
            
            choice = input("Select number or command: ").strip()
            if not choice:
                continue
                
            choice_upper = choice.upper()
            if choice_upper == 'S':
                self.current_query = input("Search query (press Enter to show all): ").strip()
            elif choice_upper == 'A':
                new_entry = prompt_add_entry(self.service)
                if new_entry:
                    try:
                        self.service.add_entry(new_entry)
                        print("Entry added successfully.")
                    except ValueError as e:
                        print(f"Error: {e}")
                    input("Press Enter to continue...")
            elif choice_upper == 'Y':
                if self.service.sync_manager:
                    print("Syncing with GitHub...")
                    # Save local changes if dirty first
                    if self.service.dirty:
                        self.service.save()
                    if self.service.sync():
                        print("Sync completed successfully.")
                    else:
                        print("Sync finished (no changes or up to date).")
                else:
                    print("GitHub sync is not configured/enabled.")
                input("Press Enter to continue...")
            elif choice_upper == 'L':
                self.locked_by_user = True
                break
            elif choice_upper == 'X':
                break
            else:
                # Check if user selected an entry number
                try:
                    idx = int(choice)
                    if 1 <= idx <= len(self.results):
                        self.view_entry_flow(self.results[idx-1])
                    else:
                        print("Invalid number selection.")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid command.")
                    input("Press Enter to continue...")

    def view_entry_flow(self, entry):
        """
        Flow for viewing a single entry's details and managing operations on it.
        """
        while True:
            # Always get a fresh version of the entry from the service
            fresh_entry = self.service.get_entry(entry.id)
            if not fresh_entry:
                break
            
            self.clear_screen()
            print("=" * 40)
            print(f"ENTRY DETAILS: {fresh_entry.site.name}")
            print("=" * 40)
            print(f"Site Name: {fresh_entry.site.name}")
            print(f"Site URL:  {fresh_entry.site.url}")
            print(f"Email ID:  {fresh_entry.email_id or 'None'}")
            print(f"Username:  {fresh_entry.username or 'None'}")
            print(f"Notes:     {fresh_entry.notes or 'None'}")
            print("-" * 40)
            print("[P] Show Pass | [C] Copy Pass | [E] Edit | [D] Delete | [B] Back")
            print("-" * 40)
            
            choice = input("Select option: ").strip().upper()
            if choice == 'P':
                print(f"Password: {fresh_entry.password}")
                input("\nPress Enter to hide password...")
            elif choice == 'C':
                if copy_password(fresh_entry.password):
                    print("Password copied to Termux clipboard!")
                else:
                    print("Copy failed. Is termux-api installed?")
                input("Press Enter to continue...")
            elif choice == 'E':
                updated = prompt_edit_entry(self.service, fresh_entry)
                if updated:
                    try:
                        self.service.update_entry(updated)
                        print("Entry updated successfully.")
                    except ValueError as e:
                        print(f"Error updating entry: {e}")
                    input("Press Enter to continue...")
            elif choice == 'D':
                if prompt_delete_entry(self.service, fresh_entry):
                    self.service.delete_entry(fresh_entry.id)
                    print("Entry deleted successfully.")
                    input("Press Enter to continue...")
                    break
            elif choice == 'B':
                break
