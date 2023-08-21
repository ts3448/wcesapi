from ces_object import CESObject
from paginated_list import PaginatedList
from nonrespondent import NonRespondent
from project_survey import ProjectSurvey
from project_course import ProjectCourse
from respondent import Respondent
from response_rate import ResponseRate
from raw_data_general import RawDataGeneral
from utilities import combine_kwargs


class Project(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)

    def get_project_surveys(self, filters=None, **kwargs):
        """
        Gets a list of surveys for the account by project id.

        API call:
            GET /api/projects/{projectId}/surveys
        
         Optional parameters (kwargs):
            page (int)    

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

    def get_respondents(self, filters=None):
        """
        Gets respondents in a project for the account.

        GET /api/projects/{projectId}/respondents

        Returns a PaginatedList of Respondents
        """

        return PaginatedList(
            Respondent,
            self.__requester,
            "GET",
            "projects/{}/respondents".format(self.id),
            filters=filters
            )

    def get_non_respondents(self, filters=None):
        """
        Gets non-respondents in a project for the account.

        GET /api/projects/{projectId}/nonRespondents

        Returns a PaginatedList of NonRespondents
        """

        return PaginatedList(
            NonRespondent,
            self.__requester,
            "GET",
            "projects/{}/nonRespondents".format(self.id),
            filters=filters
            )

    def get_response_rate(self, filters=None):
        """
        Gets response rates for a project for the account.

        GET /api/projects/{projectId}/responseRate

        Returns a PaginatedList of ResponseRate
        """

        return PaginatedList(
            ResponseRate,
            self.__requester,
            "GET",
            "projects/{}/responseRate".format(self.id),
            filters=filters
            )

    # need to see example response to know if it's different
    # from ResponseRate object
    # def get_overall_response_rate(self):
    #     """
    #     Gets response rates for a project for the account.

    #     GET /api/projects/{projectId}/OverallResponseRate

    #     Returns a ResponseRate
    #     """

    #     return PaginatedList(
    #         ResponseRate,
    #         self.__requester,
    #         "GET",
    #         "projects/{}/responseRate".format(self.id)
    #         )

    def get_raw_data(self, filters=None):
        """
        Gets response rates for a project for the account.

        GET /api/projects/{projectId}/general/rawData

        Returns a PaginatedList of RawDataGeneral
        """

        return PaginatedList(
            RawDataGeneral,
            self.__requester,
            "GET",
            "projects/{}/general/rawData".format(self.id),
            filters=filters
            )
