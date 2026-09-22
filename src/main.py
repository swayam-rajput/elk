from profiles.manager import ProfileManager
from ui.app import PasswordManager


def main():
    profile_manager = ProfileManager()

    app = PasswordManager(profile_manager)
    app.run()

    # Persist any unsaved changes after the Textual app exits.
    # Both `service` and `settings_manager` always reflect the last active profile.
    service = app.service
    settings_manager = app.settings_manager
    if service and service.dirty:
        print("Saving changes...")
        service.save()
        if settings_manager and settings_manager.settings.auto_sync:
            service.sync()
    else:
        print("No changes detected.")


if __name__ == "__main__":
    main()
