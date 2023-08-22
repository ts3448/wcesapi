import warnings

from pces.account import Account
from pces.course import Course
from pces.node import Node
from pces.node_mapper import NodeMapper
from pces.pandanated_list import PandanatedList
from pces.project import Project
from pces.requester import Requester
from pces.survey import Survey
from pces.term import Term
from pces.user import User
from pces.metadata import Metadata
from pces.utilities import clean_url, combine_kwargs


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

        self._requester = Requester(base_url, access_token)

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

    def get_course(self, id, use_unique_id=False):
        """
        Gets a course for the account by course id
        or course uniqueid.


        API calls:
            GET /api/courses?uniqueId={uniqueId}
            GET /api/courses/{id}

        Arguments:
            id (int OR str): the id or unique id of the course to find.

            use_unique_id (bool): whether or not to use the unique id.
                Defaults to "False".

        Returns:
            Course
        """
        kwargs = {}
        if use_unique_id:
            kwargs["uniqueId"] = id
            url = "courses"
        else:
            url = "courses/{}".format(id)

        response = self.__requester.request(
            "GET",
            url,
            _kwargs=combine_kwargs(kwargs)
        )
        return Course(self.__requester, response.json())

    def get_courses(self, filters=None, **kwargs):
        """
        Gets a list of project courses for the account.

        API call:
            GET /api/courses

        Params:
            filters (dict): attributes and values to apply as a filter.

            **kwargs (dict): see API documentation for optional arguments.

        Returns:
            PandanatedList(Courses)
        """

        return PandanatedList(
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

        Params:
            filters (dict): attributes and values to apply as a filter.

            **kwargs (dict): see API documentation for optional arguments.

        Returns:
            PandanatedList(Account)
        """

        return PandanatedList(
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

        Params:
            filters (dict): attributes and values to apply as a filter.

            **kwargs (dict): see API documentation for optional arguments.

        Returns:
            PandanatedList(Term)
        """

        return PandanatedList(
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

        Params:
            username (string): username of account to search

        Returns:
            bool: True if the user has a survey in progress.
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

        Params:
            username (string): username of account to search

        Returns:
            bool: True if the user has in-progress survey in all
            course project with active grades blocked.
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

        Params:
            filters (dict): attributes and values to apply as a filter.

            **kwargs (dict): see API documentation for optional arguments.

        Returns:
            PandanatedList(Surveys)
        """

        return PandanatedList(
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

        Params:
            filters (dict): attributes and values to apply as a filter.

            **kwargs (dict): see API documentation for optional arguments.

        Returns:
            PandanatedList(Projects)
        """

        return PandanatedList(
            Project,
            self._requester,
            "GET",
            "projects",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_project(self, id):
        """
        Gets a single project for the account.

        API call:
            GET /api/projects/{id}

        Params:
            id (int): id of a project.

        Return:
            Project
        """

        response = self.__requester.request(
            "GET",
            "projects/{}".format(id)
        )
        return Project(self.__requester, response.json())

    def get_users(self, filters=None, **kwargs):
        """
        Gets a list of users in the account

        API call:
            GET /api/users

        Params:
            filters (dict): attributes and values to apply as a filter.

            **kwargs (dict): see API documentation for optional arguments.

        Return:
            PandanatedList(User)
        """

        return PandanatedList(
            User,
            self.__requester,
            "GET",
            "users",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_user_metadata(self, username, filters=None, **kwargs):
        """
        Gets a list of metadata for the user by course.

        API call:
            GET /api/users/metadata

        Params:
            filters (dict): attributes and values to apply as a filter.

            **kwargs (dict): see API documentation for optional arguments.

        Returns:
            PandanatedList(Metadata)
        """

        return PandanatedList(
            Metadata,
            self.__requester,
            "GET",
            "users/metadata?username={}".format(username),
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_nodes(self, filters=None, **kwargs):
        """
        Gets list of nodes.

        API call:
            GET /api/nodes

        Params:
            filters (dict): attributes and values to apply as a filter.

            **kwargs (dict): see API documentation for optional arguments.

        Returns:
            PandanatedList(Nodes)
        """

        return PandanatedList(
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

        API call:
            GET /api/nodes/{id}

        Params:
            id (int): id of the node.

        Returns:
            Node
        """

        response = self.__requester.request(
            "GET",
            "nodes/{}".format(id)
        )
        return Node(self.__requester, response.json())

    def get_node_mapper(self, id):
        """
        Gets a single NodeMapper.

        API call:
            GET /api/nodes

        Params:
            id (int): id of the node mapper

        Returns:
            NodeMapper
        """

        response = self.__requester.request(
            "GET",
            "nodemapper/{}".format(id)
        )
        return NodeMapper(self.__requester, response.json())
