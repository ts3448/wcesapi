from pces.ces_object import CESObject
from pces.pandanated_list import PandanatedList
from pces.question import Question
from pces.response_rate import ResponseRate
from pces.utilities import combine_kwargs


class Survey(CESObject):
    def __str__(self):
        return "{} {} ({})".format(self.course_code, self.name, self.id)

    def get_questions(self, filters=None, **kwargs):
        """
        Gets a list of survey questions and options for the account
        by survey id.

        API call:
            GET /api/surveys/{surveyId}/Questions

        Accepted paramters (kwargs):
            page (int)

        Returns a PandanatedList of Questions
        """

        return PandanatedList(
            Question,
            self.__requester,
            "GET",
            "surveys/{}/Questions".format(self.id),
            filters=filters,
            _kwargs=combine_kwargs(**kwargs)
            )

    def get_response_rate(self, filters=None):
        """
        Returns response rate of all projects associated with this survey

        GET /api/SurveyResponseRate/{surveyId}

        Returns a PandanatedList of ResponseRates
        """

        return PandanatedList(
            ResponseRate,
            self.__requester,
            "GET",
            "SurveyResponseRate/{}".format(self.id),
            filters=filters
            )
