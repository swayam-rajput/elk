from profiles.manager import ProfileManager
from config.settings_manager import SettingsManager
from ui.app import PasswordManager


def main():
    profile_manager = ProfileManager()
    settings_manager = SettingsManager()

    app = PasswordManager(profile_manager, settings_manager)
    app.run()

    # Persist any unsaved changes after the Textual app exits
    service = app.service
    if service and service.dirty:
        print("Saving changes...")
        service.save()
        if settings_manager.settings.auto_sync:
            service.sync()
    else:
        print("No changes detected.")


if __name__ == "__main__":
    main()
