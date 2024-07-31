from ces_object import CESObject
from pandanated_list import PandanatedList
from nonrespondent import NonRespondent
from overall_response_rate import OverallResponseRate
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

        Returns a PandanatedList of ProjectSurveys
        """
        extra_attribs = {"projectId": self.id}

        return PandanatedList(
            ProjectSurvey,
            self._requester,
            "GET",
            "projects/{}/surveys".format(self.id),
            filters=filters,
            context=self,
            extra_attribs=extra_attribs,
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_project_courses(self, filters=None, **kwargs):
        """
        Gets a list of courses for a project.

        GET /api/projects/{projectId}/courses

        Returns a PandanatedList of ProjectCourse
        """
        extra_attribs = {"projectId": self.id}

        return PandanatedList(
            ProjectCourse,
            self._requester,
            "GET",
            "projects/{}/courses".format(self.id),
            filters=filters,
            context=self,
            extra_attribs=extra_attribs,
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_project_course(self, id, **kwargs):
        """
        Gets a course in a project for the account.

        GET /api/projects/{projectId}/courses/{id}

        Returns a ProjectCourse
        """
        extra_attribs = {"projectId": self.id}

        return PandanatedList(
            ProjectCourse,
            self._requester,
            "GET",
            "projects/{}/courses/{}".format(self.id, id),
            context=self,
            extra_attribs=extra_attribs,
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_respondents(self, filters=None, **kwargs):
        """
        Gets respondents in a project for the account.

        GET /api/projects/{projectId}/respondents

        Returns a PandanatedList of Respondents
        """

        return PandanatedList(
            Respondent,
            self.__requester,
            "GET",
            "projects/{}/respondents".format(self.id),
            context=self,
            filters=filters,
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_non_respondents(self, filters=None, **kwargs):
        """
        Gets non-respondents in a project for the account.

        GET /api/projects/{projectId}/nonRespondents

        Returns a PandanatedList of NonRespondents
        """

        return PandanatedList(
            NonRespondent,
            self._requester,
            "GET",
            "projects/{}/nonRespondents".format(self.id),
            filters=filters,
            context=self,
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_response_rate(self, filters=None, return_type=None, **kwargs):
        """
        Gets response rates for a project for the account.

        GET /api/projects/{projectId}/responseRate

        Returns a PandanatedList of ResponseRate
        """

        if return_type:
            kwargs["return_type"] = return_type

        return PandanatedList(
            ResponseRate,
            self._requester,
            "GET",
            "projects/{}/responseRate".format(self.id),
            filters=filters,
            context=self,
            _kwargs=combine_kwargs(**kwargs),
        )

    def get_overall_response_rate(self, filters=None, return_type=None, join=False):
        """
        Gets response rates for a project for the account.

        GET /api/projects/{projectId}/OverallResponseRate

        Returns a ResponseRate
        """
        if return_type and join:
            raise SyntaxError("Cannot use both return_type and join arguments")

        return PandanatedList(
            OverallResponseRate,
            self._requester,
            "GET",
            "projects/{}/OverallResponseRate".format(self.id),
            filters=filters,
            context=self,
            return_type=return_type,
            join=join,
        )

    def get_raw_data(self, filters=None, **kwargs):
        """
        Gets response rates for a project for the account.

        GET /api/projects/{projectId}/general/rawData

        Returns a PandanatedList of RawDataGeneral
        """

        return PandanatedList(
            RawDataGeneral,
            self._requester,
            "GET",
            "projects/{}/general/rawData".format(self.id),
            filters=filters,
            context=self,
            _kwargs=combine_kwargs(**kwargs),
        )

    # format is "Other Class": {"column from other class" : "column from current class"}
    _shared_columns = {
        "Course": {"courseId": "id"},
        "OverallResponseRate": {"id": "projectId"},
        "ProjectSurvey": {"id": "projectId"},
        "RawDataGeneral": {"id": "projectId"},
        "ResponseRate": {"id": "projectId"},
        "NonRespondent": {"id": "projectId"},
        "Respondent": {"id": "projectId"},
        "ProjectCourse": {"id": "projectId"},
    }
