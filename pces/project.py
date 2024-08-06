from datetime import datetime
from typing import Optional
from pces.ces_object import CESObject
from pces.nonrespondent import NonRespondent
from pces.project_survey import ProjectSurvey
from pces.project_course import ProjectCourse
from pces.respondent import Respondent
from pces.response_rate import NodeResponseRate, ResponseRate, OverallResponseRate
from pces.raw_data import RawDataGeneral


class Project(CESObject):
    """
    Represents a Project in the CES system.
    """

    def __str__(self):
        return f"{self.title} ({self.id})"

    def list_project_surveys(self):
        """
        Gets a list of surveys for the project.

        Returns:
            ProjectSurvey: A ProjectSurvey object representing the retrieved surveys.
        """
        api_endpoint = f"projects/{self.id}/surveys"
        return ProjectSurvey(self._requester, "GET", api_endpoint)

    def list_project_courses(self):
        """
        Gets a list of courses for the project.

        Returns:
            ProjectCourse: A ProjectCourse object representing the retrieved project courses.
        """
        api_endpoint = f"projects/{self.id}/courses"
        return ProjectCourse(self._requester, "GET", api_endpoint)

    def get_project_course(self, course_id: int):
        """
        Gets a course in a project for the account.

        Args:
            course_id (int): The ID of the course.

        Returns:
            ProjectCourse: A ProjectCourse object representing the retrieved project course.
        """
        api_endpoint = f"projects/{self.id}/courses/{course_id}"
        return ProjectCourse(self._requester, "GET", api_endpoint)

    def list_project_courses_by_canvas_course_sis_id(self, canvas_course_sis_id: str):
        """
        Gets a list of courses for a project by Canvas Course SIS ID.

        Args:
            canvas_course_sis_id (str): The Canvas Course SIS ID.

        Returns:
            ProjectCourse: A ProjectCourse object representing the retrieved project courses.
        """
        api_endpoint = f"projects/{self.id}/courses/canvascourse/{canvas_course_sis_id}"
        return ProjectCourse(self._requester, "GET", api_endpoint)

    def list_project_courses_by_canvas_section_sis_id(self, canvas_section_sis_id: str):
        """
        Gets a list of courses for a project by Canvas Section SIS ID.

        Args:
            canvas_section_sis_id (str): The Canvas Section SIS ID.

        Returns:
            ProjectCourse: A ProjectCourse object representing the retrieved project courses.
        """
        api_endpoint = (
            f"projects/{self.id}/courses/canvassection/{canvas_section_sis_id}"
        )
        return ProjectCourse(self._requester, "GET", api_endpoint)

    def create_project_course(
        self,
        node_id: int,
        code: str,
        title: str,
        unique_id: str,
        node_path: Optional[str] = None,
        crosslist_unique_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        admin_report_access_start_date: Optional[datetime] = None,
        admin_report_access_end_date: Optional[datetime] = None,
        instructor_report_access_start_date: Optional[datetime] = None,
        instructor_report_access_end_date: Optional[datetime] = None,
        ta_report_access_start_date: Optional[datetime] = None,
        ta_report_access_end_date: Optional[datetime] = None,
        custom_question_start_date: Optional[datetime] = None,
        custom_question_end_date: Optional[datetime] = None,
    ):
        """
        Creates a new project course in the account.

        Args:
            node_id (int): The node ID.
            code (str): The course code.
            title (str): The course title.
            unique_id (str): The unique ID of the course.
            node_path (Optional[str], optional): The node path. Defaults to None.
            crosslist_unique_id (Optional[str], optional): The crosslist unique ID. Defaults to None.
            start_date (Optional[datetime], optional): The start date. Defaults to None.
            end_date (Optional[datetime], optional): The end date. Defaults to None.
            admin_report_access_start_date (Optional[datetime], optional): The admin report access start date. Defaults to None.
            admin_report_access_end_date (Optional[datetime], optional): The admin report access end date. Defaults to None.
            instructor_report_access_start_date (Optional[datetime], optional): The instructor report access start date. Defaults to None.
            instructor_report_access_end_date (Optional[datetime], optional): The instructor report access end date. Defaults to None.
            ta_report_access_start_date (Optional[datetime], optional): The TA report access start date. Defaults to None.
            ta_report_access_end_date (Optional[datetime], optional): The TA report access end date. Defaults to None.
            custom_question_start_date (Optional[datetime], optional): The custom question start date. Defaults to None.
            custom_question_end_date (Optional[datetime], optional): The custom question end date. Defaults to None.

        Returns:
            ProjectCourse: A ProjectCourse object representing the newly created project course.
        """
        api_endpoint = f"projects/{self.id}/courses"
        data = {
            "nodeId": node_id,
            "code": code,
            "title": title,
            "uniqueId": unique_id,
            "nodePath": node_path,
            "crosslistUniqueId": crosslist_unique_id,
            "startDate": start_date,
            "endDate": end_date,
            "adminReportAccessStartDate": admin_report_access_start_date,
            "adminReportAccessEndDate": admin_report_access_end_date,
            "instructorReportAccessStartDate": instructor_report_access_start_date,
            "instructorReportAccessEndDate": instructor_report_access_end_date,
            "taReportAccessStartDate": ta_report_access_start_date,
            "taReportAccessEndDate": ta_report_access_end_date,
            "customQuestionStartDate": custom_question_start_date,
            "customQuestionEndDate": custom_question_end_date,
        }
        return ProjectCourse(self._requester, "POST", api_endpoint, data=data)

    def update_project_course(
        self,
        course_id: int,
        node_id: int,
        code: str,
        title: str,
        unique_id: str,
        node_path: Optional[str] = None,
        crosslist_unique_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        admin_report_access_start_date: Optional[datetime] = None,
        admin_report_access_end_date: Optional[datetime] = None,
        instructor_report_access_start_date: Optional[datetime] = None,
        instructor_report_access_end_date: Optional[datetime] = None,
        ta_report_access_start_date: Optional[datetime] = None,
        ta_report_access_end_date: Optional[datetime] = None,
        custom_question_start_date: Optional[datetime] = None,
        custom_question_end_date: Optional[datetime] = None,
    ):
        """
        Updates an existing project course in the account.

        Args:
            course_id (int): The ID of the course.
            node_id (int): The node ID.
            code (str): The course code.
            title (str): The course title.
            unique_id (str): The unique ID of the course.
            node_path (Optional[str], optional): The node path. Defaults to None.
            crosslist_unique_id (Optional[str], optional): The crosslist unique ID. Defaults to None.
            start_date (Optional[datetime], optional): The start date. Defaults to None.
            end_date (Optional[datetime], optional): The end date. Defaults to None.
            admin_report_access_start_date (Optional[datetime], optional): The admin report access start date. Defaults to None.
            admin_report_access_end_date (Optional[datetime], optional): The admin report access end date. Defaults to None.
            instructor_report_access_start_date (Optional[datetime], optional): The instructor report access start date. Defaults to None.
            instructor_report_access_end_date (Optional[datetime], optional): The instructor report access end date. Defaults to None.
            ta_report_access_start_date (Optional[datetime], optional): The TA report access start date. Defaults to None.
            ta_report_access_end_date (Optional[datetime], optional): The TA report access end date. Defaults to None.
            custom_question_start_date (Optional[datetime], optional): The custom question start date. Defaults to None.
            custom_question_end_date (Optional[datetime], optional): The custom question end date. Defaults to None.

        Returns:
            ProjectCourse: A ProjectCourse object representing the updated project course.
        """
        api_endpoint = f"projects/{self.id}/courses/{course_id}"
        data = {
            "nodeId": node_id,
            "code": code,
            "title": title,
            "uniqueId": unique_id,
            "nodePath": node_path,
            "crosslistUniqueId": crosslist_unique_id,
            "startDate": start_date.isoformat() if start_date else None,
            "endDate": end_date.isoformat() if end_date else None,
            "adminReportAccessStartDate": (
                admin_report_access_start_date.isoformat()
                if admin_report_access_start_date
                else None
            ),
            "adminReportAccessEndDate": (
                admin_report_access_end_date.isoformat()
                if admin_report_access_end_date
                else None
            ),
            "instructorReportAccessStartDate": (
                instructor_report_access_start_date.isoformat()
                if instructor_report_access_start_date
                else None
            ),
            "instructorReportAccessEndDate": (
                instructor_report_access_end_date.isoformat()
                if instructor_report_access_end_date
                else None
            ),
            "taReportAccessStartDate": (
                ta_report_access_start_date.isoformat()
                if ta_report_access_start_date
                else None
            ),
            "taReportAccessEndDate": (
                ta_report_access_end_date.isoformat()
                if ta_report_access_end_date
                else None
            ),
            "customQuestionStartDate": (
                custom_question_start_date.isoformat()
                if custom_question_start_date
                else None
            ),
            "customQuestionEndDate": (
                custom_question_end_date.isoformat()
                if custom_question_end_date
                else None
            ),
        }
        return ProjectCourse(self._requester, "PUT", api_endpoint, data=data)

    def remove_project_course(self, course_id: int):
        """
        Removes a project course for the account.

        Args:
            course_id (int): The ID of the course.

        Returns:
            dict: The response from the API after removing the project course.
        """
        api_endpoint = f"projects/{self.id}/courses/{course_id}"
        return self._requester.request("DELETE", api_endpoint)

    def list_respondents(self):
        """
        Gets a list of respondents by project.

        Returns:
            Respondent: A Respondent object representing the retrieved respondents.
        """
        api_endpoint = f"projects/{self.id}/respondents"
        return Respondent(self._requester, "GET", api_endpoint)

    def list_non_respondents(self):
        """
        Gets a list of non-respondents by project.

        Returns:
            NonRespondent: A NonRespondent object representing the retrieved non-respondents.
        """
        api_endpoint = f"projects/{self.id}/nonRespondents"
        return NonRespondent(self._requester, "GET", api_endpoint)

    def get_response_rate(self):
        """
        Gets the response rate by project.

        Returns:
            ResponseRate: A ResponseRate object representing the retrieved response rate.
        """
        api_endpoint = f"projects/{self.id}/responseRate"
        return ResponseRate(self._requester, "GET", api_endpoint)

    def get_overall_response_rate(self):
        """
        Gets the overall project response rate.

        Returns:
            OverallResponseRate: An Overal ResponseRate object representing the overall project response rate.
        """
        api_endpoint = f"projects/{self.id}/OverallResponseRate"
        return OverallResponseRate(self._requester, "GET", api_endpoint)

    def get_node_response(self):
        """
        Gets the node response rate by project.

        Returns:
            ResponseRate: A ResponseRate object representing the node response rate by project.
        """
        api_endpoint = f"projects/{self.id}/NodeResponseRateByProject"
        return NodeResponseRate(self._requester, "GET", api_endpoint)

    def get_raw_data(self):
        """
        Gets the raw data by general project.

        Returns:
            RawDataGeneral: A RawDataGeneral object representing the raw data by general project.
        """
        api_endpoint = f"projects/{self.id}/general/rawData"
        return RawDataGeneral(self._requester, "GET", api_endpoint)
