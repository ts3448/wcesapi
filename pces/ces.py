from typing import Annotated, TypeAlias
import warnings
import logging

from account import Account
from course import Course
from node import Node
from node_mapper import NodeMapper
from project import Project
from requester import Requester, MaxRetries, RetryBackoff, RateLimitDelay
from survey import Survey
from term import Term
from user import User
from metadata import Metadata
from utilities import combine_kwargs


logger = logging.getLogger(__name__)

BaseURL: TypeAlias = Annotated[str, "The base URL of the CES instance being accessed"]
AccessToken: TypeAlias = Annotated[str, "The API key used to authenticate requests"]


class CES:
    """
    The main class to be instantiated to provide access to CES's API.
    """

    def __init__(
        self,
        base_url: BaseURL,
        access_token: AccessToken,
        max_retries: MaxRetries = None,
        retry_backoff: RetryBackoff = None,
        rate_limit_delay: RateLimitDelay = None,
    ) -> None:
        """Initialize the CES instance."""
        self._validate_base_url(base_url)
        clean_base_url = self._clean_url(base_url)
        clean_access_token = access_token.strip()

        self._requester = Requester(
            base_url=clean_base_url,
            access_token=clean_access_token,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            rate_limit_delay=rate_limit_delay,
        )
        logger.info(f"CES instance initialized with base URL: {clean_base_url}")

    @staticmethod
    def _validate_base_url(base_url: BaseURL) -> None:
        """
        Validate the given base URL.

        This method checks for common issues with the base URL:
        - Ensures the URL is not empty
        - Checks for the presence of a scheme (http:// or https://)
        - Verifies that 'api/' is not included in the URL
        - Warns if HTTP is used instead of HTTPS

        Args:
            base_url (BaseURL): The base URL to validate.

        Raises:
            ValueError: If the URL is empty, lacks a scheme, or includes 'api/'.

        Warns:
            If the URL uses HTTP instead of HTTPS.
        """
        if not base_url:
            raise ValueError(
                "CES needs a valid URL, please provide a non-blank 'base_url'."
            )
        if "://" not in base_url:
            raise ValueError(
                "An invalid `base_url` for the CES API Instance was used. Please provide a valid HTTP or HTTPS URL."
            )
        if "api/" in base_url:
            raise ValueError(
                "`base_url` should not specify API. Remove 'api/' from the URL."
            )
        if base_url.startswith("http://"):
            warnings.warn(
                "CES may respond unexpectedly when making requests to HTTP URLs. If possible, please use HTTPS."
            )

    @staticmethod
    def _clean_url(base_url: BaseURL) -> BaseURL:
        """
        Clean up a given base URL.

        This method performs the following cleanup operations:
        - Removes leading and trailing whitespace
        - Removes trailing forward slashes

        Args:
            base_url (BaseURL): The base URL to clean.

        Returns:
            BaseURL: The cleaned base URL.
        """
        return base_url.strip().rstrip("/")


    def set_retry_options(
        self, max_retries: MaxRetries, retry_backoff: RetryBackoff
    ) -> None:
        """Set retry options for the requester."""
        self._requester.set_retry_options(max_retries, retry_backoff)


    def set_rate_limit_delay(self, rate_limit_delay: RateLimitDelay) -> None:
        """Set rate limit delay for the requester."""
        self._requester.set_rate_limit_delay(rate_limit_delay)


    def get_account(self) -> "Account":
        """Gets the account for your token."""

        return Account(self._requester, "GET", "account")


    def list_subaccounts(self) -> Account:
        """Gets a list of subaccounts for the account."""

        api_endpoint = "subAccounts"

        return Account(self._requester, "GET", api_endpoint)

    def list_terms(self) -> Term:
        """Gets a list of terms for the account."""

        api_endpoint = "terms"

        return Term(self._requester, "GET", api_endpoint)

    def user_has_in_progress_survey(self, username: str) -> bool:
        """Checks if user has in-progress survey for all projects in the account."""

        api_endpoint = "users/hasInProgressSurvey"
        params = {"username": username}

        response = self._requester.request("GET", api_endpoint, params)

        return response.get("result", False)

    def user_has_grade_block(self, username: str) -> bool:
        """Checks if user has in-progress survey in all course project with active grades blocked."""

        api_endpoint = "users/hasGradeBlock"
        params = {"username": username}

        response = self._requester.request("GET", api_endpoint, params)

        return response.get("result", False)
    
    def list_surveys(self) -> Survey:
        """Gets a list of surveys for the Accounts."""
        
        api_endpoint = "surveys"
        
        return Survey(self._requester, "GET", api_endpoint)
    
    def list_projects(self, project_type: Optional[int] = None, project_status: Optional[int] = None, 
                      ended_since: Optional[datetime] = None, include_subaccounts: Optional[bool] = None) -> Project:
        """List all the projects for an account, filter by project type status, or ended since."""
        
        api_endpoint = "projects"
        
        params = {
            'projectType': project_type,
            'projectStatus': project_status,
            'endedSince': ended_since.isoformat() if ended_since else None,
            'includeSubaccounts': include_subaccounts
        }
        
        return Project(self._requester, "GET", api_endpoint, **params)

    def get_project(self, project_id: int) -> Project:
        """Gets a single project for the account."""
        
        api_endpoint = f"projects/{project_id}"
        
        return Project(self._requester, "GET", api_endpoint)
    
    def create_project(self, account_id: Optional[int] = None, title: Optional[str] = None, 
                       project_type: int, project_status: int, main_survey_id: Optional[int] = None, 
                       term_id: Optional[int] = None, start_date: datetime, end_date: datetime) -> Project:
        """Creates a new project in the Accounts."""
        api_endpoint = "projects"
        data = {
            'accountId': account_id,
            'title': title,
            'projectType': project_type,
            'projectStatus': project_status,
            'mainSurveyId': main_survey_id,
            'termId': term_id,
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat()
        }
        return Project(self._requester, "POST", api_endpoint, data=data)

    def list_courses(self) -> Course:
        """Gets a list of project courses for the account."""
        
        api_endpoint = "courses"
        
        return Course(self._requester, "GET", api_endpoint)

    def get_course(self, id: int | str, use_unique_id: bool=False) -> Course:
        """Gets a course for the account by course id or course uniqueid."""

        if use_unique_id:
            params = {'uniqueId': id}
            api_endpoint = "courses"
        else:
            api_endpoint = f"courses/{id}"
            params = None

        return Course(self._requester, "GET", api_endpoint, params)

    def list_account_users(self, user_types: Optional[str] = None, username: Optional[str] = None, 
                           user_id: Optional[int] = None, include_subaccounts: Optional[bool] = None) -> User:
        """Gets a list of users in the account."""
        
        api_endpoint = "users"
        
        params = {
            'userTypes': user_types,
            'username': username,
            'userId': user_id,
            'includeSubaccounts': include_subaccounts
        }
        
        return User(self._requester, "GET", api_endpoint, **params)

    def list_user_metadata(self, username: str) -> Metadata:
        """Gets a list of metadata for the account by course."""

        api_endpoint = "users/metadata"

        return Metadata(self._requester, "GET", api_endpoint, username=username)

    def save_user_metadata(self, username: str, name: str, value: str) -> Metadata:
        """Create or update user metadata."""

        api_endpoint = "users/metadata"

        data = {'name': name, 'value': value}

        return Metadata(self._requester, "POST", api_endpoint, username=username, data=data)

    def save_user_metadata_batch(self, username: str, metadata: list[dict[str, str]]) -> Metadata:
        """Create or update user metadata by uploading multiple metadata as a batch."""

        api_endpoint = "users/metadata-batch"

        return Metadata(self._requester, "POST", api_endpoint, username=username, data={'metadata': metadata})

    def remove_user_metadata(self, username: str, name: str) -> None:
        """Removes a user metadata by name in the account."""

        api_endpoint = "users/metadata"

        self._requester.request("DELETE", api_endpoint, params={"username": username, "name": name})

    def create_admin_user(self, username: str, user_type: int, user_types: list[int], first_name: str, 
                          last_name: str, email: str, roles: list[int], node_path: list[str], 
                          user_id: Optional[int] = None, account_id: Optional[int] = None, 
                          password: Optional[str] = None) -> User:
        """Creates an admin user in the account."""
        
        api_endpoint = "users/administrator"
        
        data = {
            'userId': user_id,
            'accountId': account_id,
            'username': username,
            'userType': user_type,
            'userTypes': user_types,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'password': password,
            'roles': roles,
            'nodePath': node_path
        }
        return User(self._requester, "POST", api_endpoint, data=data)

    def update_admin_user(self, username: str, user_type: int, user_types: list[int], first_name: str, 
                          last_name: str, email: str, roles: list[int], node_path: list[str], 
                          user_id: Optional[int] = None, account_id: Optional[int] = None, 
                          password: Optional[str] = None) -> User:
        """Updates an admin user in the account."""
        api_endpoint = "users/administrator"
        data = {
            'userId': user_id,
            'accountId': account_id,
            'username': username,
            'userType': user_type,
            'userTypes': user_types,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'password': password,
            'roles': roles,
            'nodePath': node_path
        }
        return User(self._requester, "PUT", api_endpoint, data=data)

    def get_nodes(self) -> Node:
        """Gets list of nodes."""
        api_endpoint = "nodes"
        return Node(self._requester, "GET", api_endpoint)

    def get_node(self, node_id: int) -> Node:
        """Gets a single node."""
        api_endpoint = f"nodes/{node_id}"
        return Node(self._requester, "GET", api_endpoint)

    def create_node(self, parent_id: int, account_id: int, name: str, level: Optional[int] = None, 
                    node_path: Optional[str] = None) -> Node:
        """Creates a node in the account."""
        api_endpoint = "node"
        data = {
            'parentId': parent_id,
            'accountId': account_id,
            'level': level,
            'name': name,
            'nodePath': node_path
        }
        return Node(self._requester, "POST", api_endpoint, data=data)

    def update_node(self, node_id: int, parent_id: int, account_id: int, name: str, 
                    level: Optional[int] = None, node_path: Optional[str] = None) -> Node:
        """Updates a node in the account."""
        api_endpoint = f"node/{node_id}"
        data = {
            'id': node_id,
            'parentId': parent_id,
            'accountId': account_id,
            'level': level,
            'name': name,
            'nodePath': node_path
        }
        return Node(self._requester, "PUT", api_endpoint, data=data)

    def delete_node(self, node_id: int) -> None:
        """Deletes a node in the account."""
        api_endpoint = f"node/{node_id}"
        self._requester.request("DELETE", api_endpoint)

    def get_node_mapper(self, node_mapper_id: int) -> NodeMapper:
        """Gets a single NodeMapper."""
        api_endpoint = f"nodemapper/{node_mapper_id}"
        return NodeMapper(self._requester, "GET", api_endpoint)

    def create_node_mapper(self, node_mapper: dict) -> NodeMapper:
        """Creates a NodeMapper in node."""
        api_endpoint = "nodemapper"
        return NodeMapper(self._requester, "POST", api_endpoint, data={'nodeMapper': node_mapper})

    def update_node_mapper(self, node_mapper_id: int, node_mapper: dict) -> NodeMapper:
        """Updates a NodeMapper in the node."""
        api_endpoint = f"nodemapper/{node_mapper_id}"
        return NodeMapper(self._requester, "PUT", api_endpoint, data={'nodeMapper': node_mapper})

    def delete_node_mapper(self, node_mapper_id: int) -> None:
        """Deletes a NodeMapper in the account."""
        api_endpoint = f"nodemapper/{node_mapper_id}"
        self._requester.request("DELETE", api_endpoint)


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
            self._requester,
            "GET",
            "subAccounts",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs),
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
            self._requester,
            "GET",
            "terms",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs),
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

        response = self._requester.request(
            "GET", "users/hasInProgressSurvey?username={}".format(username)
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

        response = self._requester.request(
            "GET", "users/hasGradeBlock?username={}".format(username)
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
            self._requester,
            "GET",
            "surveys",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs),
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
            _kwargs=combine_kwargs(**kwargs),
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

        response = self._requester.request("GET", "projects/{}".format(id))
        return Project(self._requester, response.json())

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
            self._requester,
            "GET",
            "users",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs),
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
            self._requester,
            "GET",
            "users/metadata?username={}".format(username),
            filters=filters,
            _kwargs=combine_kwargs(**kwargs),
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
            self._requester,
            "GET",
            "nodes",
            filters=filters,
            _kwargs=combine_kwargs(**kwargs),
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

        response = self._requester.request("GET", "nodes/{}".format(id))
        return Node(self._requester, response.json())

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

        response = self._requester.request("GET", "nodemapper/{}".format(id))
        return NodeMapper(self._requester, response.json())
