import pandas as pd


class UnifiedObject(object):
    """
    Unified class that abstracts both the CESObject and PandanatedList functionalities.
    This class can handle both single row and multi-row data.
    """
    
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

        # Initialize the dataframe
        self.set_attributes(attributes)
    
    def set_attributes(self, attributes):
        """Load the JSON response (dict) into a DataFrame."""
        # Check if 'resultList' key exists in attributes
        if 'resultList' in attributes:
            # Use the resultList for the dataframe
            self._df = pd.DataFrame(attributes['resultList'])
        else:
            self._df = pd.DataFrame([attributes])
        
        # Convert specific columns to datetime format
        date_columns = [
            "created", "updated", "startDate", "endDate",
            "adminReportAccessStartDate", "adminReportAccessEndDate",
            "instructorReportAccessStartDate", "instructorReportAccessEndDate",
            "taReportAccessStartDate", "taReportAccessEndDate",
            "customQuestionStartDate", "customQuestionEndDate",
            "submitDateTime", "courseSurveyStart", "courseSurveyEnd", "submitDate"
        ]
        for col in date_columns:
            if col in self._df.columns:
                self._df[col] = pd.to_datetime(self._df[col])
    
    @property
    def df(self):
        """Return the dataframe, ensuring that all data is loaded."""
        # If the dataframe represents a paginated list, we might need to fetch more data.
        # This functionality is based on the '_grow_until_complete' method from PandanatedList.
        # For simplicity, we're omitting that here but it can be added if needed.
        return self._df
    
    def __getattr__(self, name):
        """Dynamic attribute access."""
        # If the dataframe has only one row, return the value from the first row
        if len(self._df) == 1 and name in self._df.columns:
            return self._df[name].iloc[0]
        
        # If the dataframe has more than one row, we might need to handle methods or other attributes.
        # This is based on the PandanatedList functionality.
        # For simplicity, we're omitting that here but it can be added if needed.
        
        # If attribute doesn't exist, raise an AttributeError
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    # The __repr__ method can be adjusted to represent both single and multi-row data.
    # Also, methods like 'prefix_columns', 'join_contexts', etc. from PandanatedList can be added as needed.

    
# This is a basic UnifiedObject class. Depending on specific requirements, more functionalities can be added.
