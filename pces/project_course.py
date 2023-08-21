from ces_object import CESObject
from user import User
from paginated_list import PaginatedList
from utilities import combine_kwargs


class ProjectCourse(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)

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

    
