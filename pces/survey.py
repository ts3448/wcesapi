from ces_object import CESObject
from paginated_list import PaginatedList
from question import Question
from utilities import combine_kwargs


class Survey(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)

    def get_questions(self, filters=None, **kwargs):
        """
        Gets a list of survey questions and options for the account by survey id.

        GET /api/surveys/{surveyId}/Questions

        Returns a PaginatedList of Questions
        """

        return PaginatedList(
            Question,
            self.__requester,
            "GET",
            "surveys/{}/Questions".format(self.id),
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )
    
    