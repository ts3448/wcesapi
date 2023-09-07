import pandas as pd


class CESObject(object):
    """
    Base class for all classes representing objects returned by the API.

    This class abstracts Pandas DataFrame, storing attributes as columns and
    values as a single row.
    """

    @property
    def df(self):
        return self._df

    def __getattr__(self, name):
        # Check if attribute exists in the main dataframe
        if name in self._df.columns:
            return self._df[name].iloc[0]

        # If attribute doesn't exist, raise an AttributeError
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'")

    def __init__(self, requester, attributes, context=None):
        """
        Initializes the class and calls "set_attributes".

        Args:
            requester (Requester): The Requester object used to make API calls.

            attributes (json): JSON formatted response from thr API call.

            context (object): The object that called the method that created
                the current object. Used to navigate through chained methods
                to return a specific object, rather than the last object
                called in the chain.

        Returns:
            CESObject: Instance of the class.

        """
        self._requester = requester
        self._context = context
        self._shared_columns = {}

        self.set_attributes(attributes)

    def __repr__(self):  # pragma: no cover
        classname = self.__class__.__name__

        # Extracting column names from the DataFrame
        attrs = ", ".join(self._df.columns)

        return "{}({})".format(classname, attrs)

    def set_attributes(self, attributes):
        """
        Load the JSON response (dict) into a DataFrame with attributes
        as columns and data as a single row.

        Params:
            attributes (dict): The JSON object used to create the object data.

        """
        # Check if 'resultList' key exists in attributes
        if 'resultList' in attributes:
            # Use the resultList for the dataframe
            self._df = pd.DataFrame(attributes['resultList'])
        else:
            self._df = pd.DataFrame([attributes])

        # Convert specific columns to datetime format
        date_columns = [
            "created",
            "updated",
            "startDate",
            "endDate",
            "adminReportAccessStartDate",
            "adminReportAccessEndDate",
            "instructorReportAccessStartDate",
            "instructorReportAccessEndDate",
            "taReportAccessStartDate",
            "taReportAccessEndDate",
            "customQuestionStartDate",
            "customQuestionEndDate",
            "submitDateTime",
            "courseSurveyStart",
            "courseSurveyEnd",
            "submitDate"
            ]
        for col in date_columns:
            if col in self._df.columns:
                self._df[col] = pd.to_datetime(self._df[col])

    def get_context(self, return_type):
        """
        Retrieve the context (object) based on the return_type.
        Recursively called until the context is None (only true
        of the CES class).

        Params:
            return_type (str): Name of the class to return.
            join (bool): Whether to join the dataframes or not.

        Returns:
            self (object): The object with name that matches the return_type.
        """

        if return_type == type(self).__name__:
            return self
        elif self._context:
            return self._context.get_context(return_type)
        else:
            raise ValueError(
                "Context of type '{}' not found in the method chain."
                ).format(return_type)
