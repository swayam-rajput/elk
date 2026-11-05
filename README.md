# Elk Password Manager

![](elk.png)


Elk is a secure, keyboard-first, terminal-based password manager. It provides a dual-interface approach: a rich, keyboard-driven terminal user interface (TUI) for desktops, and a lightweight, zero-dependency console interface optimized for mobile devices (like Termux on Android).

With local-first storage, Argon2id key derivation, and AES-256-GCM encryption, Elk guarantees that your credentials remain private and secure while providing seamless GitHub-backed cloud synchronization.

---

## Overview

**Dual Interfaces:**
- **Desktop TUI**: Full-screen, responsive, keyboard-first UI with split-pane navigation built on [Textual](https://github.com/Textualize/textual).
- **Phone CLI**: Lightweight console interface designed for mobile devices and Termux.

**Architecture:**
Elk's design separates the interactive presentation layers from the core cryptographic and storage services. The system workflow shows Desktop and Phone interfaces both connecting through a Profile layer to the VaultService and SyncManager, with cryptographic encryption via Argon2id KDF and AES-256-GCM, and storage via local files or GitHub remote.

**Features:**
- Dual interfaces (desktop TUI and phone CLI)
- Multiple profiles with independent vaults and master passwords
- Profile isolation (each profile has its own vault and settings)
- Security: Argon2id KDF, AES-256-GCM authenticated encryption, configurable clipboard timeout
- GitHub-backed sync with profile-specific remote vault paths
- Vault import/export (encrypted vaults retain existing encryption)

---

## Getting Started

**Prerequisites:** Ensure you have Python 3.11 or newer installed.

**Installation:**
Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/yourusername/elk.git
cd elk

# Install dependencies using uv (recommended)
uv sync

# Or using standard pip
pip install -r requirements.txt
```

**Running the Desktop TUI:**
To launch the desktop interface:
```bash
python src/main.py
```
On the first launch, Elk creates a default `Personal` profile and asks you to create its master password.

**Navigation keys (Desktop):**
- `1-3`: View Passwords, Emails, or Settings screens
- `f` / `Ctrl+F`: Toggle search bar
- `a`: Add new item
- `e`: Edit selected item
- `d`: Delete selected item
- `y`: Copy selected password to clipboard
- `p`: Reveal / hide password
- `Ctrl+S`: Save item
- `Esc`: Cancel editing or close search
- `q`: Quit application

**Running the Phone Companion:**
To launch the lightweight phone app on a mobile device (Termux on Android):
```bash
python src/phone/main.py
```
The phone interface provides a lightweight CLI for working with the same encrypted vault format.

**Termux setup:**
- Install Termux from F-Droid or Google Play Store
- Termux includes Python and pip by default
- Run `pip install argon2-cffi cryptography pydantic python-dotenv requests textual` to install dependencies
- The `termux-clipboard-set` command is available by default for password copy functionality

**Keyboard shortcuts (Phone):**
- `S` - Search entries
- `A` - Add new entry
- `Y` - Sync with GitHub
- `L` - Lock vault and exit to main menu
- `X` - Exit application
- Number keys (1-N) - Select entry by number
- `P` - Show password (in entry view)
- `C` - Copy password to clipboard
- `E` - Edit entry
- `D` - Delete entry
- `B` - Back to search results

---

## Profiles

Each profile has its own encrypted vault and settings:

```
data/
├── profiles.json
└── profiles/
    ├── personal/
    │   ├── vault.enc
    │   └── settings.json
    │
    └── work/
        ├── vault.enc
        └── settings.json
```

Each profile has an independent master password and encryption key. `profiles.json` stores profile metadata and the default/active profile. It does not store master passwords or encryption keys.

---

## Configuration & Sync

Each profile stores its configuration separately:

```
data/profiles/<profile-id>/settings.json
```

This allows profiles to have independent GitHub repositories and synchronization settings.

**Setting Up GitHub Cloud Sync:**
1. Create a **private** GitHub repository dedicated to Elk vault synchronization.
2. Generate a **Fine-grained Personal Access Token (PAT)**.
3. Grant `Contents` **Read and write** access to the repository.
4. Open Elk's **Settings → GitHub Sync**.
5. Enter the GitHub username, repository name, and token.
6. Enable synchronization.

The remote repository uses profile-specific paths:
```
elk-vault/
└── data/
    └── profiles/
        ├── personal/
        │   └── vault.enc
        └── work/
            └── vault.enc
```
Only encrypted vault files are synchronized.

---

## Import & Export

Import and export operate on encrypted vault files. Exporting a vault does not decrypt or change it. An imported vault retains its existing encryption and therefore requires its original master password.

Example:
```
Encrypted vault
    ↓
Export
    ↓
Import
    ↓
Same encryption + same master password
```

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
