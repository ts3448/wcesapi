from ces_object import CESObject
from paginated_list import PaginatedList
from project import Project
from utilities import combine_kwargs
from metadata import Metadata


class Course(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)

    def get_projects(self, filters=None, **kwargs):
        """
        Gets a list of projects for a course in the account.

        GET /api/courses/{courseId}/projects

        Returns a PaginatedList of Projects
        """

        return PaginatedList(
            Project,
            self.__requester,
            "GET",
            "courses/{}/projects".format(self.id),
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_metadata(self):
        """
        Gets a list of metadata for the account by course id.

        GET /api/courses/{courseId}/metadata

        Returns a Metadata
        """
        response = self.__requester.request(
            "GET",
            "courses/{}/metadata".format(self.id)
            )
        return Metadata(self.__requester, response.json())


