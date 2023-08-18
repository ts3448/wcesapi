import warnings
from survey import Survey
from requester import Requester
from utilities import clean_url, combine_kwargs
from project import Project
from paginated_list import PaginatedList
from account import Account
from term import Term
from course import Course
from user import User


class CES(object):
    """
    The main class to be instantiated to provide access to Canvas's API.
    """

    def __init__(self, base_url, access_token):
        """
        :param base_url: The base URL of the CES instance's API.
        :type base_url: str
        :param access_token: The API key to authenticate requests with.
        :type access_token: str
        """
        if "api/v1" in base_url:
            raise ValueError(
                "`base_url` should not specify an API version. Remove trailing /api/v1/"
            )

        if "http://" in base_url:
            warnings.warn(
                "Canvas may respond unexpectedly when making requests to HTTP "
                "URLs. If possible, please use HTTPS."
            )

        if not base_url.strip():
            warnings.warn(
                "Canvas needs a valid URL, please provide a non-blank `base_url`."
            )

        if "://" not in base_url:
            warnings.warn(
                "An invalid `base_url` for the Canvas API Instance was used. "
                "Please provide a valid HTTP or HTTPS URL if possible."
            )

        # Ensure that the user-supplied access token and base_url contain no leading or
        # trailing spaces that might cause issues when communicating with the API.
        access_token = access_token.strip()
        base_url = clean_url(base_url)

        self.__requester = Requester(base_url, access_token)

    def get_account(self, **kwargs):
        """
        Gets the account for your token.

        GET /api/account

        Returns an Account

        """
        response = self.__requester.request(
            "GET",
            "account",
            _kwargs=combine_kwargs(**kwargs)
        )
        return Account(self.__requester, response.json())

    def get_course(self, id, use_unique_id=False, **kwargs):
        """
        Gets the account for your token.

        GET /api/courses?uniqueId={uniqueId}
        OR
        GET /api/courses/{id}

        Returns a Course

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

        GET /api/courses

        Returns a PaginatedList of Courses
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

        GET /api/subAccounts

        Returns a PaginatedList of Accounts
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

        GET /api/terms

        Returns a PaginatedList of Terms
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


        GET /api/users/hasInProgressSurvey?username={username}

        Returns a bool
        """
        response = self.__requester.request(
            "GET",
            "users/hasInProgressSurvey?username={}".format(username)
            )
        return bool(response.json["result"])

    def user_has_grade_block(self, username):
        """
        User has in-progress survey in all course project with active grades blocked.

        GET /api/users/hasGradeBlock?username={username}

        Returns a bool
        """
        response = self.__requester.request(
            "GET",
            "users/hasGradeBlock?username={}".format(username)
            )
        return bool(response.json["result"])

    def get_surveys(self, filters=None, **kwargs):
        """
        Gets a list of surveys for the Account.

        GET /api/surveys

        Returns a PaginatedList of Surveys
        """

        return PaginatedList(
            Survey,
            self.__requester,
            "GET",
            "surveys",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_project(self, id, **kwargs):
        """
        Gets a single project for the account.

        GET /api/projects/{id}

        Returns a Project
        """
        response = self.__requester.request(
            "GET",
            "projects/{}".format(id),
            _kwargs=combine_kwargs(**kwargs)
        )
        return Project(self.__requester, response.json())

    def get_projects(self, filters=None, **kwargs):
        """
        Retrieve a project by its ID.

        :calls: `GET /api/projects/:id \

        :param course: The object or ID of the project to retrieve.


        :rtype: :project:`pces.project.Project`
        """

        return PaginatedList(
            Project,
            self.__requester,
            "GET",
            "projects",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )
    
    def get_users(self, filters=None, **kwargs):
        """
        Gets a list of users in the account

        GET /api/users

        Returns a PaginatedList of Users
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

        GET /api/users/metadata?username={username}&page={page}

        Returns a Metadata
        """
        response = self.__requester.request(
            "GET",
            "users/metadata?username={}".format(username),
            _kwargs=combine_kwargs(**kwargs)
        )
        return User(self.__requester, response.json())