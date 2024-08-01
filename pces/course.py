from ces_object import CESObject
from project import Project
from metadata import Metadata


class Course(CESObject):
    """
    Represents a Course in the CES system.
    """

    def __str__(self):
        return "{} ({})".format(self.title, self.id)

    def list_projects(self):
        """
        Gets a list of projects for the course.

        Returns:
            Project: A Project object representing the retrieved projects.
        """
        api_endpoint = f"courses/{self.id}/projects"
        return Project(self._requester, "GET", api_endpoint)

    def list_metadata(self):
        """
        Gets a list of metadata for the course.

        Returns:
            Metadata: A Metadata object representing the retrieved metadata.
        """
        api_endpoint = f"courses/{self.id}/metadata"
        return Metadata(self._requester, "GET", api_endpoint)

    def save_metadata(self, name: str, value: str):
        """
        Creates or updates metadata for the course.

        Args:
            name (str): The name of the metadata.
            value (str): The value of the metadata.

        Returns:
            Metadata: A Metadata object representing the saved metadata.
        """
        api_endpoint = f"courses/{self.id}/metadata"
        data = {"name": name, "value": value}
        return Metadata(self._requester, "POST", api_endpoint, data=data)

    def remove_metadata(self, name: str):
        """
        Removes metadata from the course.

        Args:
            name (str): The name of the metadata to remove.

        Returns:
            dict: The response from the API after removing the metadata.
        """
        api_endpoint = f"courses/{self.id}/metadata/name/{name}"
        return self._requester.request("DELETE", api_endpoint)
