from wcesapi.ces_object import CESObject
from wcesapi.user import User


class ProjectCourse(CESObject):
    pass
    # need to figure out relationship between projectCourse id, projectId, and courseId
    # def get_users(self, filters=None, **kwargs):
    #     """
    #     Gets a list of users in a project course for the account. Filter by optional userType.

    #     GET /api/projects/{projectId}/courses/{courseId}/users?userType={userType}

    #     Returns a PaginatedList of Users
    #     """

    #     return PaginatedList(
    #         User,
    #         self.__requester,
    #         "GET",
    #         "courses/{}/projects".format(self.id),
    #         filters=filters,
    #         _kwargs=combine_kwargs(**kwargs)
    #         )
