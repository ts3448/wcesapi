from datetime import datetime
from typing import Any, Optional
import warnings
import logging

from wcesapi.account import Account
from wcesapi.course import Course
from wcesapi.node import Node
from wcesapi.node_mapper import NodeMapper
from wcesapi.project import Project
from wcesapi.requester import Requester
from wcesapi.survey import Survey
from wcesapi.term import Term
from wcesapi.user import User
from wcesapi.metadata import Metadata


logger = logging.getLogger(__name__)


class CES:
    """
    The main class to be instantiated to provide access to CES's API.
    """

    def __init__(
        self,
        base_url: str,
        access_token: str,
        max_retries: Optional[int] = None,
        retry_backoff: Optional[int] = None,
        rate_limit_delay: Optional[int] = None,
    ) -> None:
        """
        Initialize the CES instance.

        Args:
            base_url (str): The base URL of the CES instance being accessed.
            access_token (str): The API key used to authenticate requests.
            max_retries (Optional[int], optional): Maximum number of retry attempts for failed requests. Defaults to None.
            retry_backoff (Optional[int], optional): Exponential backoff factor for retries (in seconds). Defaults to None.
            rate_limit_delay (Optional[int], optional): Initial delay for rate limiting (in seconds). Defaults to None.
        """
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

    def __repr__(self) -> str:
        """
        Provides a detailed string representation of the CES object.

        Returns:
            str: A detailed string representation of the CES instance.
        """
        classname = self.__class__.__name__
        attributes = [
            f"base_url='{self._requester.base_url}'",
            f"max_retries={self._requester.max_retries}",
            f"retry_backoff={self._requester.retry_backoff}",
            f"rate_limit_delay={self._requester.rate_limit_delay}",
        ]
        attr_str = ",\n    ".join(attributes)
        return f"{classname}(\n    {attr_str}\n)"

    def __str__(self) -> str:
        """
        Provides a concise string representation of the CES object.

        Returns:
            str: A concise string representation of the CES instance.
        """
        return f"CES(base_url='{self._requester.base_url}')"

    @staticmethod
    def _validate_base_url(base_url: str) -> None:
        """
        Validate the given base URL.

        This method checks for common issues with the base URL:
        - Ensures the URL is not empty
        - Checks for the presence of a scheme (http:// or https://)
        - Verifies that 'api/' is not included in the URL
        - Warns if HTTP is used instead of HTTPS

        Args:
            base_url (str): The base URL to validate.

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
    def _clean_url(base_url: str) -> str:
        """
        Clean up a given base URL.

        This method performs the following cleanup operations:
        - Removes leading and trailing whitespace
        - Removes trailing forward slashes

        Args:
            base_url (str): The base URL to clean.

        Returns:
            str: The cleaned base URL.
        """
        return base_url.strip().rstrip("/")

    def set_retry_options(
        self, max_retries: Optional[int], retry_backoff: Optional[int]
    ) -> None:
        """
        Set retry options for the requester.

        Args:
            max_retries (Optional[int]): Maximum number of retry attempts for failed requests.
            retry_backoff (Optional[int]): Exponential backoff factor for retries (in seconds).
        """
        self._requester.set_retry_options(max_retries, retry_backoff)

    def set_rate_limit_delay(self, rate_limit_delay: Optional[int]) -> None:
        """
        Set rate limit delay for the requester.

        Args:
            rate_limit_delay (Optional[int]): Initial delay for rate limiting (in seconds).
        """
        self._requester.set_rate_limit_delay(rate_limit_delay)

    def get_account(self) -> Account:
        """Gets the account for your token."""
        api_endpoint = "account"
        return Account(self._requester, "GET", api_endpoint)

    def list_subaccounts(self) -> Account:
        """Gets a list of subaccounts for the account."""
        api_endpoint = "subAccounts"
        return Account(self._requester, "GET", api_endpoint)

    def list_terms(self) -> Term:
        """Gets a list of terms for the account."""
        api_endpoint = "terms"
        return Term(self._requester, "GET", api_endpoint)

    def user_has_in_progress_survey(self, username: str) -> bool:
        """
        Checks if user has in-progress survey for all projects in the account.

        Args:
            username (str): The username of the user to check.

        Returns:
            bool: True if the user has an in-progress survey, False otherwise.
        """
        api_endpoint = "users/hasInProgressSurvey"
        params = {"username": username}
        response = self._requester.request("GET", api_endpoint, params)
        return response.get("result", False)

    def user_has_grade_block(self, username: str) -> bool:
        """
        Checks if user has in-progress survey in all course projects with active grades blocked.

        Args:
            username (str): The username of the user to check.

        Returns:
            bool: True if the user has an in-progress survey with active grade block, False otherwise.
        """
        api_endpoint = "users/hasGradeBlock"
        params = {"username": username}
        response = self._requester.request("GET", api_endpoint, params)
        return response.get("result", False)

    def list_surveys(self) -> Survey:
        """Gets a list of surveys for the Accounts."""
        api_endpoint = "surveys"
        return Survey(self._requester, "GET", api_endpoint)

    def list_projects(
        self,
        project_type: Optional[int] = None,
        project_status: Optional[int] = None,
        ended_since: Optional[datetime] = None,
        include_subaccounts: Optional[bool] = None,
    ) -> Project:
        """
        List all the projects for an account, filter by project type status, or ended since.

        Args:
            project_type (Optional[int], optional): 1 = Course, 2 = General. Defaults to None.
            project_status (Optional[int], optional): 1 = Not-Deployed, 2 = Deployed-NotStarted, 3 = In-Progress, 4 = Ended. Defaults to None.
            ended_since (Optional[datetime], optional): Projects ended after this date (ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ). Defaults to None.
            include_subaccounts (Optional[bool], optional): Include projects from subaccounts. Defaults to None.

        Returns:
            Project: A Project object representing the retrieved projects.
        """
        api_endpoint = "projects"
        params = {
            "projectType": project_type,
            "projectStatus": project_status,
            "endedSince": ended_since.isoformat() if ended_since else None,
            "includeSubaccounts": include_subaccounts,
        }
        return Project(self._requester, "GET", api_endpoint, params=params)

    def get_project(self, project_id: int) -> Project:
        """
        Gets a single project for the account.

        Args:
            project_id (int): The ID of the project to retrieve.

        Returns:
            Project: A Project object representing the retrieved project.
        """
        api_endpoint = f"projects/{project_id}"
        return Project(self._requester, "GET", api_endpoint)

    def create_project(
        self,
        project_type: int,
        project_status: int,
        start_date: datetime,
        end_date: datetime,
        account_id: Optional[int] = None,
        title: Optional[str] = None,
        main_survey_id: Optional[int] = None,
        term_id: Optional[int] = None,
    ) -> Project:
        """
        Creates a new project.

        Args:
            project_type (int): The type of project. 1 = Course, 2 = General.
            project_status (int): The status of the project. Must be 1 (Not-Deployed).
            start_date (datetime): The start date of the project.
            end_date (datetime): The end date of the project.
            account_id (Optional[int], optional): The ID of the account for the project. Defaults to None.
            title (Optional[str], optional): The title of the project. Defaults to None.
            main_survey_id (Optional[int], optional): The ID of the main survey for the project. Defaults to None.
            term_id (Optional[int], optional): The ID of the term associated with the project. Defaults to None.

        Returns:
            Project: A Project object representing the newly created project.

        Raises:
            UserWarning: If project_status is not 1 (Not-Deployed).
            ValueError: If required parameters are missing or invalid.
        """
        if project_status != 1:
            warnings.warn(
                "Project status must be 1 (Not-Deployed). The API may reject this request.",
                UserWarning,
            )

        api_endpoint = "projects"
        data = {
            "projectType": project_type,
            "projectStatus": project_status,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "accountId": account_id,
            "title": title,
            "mainSurveyId": main_survey_id,
            "termId": term_id,
        }

        return Project(self._requester, "POST", api_endpoint, data=data)

    def list_courses(self) -> Course:
        """Gets a list of project courses for the account."""

        api_endpoint = "courses"

        return Course(self._requester, "GET", api_endpoint)

    def get_course(self, id: int | str, use_unique_id: bool = False) -> Course:
        """
        Gets a course for the account by course ID or course unique ID.

        Args:
            id (int | str): The ID or unique ID of the course.
            use_unique_id (bool, optional): Whether to use the unique ID. Defaults to False.

        Returns:
            Course: A Course object representing the retrieved course.
        """
        if use_unique_id:
            params = {"uniqueId": id}
            api_endpoint = "courses"
        else:
            api_endpoint = f"courses/{id}"
            params = None

        return Course(self._requester, "GET", api_endpoint, params=params)

    def list_account_users(
        self,
        user_types: Optional[str] = None,
        username: Optional[str] = None,
        user_id: Optional[int] = None,
        include_subaccounts: Optional[bool] = None,
    ) -> User:
        """
        Gets a list of users in the account.

        Args:
            user_types (Optional[str], optional): The types of users to include. Defaults to None.
            username (Optional[str], optional): The username to filter by. Defaults to None.
            user_id (Optional[int], optional): The user ID to filter by. Defaults to None.
            include_subaccounts (Optional[bool], optional): Whether to include users from subaccounts. Defaults to None.

        Returns:
            User: A User object representing the retrieved users.
        """
        api_endpoint = "users"
        params = {
            "userTypes": user_types,
            "username": username,
            "userId": user_id,
            "includeSubaccounts": include_subaccounts,
        }
        return User(self._requester, "GET", api_endpoint, params=params)

    def list_user_metadata(self, username: str) -> Metadata:
        """
        Gets a list of metadata for the account by course.

        Args:
            username (str): The username to filter by.

        Returns:
            Metadata: A Metadata object representing the retrieved metadata.
        """
        api_endpoint = "users/metadata"
        params = {"username": username}
        return Metadata(self._requester, "GET", api_endpoint, params=params)

    def save_user_metadata(self, username: str, name: str, value: str) -> Metadata:
        """
        Create or update user metadata.

        Args:
            username (str): The username to update.
            name (str): The name of the metadata.
            value (str): The value of the metadata.

        Returns:
            Metadata: A Metadata object representing the saved metadata.
        """
        api_endpoint = "users/metadata"
        params = {"username": username}
        data = {"name": name, "value": value}
        return Metadata(self._requester, "POST", api_endpoint, params=params, data=data)

    def save_user_metadata_batch(
        self, username: str, metadata: list[dict[str, str]]
    ) -> Metadata:
        """
        Create or update user metadata by uploading multiple metadata as a batch.

        Args:
            username (str): The username to update.
            metadata (list[dict[str, str]]): The metadata to save.

        Returns:
            Metadata: A Metadata object representing the saved metadata.
        """
        api_endpoint = "users/metadata-batch"
        params = {"username": username}
        data = {"metadata": metadata}
        return Metadata(
            self._requester,
            "POST",
            api_endpoint,
            params=params,
            data=data,
        )

    def remove_user_metadata(self, username: str, name: str) -> None:
        """
        Removes a user metadata by name in the account.

        Args:
            username (str): The username to update.
            name (str): The name of the metadata to remove.
        """
        api_endpoint = "users/metadata"
        params = {"username": username, "name": name}
        self._requester.request("DELETE", api_endpoint, params=params)

    def create_admin_user(
        self,
        username: str,
        user_type: int,
        user_types: list[int],
        first_name: str,
        last_name: str,
        email: str,
        roles: list[int],
        node_path: list[str],
        user_id: Optional[int] = None,
        account_id: Optional[int] = None,
        password: Optional[str] = None,
    ) -> User:
        """
        Creates an admin user in the account.

        Args:
            username (str): The username of the new user.
            user_type (int): The type of user.
            user_types (list[int]): A list of user types.
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            email (str): The email of the user.
            roles (list[int]): A list of roles for the user.
            node_path (list[str]): The node path for the user.
            user_id (Optional[int], optional): The user ID. Defaults to None.
            account_id (Optional[int], optional): The account ID. Defaults to None.
            password (Optional[str], optional): The password for the user. Defaults to None.

        Returns:
            User: A User object representing the created user.
        """
        api_endpoint = "users/administrator"
        data = {
            "userId": user_id,
            "accountId": account_id,
            "username": username,
            "userType": user_type,
            "userTypes": user_types,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "password": password,
            "roles": roles,
            "nodePath": node_path,
        }
        return User(self._requester, "POST", api_endpoint, data=data)

    def update_admin_user(
        self,
        username: str,
        user_type: int,
        user_types: list[int],
        first_name: str,
        last_name: str,
        email: str,
        roles: list[int],
        node_path: list[str],
        user_id: Optional[int] = None,
        account_id: Optional[int] = None,
        password: Optional[str] = None,
    ) -> User:
        """
        Updates an admin user in the account.

        Args:
            username (str): The username of the user.
            user_type (int): The type of user.
            user_types (list[int]): A list of user types.
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
            email (str): The email of the user.
            roles (list[int]): A list of roles for the user.
            node_path (list[str]): The node path for the user.
            user_id (Optional[int], optional): The user ID. Defaults to None.
            account_id (Optional[int], optional): The account ID. Defaults to None.
            password (Optional[str], optional): The password for the user. Defaults to None.

        Returns:
            User: A User object representing the updated user.
        """
        api_endpoint = "users/administrator"
        data = {
            "userId": user_id,
            "accountId": account_id,
            "username": username,
            "userType": user_type,
            "userTypes": user_types,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "password": password,
            "roles": roles,
            "nodePath": node_path,
        }
        return User(self._requester, "PUT", api_endpoint, data=data)

    def list_nodes(self) -> Node:
        """Gets list of nodes."""
        api_endpoint = "nodes"
        return Node(self._requester, "GET", api_endpoint)

    def get_node(self, node_id: int) -> Node:
        """
        Gets a single node.

        Args:
            node_id (int): The ID of the node to retrieve.

        Returns:
            Node: A Node object representing the retrieved node.
        """
        api_endpoint = f"nodes/{node_id}"
        return Node(self._requester, "GET", api_endpoint)

    def create_node(
        self,
        parent_id: int,
        account_id: int,
        name: str,
        level: Optional[int] = None,
        node_path: Optional[str] = None,
    ) -> Node:
        """
        Creates a node in the account.

        Args:
            parent_id (int): The parent ID of the node.
            account_id (int): The account ID.
            name (str): The name of the node.
            level (Optional[int], optional): The level of the node. Defaults to None.
            node_path (Optional[str], optional): The node path. Defaults to None.

        Returns:
            Node: A Node object representing the created node.
        """
        api_endpoint = "node"
        data = {
            "parentId": parent_id,
            "accountId": account_id,
            "level": level,
            "name": name,
            "nodePath": node_path,
        }
        return Node(self._requester, "POST", api_endpoint, data=data)

    def update_node(
        self,
        node_id: int,
        parent_id: int,
        account_id: int,
        name: str,
        level: Optional[int] = None,
        node_path: Optional[str] = None,
    ) -> Node:
        """
        Updates a node in the account.

        Args:
            node_id (int): The ID of the node to update.
            parent_id (int): The parent ID of the node.
            account_id (int): The account ID.
            name (str): The name of the node.
            level (Optional[int], optional): The level of the node. Defaults to None.
            node_path (Optional[str], optional): The node path. Defaults to None.

        Returns:
            Node: A Node object representing the updated node.
        """
        api_endpoint = f"node/{node_id}"
        data = {
            "id": node_id,
            "parentId": parent_id,
            "accountId": account_id,
            "level": level,
            "name": name,
            "nodePath": node_path,
        }
        return Node(self._requester, "PUT", api_endpoint, data=data)

    def delete_node(self, node_id: int) -> None:
        """
        Deletes a node in the account.

        Args:
            node_id (int): The ID of the node to delete.
        """
        api_endpoint = f"node/{node_id}"
        self._requester.request("DELETE", api_endpoint)

    def get_node_mapper(self, node_mapper_id: int) -> NodeMapper:
        """
        Gets a single NodeMapper.

        Args:
            node_mapper_id (int): The ID of the NodeMapper to retrieve.

        Returns:
            NodeMapper: A NodeMapper object representing the retrieved NodeMapper.
        """
        api_endpoint = f"nodemapper/{node_mapper_id}"
        return NodeMapper(self._requester, "GET", api_endpoint)

    def create_node_mapper(self, node_mapper: dict) -> NodeMapper:
        """
        Creates a NodeMapper in node.

        Args:
            node_mapper (dict): The NodeMapper data.

        Returns:
            NodeMapper: A NodeMapper object representing the created NodeMapper.
        """
        api_endpoint = "nodemapper"
        data = {"nodeMapper": node_mapper}
        return NodeMapper(self._requester, "POST", api_endpoint, data=data)

    def update_node_mapper(self, node_mapper_id: int, node_mapper: dict) -> NodeMapper:
        """
        Updates a NodeMapper in the node.

        Args:
            node_mapper_id (int): The ID of the NodeMapper to update.
            node_mapper (dict): The NodeMapper data.

        Returns:
            NodeMapper: A NodeMapper object representing the updated NodeMapper.
        """

        api_endpoint = f"nodemapper/{node_mapper_id}"
        data = {"nodeMapper": node_mapper}
        return NodeMapper(self._requester, "PUT", api_endpoint, data=data)

    def delete_node_mapper(self, node_mapper_id: int) -> None:
        """
        Deletes a NodeMapper in the account.

        Args:
            node_mapper_id (int): The ID of the NodeMapper to delete.
        """
        api_endpoint = f"nodemapper/{node_mapper_id}"
        self._requester.request("DELETE", api_endpoint)
