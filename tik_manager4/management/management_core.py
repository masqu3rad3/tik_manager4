"""The core of the management system."""
from datetime import datetime, timezone

class ManagementCore:
    """The core of the management system."""
    @staticmethod
    def date_stamp():
        """Return the current date stamp in ISO 8601 format."""
        # Get the current time in UTC and format it as ISO 8601
        return datetime.now(timezone.utc).strftime(
            '%Y-%m-%dT%H:%M:%SZ')

    def sync_project(self):
        """This method is called when the project is synced."""
        raise NotImplementedError("The method 'sync_project' must be implemented.")

    def force_sync(self):
        """This method is called when the project is forcefully synced."""
        raise NotImplementedError("The method 'force_sync' must be implemented.")

    def authenticate(self):
        """This method is called when the user authenticates."""
        raise NotImplementedError("The method 'authenticate' must be implemented.")

    def logout(self):
        """This method is called when the user logs out."""
        raise NotImplementedError("The method 'logout' must be implemented.")

    def create_from_project(self):
        """This method is called when a new project is created."""
        raise NotImplementedError("The method 'create_project' must be implemented.")

    def get_projects(self):
        """This method is called when the projects are retrieved."""
        raise NotImplementedError("The method 'get_projects' must be implemented.")

    def get_all_assets(self):
        """This method is called when all assets are retrieved."""
        raise NotImplementedError("The method 'get_all_assets' must be implemented.")

    def get_all_shots(self):
        """This method is called when all shots are retrieved."""
        raise NotImplementedError("The method 'get_all_shots' must be implemented.")

    def get_entity_url(self, entity_type, entity_id):
        """This method is called when the URL of an entity is retrieved."""
        raise NotImplementedError("The method 'get_entity_url' must be implemented.")
