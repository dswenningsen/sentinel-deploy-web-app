"""
response Checker
Can eventually be used to handle pagination and API limits
"""

import requests
import src.app_logging as al

# pylint: disable=W1203


def response_check(preamble: str, response: requests.Response):
    """Check the response from a request and log errors if any"""
    try:
        if not response.raise_for_status() and response.content:
            return response.json()
        else:
            al.logger.info(
                f"No content in good response: {response.status_code}"
            )
            return True
    except requests.exceptions.HTTPError as e:
        al.logger.error(f"{preamble}: {e} :::: {response.text}")
        return False
