from typing import Any, Dict

import pandas as pd
import logging
from requester import Requester, HttpMethod, ApiEndpoint


logger = logging.getLogger(__name__)


class CESObject:
    """
    Base class for all classes representing objects returned by the API.
    This class abstracts Pandas DataFrame, storing attributes as columns and
    values as a single row.
    """

    def __init__(
        self,
        requester: Requester,
        request_method: HttpMethod,
        api_endpoint: ApiEndpoint,
        **kwargs: Any,
    ) -> None:
        self._df: pd.DataFrame = pd.DataFrame()
        self._requester = requester
        self._request_method = request_method
        self._api_endpoint = api_endpoint
        self._params = kwargs or {}
        self._params["per_page"] = kwargs.get("per_page", 100)

        self._fetch_all_data()

    @property
    def df(self) -> pd.DataFrame:
        """Returns the underlying DataFrame."""
        return self._df

    def __getattr__(self, name: str) -> Any:
        """Provides attribute-like access to DataFrame columns."""
        try:
            return self._df[name].iloc[0]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    def __repr__(self) -> str:
        """Provides a string representation of the object."""
        classname = self.__class__.__name__
        attrs = ", ".join(self._df.columns)
        return f"{classname}({attrs})"

    def __iter__(self):
        """Allows iteration over the object's data."""
        yield from self._df.itertuples(index=False)

    def _fetch_all_data(self) -> None:
        """Fetches all available data, handling pagination and converting date columns."""
        next_url = self._endpoint
        while next_url:
            response = self._requester.request(
                self._request_method,
                next_url,
                **self._params,
            )
            data = response.json()

            result_list = data.get("resultList", [])
            new_df = pd.DataFrame(result_list)
            self._df = pd.concat([self._df, new_df], ignore_index=True)

            page = data.get("page")
            page_size = data.get("pageSize")
            if page_size == len(result_list) and page is not None:
                next_url = next_url.replace(f"page={page}", f"page={page + 1}")
            else:
                next_url = None

        self._convert_date_columns()

    def _convert_date_columns(self) -> None:
        """Converts date columns to datetime objects."""
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
            "submitDate",
        ]
        for col in date_columns:
            if col in self._df.columns:
                self._df[col] = pd.to_datetime(self._df[col], errors="coerce")

    @property
    def data(self) -> Dict[str, Any]:
        """Returns a dictionary representation of the object's data."""
        return self._df.to_dict(orient="records")[0] if not self._df.empty else {}

    # def get_context(self, return_type: str) -> "CESObject":
    #     """
    #     Retrieve the context (object) based on the return_type.
    #     Recursively called until the context is None (only true of the CES class).

    #     Args:
    #         return_type (str): Name of the class to return.

    #     Returns:
    #         CESObject: The object with name that matches the return_type.

    #     Raises:
    #         ValueError: If the context of the specified type is not found.
    #     """
    #     if return_type == type(self).__name__:
    #         return self
    #     elif self._config.context:
    #         return self._config.context.get_context(return_type)
    #     else:
    #         raise ValueError(
    #             f"Context of type '{return_type}' not found in the method chain."
    #         )

    # def refresh(self) -> None:
    #     """Refreshes the object's data from the API."""
    #     try:
    #         response = self._config.requester.request(
    #             self._config.request_method, self._config.first_url, **self._next_params
    #         )
    #         self._set_attributes(response.json())
    #     except Exception as e:
    #         logger.error(f"Error refreshing data: {str(e)}")
    #         raise

    # @lru_cache(maxsize=128)
    # def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    #     """Applies filters to the DataFrame. Results are cached for performance."""
    #     if not filters:
    #         return df

    #     mask = pd.Series([True] * len(df))
    #     for key, values in filters.items():
    #         if key not in df.columns:
    #             logger.warning(f"DataFrame does not have a column named {key}")
    #             continue

    #         key_mask = pd.Series([False] * len(df))
    #         for value in values:
    #             key_mask |= self._apply_single_filter(df[key], value)
    #         mask &= key_mask

    #     return df[mask].reset_index(drop=True)

    # @staticmethod
    # def _apply_single_filter(series: pd.Series, filter_value: str) -> pd.Series:
    #     """Applies a single filter to a Series."""
    #     operators_pattern = re.compile(r"^([><≥≤!=≠<>]+)")
    #     operator_match = operators_pattern.match(filter_value)
    #     operator = operator_match.group(0) if operator_match else None
    #     value = re.sub(operators_pattern, "", filter_value)

    #     try:
    #         numeric_value = float(value)
    #         return CESObject._apply_numeric_filter(series, operator, numeric_value)
    #     except ValueError:
    #         return CESObject._apply_string_filter(series, operator, value)

    # @staticmethod
    # def _apply_numeric_filter(
    #     series: pd.Series, operator: Optional[str], value: float
    # ) -> pd.Series:
    #     """Applies a numeric filter to a Series."""
    #     if operator in [">", "≥"]:
    #         return series > value
    #     elif operator in ["<", "≤"]:
    #         return series < value
    #     elif operator in ["!=", "≠", "<>"]:
    #         return series != value
    #     else:
    #         return series == value

    # @staticmethod
    # def _apply_string_filter(
    #     series: pd.Series, operator: Optional[str], value: str
    # ) -> pd.Series:
    #     """Applies a string filter to a Series."""
    #     if operator in ["!=", "≠", "<>"]:
    #         return ~series.str.match(f'^{value.replace("*", ".*")}$')
    #     else:
    #         return series.str.match(f'^{value.replace("*", ".*")}$')
