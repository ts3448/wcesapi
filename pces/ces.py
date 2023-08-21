import warnings

from account import Account
from course import Course
from node import Node
from node_mapper import NodeMapper
from paginated_list import PaginatedList
from project import Project
from requester import Requester
from survey import Survey
from term import Term
from user import User
from utilities import clean_url, combine_kwargs


class CES(object):
    """
    The main class to be instantiated to provide access to CES's API.
    """

    def __init__(self, base_url, access_token):
        """
        Params:
            base_url (str): The base URL of the CES instance being accessed.

            access_token (str): The API key used to authenticate requests.
        """

        if "api/" in base_url:
            raise ValueError(
                "`base_url` should not specify API. Remove trailing /api/"
            )

        if "http://" in base_url:
            warnings.warn(
                "CES may respond unexpectedly when making requests to HTTP "
                "URLs. If possible, please use HTTPS."
            )

        if not base_url.strip():
            warnings.warn(
                "CES needs a valid URL, please provide a non-blank 'base_url'."
            )

        if "://" not in base_url:
            warnings.warn(
                "An invalid `base_url` for the Canvas API Instance was used. "
                "Please provide a valid HTTP or HTTPS URL if possible."
            )

        # Ensure that the user-supplied access token and base_url
        # contain no leading or trailing spaces that might cause issues
        # when communicating with the API.
        access_token = access_token.strip()
        base_url = clean_url(base_url)

        self.__requester = Requester(base_url, access_token)

    def get_account(self):
        """
        Gets the account for your token.

        GET /api/account

        Returns:
            Account
        """

        response = self.__requester.request(
            "GET",
            "account"
            )
        return Account(self.__requester, response.json())

    def get_course(self, id, use_unique_id=False, **kwargs):
        """
        Gets a course for the account by course id
        or course uniqueid.


        API calls:
            GET /api/courses?uniqueId={uniqueId}
            GET /api/courses/{id}

        Returns:
            Course
        """

        if use_unique_id:
            kwargs["uniqueId"] = id
            url = "courses"
        else:
            url = "courses/{}".format(id)

        response = self.__requester.request(
            "GET",
            url,
            _kwargs=combine_kwargs(**kwargs)
        )
        return Course(self.__requester, response.json())

    def get_courses(self, filters=None, **kwargs):
        """
        Gets a list of project courses for the account.

        API call:
            GET /api/courses

        Optional parameters (kwargs):
            page (int)

        Returns:
            PaginatedList(Courses)
        """

        return PaginatedList(
            Course,
            self.__requester,
            "GET",
            "courses",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_subaccounts(self, filters=None, **kwargs):
        """
        Gets a list of subaccounts for the account.

        API call:
            GET /api/subAccounts

        Optional parameters (kwargs):
            page (int)

        Returns a PaginatedList of Accounts.
        """

        return PaginatedList(
            Account,
            self.__requester,
            "GET",
            "subAccounts",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_terms(self, filters=None, **kwargs):
        """
        Gets a list of terms for the account.

        API call:
            GET /api/terms

        Optional parameters (kwargs):
            page (int)

        Returns a PaginatedList of Terms.
        """

        return PaginatedList(
            Term,
            self.__requester,
            "GET",
            "terms",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def user_has_in_progress_survey(self, username):
        """
        User has in-progress survey for all projects in the account.

        API call:
            GET /api/users/hasInProgressSurvey?username={username}

        Returns a bool.
        """

        response = self.__requester.request(
            "GET",
            "users/hasInProgressSurvey?username={}".format(username)
            )
        return bool(response.json["result"])

    def user_has_grade_block(self, username):
        """
        User has in-progress survey in all course project with
        active grades blocked.

        API call:
            GET /api/users/hasGradeBlock?username={username}

        Returns a bool.
        """

        response = self.__requester.request(
            "GET",
            "users/hasGradeBlock?username={}".format(username)
            )
        return bool(response.json["result"])

    def get_surveys(self, filters=None, **kwargs):
        """
        Gets a list of surveys for the Account.

        API call:
            GET /api/surveys

        Optional parameters (kwargs):
            page (int)

        Returns a PaginatedList of Surveys.
        """

        return PaginatedList(
            Survey,
            self.__requester,
            "GET",
            "surveys",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_projects(self, filters=None, **kwargs):
        """
        List all the projects for an account, filter by project type status,
        or ended since.

        API call:
            GET /api/projects

        Optional parameters (kwargs):
            projectType (int)
                1 = Course, 2 = General
            projectStatus (int)
                1 = Not-Deployed, 2 = Deployed-NotStarted,
                3 = In-Progress, 4 = Ended
            endedSince (str)
                If this argument is set, the response will only include
                projects that were ended after the specified DateTime.
                The value must be formatted as ISO 8601 YYYY-MM-DDTHH:MM:SSZ.
            page (int)
            includeSubaccounts (bool)

        Returns a PaginatedList of Projects.
        """

        return PaginatedList(
            Project,
            self.__requester,
            "GET",
            "projects",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_project(self, id, **kwargs):
        """
        Gets a single project for the account.

        API call:
            GET /api/projects/{id}

        Returns a Project.
        """

        response = self.__requester.request(
            "GET",
            "projects/{}".format(id),
            _kwargs=combine_kwargs(**kwargs)
        )
        return Project(self.__requester, response.json())

    def get_users(self, filters=None, **kwargs):
        """
        Gets a list of users in the account

        GET /api/users

        Returns a PaginatedList of Users.
        """

        return PaginatedList(
            User,
            self.__requester,
            "GET",
            "users",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_user_metadata(self, username, **kwargs):
        """
        Gets a list of metadata for the account by course.

        GET /api/users/metadata

        Returns a Metadata.
        """
        response = self.__requester.request(
            "GET",
            "users/metadata?username={}".format(username),
            _kwargs=combine_kwargs(**kwargs)
        )
        return User(self.__requester, response.json())

    def get_nodes(self, filters=None, **kwargs):
        """
        Gets list of nodes.

        GET /api/nodes

        Returns a PaginatedList of Nodes.
        """

        return PaginatedList(
            Node,
            self.__requester,
            "GET",
            "nodes",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_node(self, id):
        """
        Gets a node.

        GET /api/nodes/{id}

        Returns a single Nodes.
        """

        response = self.__requester.request(
            "GET",
            "nodes/{}".format(id)
        )
        return Node(self.__requester, response.json())

    def get_node_mapper(self, id):
        """
        Gets a single NodeMapper.

        GET /api/nodes

        Returns a single NodeMapper.
        """

        response = self.__requester.request(
            "GET",
            "nodemapper/{}".format(id)
        )
        return NodeMapper(self.__requester, response.json())
