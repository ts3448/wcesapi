from pces.ces_object import CESObject
from pces.pandanated_list import PandanatedList
from pces.project import Project
from pces.utilities import combine_kwargs
from pces.metadata import Metadata


class Course(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)

    def get_projects(self, filters=None, **kwargs):
        """
        Gets a list of projects for a course in the account.

        API call:
            GET /api/courses/{courseId}/projects

        Params:
            filters (dict): attributes and value pairs to apply as a filter.

            **kwargs:
                page (int)

        Returns a PandanatedList of Projects
        """

        return PandanatedList(
            Project,
            self.__requester,
            "GET",
            "courses/{}/projects".format(self.id),
            filters=filters,
            extra_attribs={"courseID": self.id},
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
