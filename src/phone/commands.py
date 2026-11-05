import subprocess
from crypto.random import RandomGenerator
from models.entry import Entry, Site
from models.email import Email

def copy_password(password: str) -> bool:
    """
    Copies the password to the Termux clipboard using the termux-clipboard-set command.
    """
    try:
        subprocess.run(
            ["termux-clipboard-set"],
            input=password,
            text=True,
            check=True,
            capture_output=True
        )
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False

def prompt_add_entry(service) -> Entry | None:
    """
    Prompts the user to input the fields to create a new Entry.
    """
    print("\n--- Add New Entry ---")
    name = input("Site Name: ").strip()
    if not name:
        print("Site Name cannot be empty.")
        return None
    url = input("Site URL: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    if not password:
        print("Password cannot be empty.")
        return None
    
    # Email templates selection
    emails = service.get_emails()
    email_id = ""
    if emails:
        print("\nAvailable Emails:")
        for idx, email in enumerate(emails, 1):
            print(f"  {idx}. {email.address} ({email.label})")
        print(f"  {len(emails)+1}. [Enter Custom Email]")
        print(f"  {len(emails)+2}. [None]")
        try:
            choice = input(f"Select email option (1-{len(emails)+2}): ").strip()
            if choice:
                val = int(choice)
                if 1 <= val <= len(emails):
                    email_id = emails[val-1].address
                elif val == len(emails) + 1:
                    email_id = input("Custom Email: ").strip()
        except ValueError:
            print("Invalid selection, defaulting to no email.")
    else:
        email_id = input("Email: ").strip()

    notes = input("Notes: ").strip()
    
    new_entry = Entry(
        id=RandomGenerator.generate_uuid(),
        site=Site(name=name, url=url),
        email_id=email_id,
        username=username if username else None,
        password=password,
        notes=notes,
    )
    return new_entry

def prompt_edit_entry(service, entry: Entry) -> Entry | None:
    """
    Prompts the user to edit existing fields on an Entry.
    Pressing enter keeps the current values.
    """
    print(f"\n--- Edit Entry: {entry.site.name} ---")
    print("Press Enter to keep current value.")
    
    name = input(f"Site Name [{entry.site.name}]: ").strip() or entry.site.name
    url = input(f"Site URL [{entry.site.url}]: ").strip() or entry.site.url
    
    current_username = entry.username or ""
    username_input = input(f"Username [{current_username}]: ").strip()
    username = username_input if username_input else entry.username
    
    password = input(f"Password [********]: ").strip() or entry.password
    
    # Email selection
    emails = service.get_emails()
    email_id = entry.email_id
    if emails:
        print(f"\nCurrent Email: {entry.email_id or 'None'}")
        print("Available Emails:")
        for idx, email in enumerate(emails, 1):
            print(f"  {idx}. {email.address} ({email.label})")
        print(f"  {len(emails)+1}. [Enter Custom Email]")
        print(f"  {len(emails)+2}. [None/Clear]")
        print(f"  {len(emails)+3}. [Keep Current]")
        try:
            choice = input(f"Select option (1-{len(emails)+3}): ").strip()
            if choice:
                val = int(choice)
                if 1 <= val <= len(emails):
                    email_id = emails[val-1].address
                elif val == len(emails) + 1:
                    email_id = input("Custom Email: ").strip()
                elif val == len(emails) + 2:
                    email_id = ""
        except ValueError:
            pass
    else:
        email_id = input(f"Email [{entry.email_id}]: ").strip() or entry.email_id

    notes = input(f"Notes [{entry.notes}]: ").strip() or entry.notes
    
    updated_entry = Entry(
        id=entry.id,
        site=Site(name=name, url=url),
        email_id=email_id,
        username=username,
        password=password,
        notes=notes,
        favorite=entry.favorite,
        created_at=entry.created_at
    )
    return updated_entry

def prompt_delete_entry(service, entry: Entry) -> bool:
    """
    Prompts the user to confirm deletion of an Entry.
    """
    confirm = input(f"Are you sure you want to delete '{entry.site.name}'? (y/N): ").strip().lower()
    return confirm == 'y'
