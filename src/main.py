from vault.service import VaultService
from ui.app import ElkPasswordManagerApp

def main():
    service = VaultService()
    app = ElkPasswordManagerApp(service)
    app.run()

if __name__ == "__main__":
    main()

