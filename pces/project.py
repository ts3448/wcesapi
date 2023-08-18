from ces_object import CESObject
from paginated_list import PaginatedList
from project_survey import ProjectSurvey
from project_course import ProjectCourse
from utilities import combine_kwargs


class Project(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)

    def get_project_surveys(self, filters=None, **kwargs):
        """
        Gets a list of surveys for the account by project id.

        GET /api/projects/{projectId}/surveys

        Returns a PaginatedList of ProjectSurveys
        """

        return PaginatedList(
            ProjectSurvey,
            self.__requester,
            "GET",
            "projects/{}/surveys".format(self.id),
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_project_courses(self, filters=None, **kwargs):
        """
        Gets a list of courses for a project.

        GET /api/projects/{projectId}/courses

        Returns a PaginatedList of ProjectCourse
        """

        return PaginatedList(
            ProjectCourse,
            self.__requester,
            "GET",
            "projects/{}/courses".format(self.id),
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_project_course(self, id, **kwargs):
        """
        Gets a course in a project for the account.

        GET /api/projects/{projectId}/courses/{id}

        Returns a ProjectCourse
        """

        return PaginatedList(
            ProjectCourse,
            self.__requester,
            "GET",
            "projects/{}/courses/{}".format(self.id, id),
            _kwargs=combine_kwargs(**kwargs)
            )
    

    