from pces.ces_object import CESObject
from pces.question import Question
from pces.response_rate import ResponseRate


class Survey(CESObject):

    def get_questions(self):
        """
        Gets a list of survey questions and options for the account by survey id.

        API call:
            GET /api/surveys/{surveyId}/Questions

        Returns:
            Question: A Question containing the list of survey questions and options.
        """
        api_endpoint = f"surveys/{self.id}/Questions"
        return Question(
            requester=self._requester, request_method="GET", api_endpoint=api_endpoint
        )

    def get_response_rate(self):
        """
        Returns response rate of all projects associated with this survey.

        API call:
            GET /api/SurveyResponseRate/{surveyId}

        Returns:
            ResponseRate: A ResponseRate containing the response rates for all projects
                          associated with this survey.
        """
        api_endpoint = f"SurveyResponseRate/{self.id}"
        return ResponseRate(
            requester=self._requester, request_method="GET", api_endpoint=api_endpoint
        )
