import requests


class TelegramClient:
    """
    Implements telegram client class to send critical error messages to bot admin when exceptions happen.
    """

    def __init__(self, token: str):
        self.base_url = "https://api.telegram.org"
        self.token = token

    def make_request_url(self, method: str = None) -> str:
        """
        Creates the part of request URL to Telegram API without params and body.
        Args:
            method: Telegram API method, f.e "sendMessage"

        Returns:
            Request URL.
        """

        request_url = f"{self.base_url}/bot{self.token}/"
        if method is not None:
            request_url += method
        return request_url

    def post(self, method: str = None, params: dict = None, body: dict = None) -> int:
        """

        Args:
            method: Telegram API method, f.e "sendMessage".
            params: Params query string.
            body: The body of POST request (if needed).

        Returns:
            Response status code.
        """

        response = requests.post(url=self.make_request_url(method), params=params, data=body)
        return response.status_code
