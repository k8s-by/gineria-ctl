import requests
from requests.exceptions import HTTPError

LOGIN_URL = 'https://ginarea.org/api/accounts/login'
BOT_URL = 'https://ginarea.org/api/bots/'


class Ginarea():

    def __init__(self, api_key="login", api_secret="encrypted_password"):
        self.session = requests.Session()
        self.session.headers['Accept'] = 'application/json'
        self.session.headers['Origin'] = 'https://ginarea.org'
        self.session.headers['Referer'] = 'https://ginarea.org/login'
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['cache-control'] = 'no-cache'
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) Chrome/122.0.0.0 Safari/537.36'

        self.token = None

        self.api_key = api_key
        self.api_secret = api_secret
        self.connect_to_api(api_key, api_secret)

    def connect_to_api(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

        self._authenticate()

    def _authenticate(self):
        payload = {
            "email": self.api_key,
            "password": self.api_secret
        }

        try:
            # login
            response = self.session.request("POST", LOGIN_URL, json=payload)
            response.raise_for_status()

            # save access token and add it to headers
            self.token = response.json()['accessToken']
            self.session.headers['Authorization'] = "Bearer " + self.token

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        except Exception as err:
            print(f'Other error occurred: {err}')

    def _get_bot_data(self, bot_id):

        bot_url = BOT_URL + bot_id

        try:
            response = self.session.request("Get", bot_url)
            data = response.json()
            return data['name'], data['params']

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        except Exception as err:
            print(f'Other error occurred: {err}')

        return None

    def _update_bot_data(self, bot_id, bot_data):

        bot_url = BOT_URL + bot_id + '/params'

        try:
            response = self.session.request("PUT", bot_url, json=bot_data)
            response.raise_for_status()
            return True

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        except Exception as err:
            print(f'Other error occurred: {err}')

        return False

    def status(self, bot_id):

        bot_name, bot_data = self._get_bot_data(bot_id)

        return {
            'name': bot_name,
            'bottom': bot_data['border']['bottom'],
            'top': bot_data['border']['top'],
            'dsblin': bot_data['dsblin']
        }

    def stats(self, bot_id):

        bot_name, bot_data = self._get_bot_data(bot_id)

        return {
            'name': bot_name,
            'profit': bot_data['stat']['profit'],
            'currentProfit': bot_data['stat']['currentProfit']
        }

    def update(self, bot_id, top=None, bottom=None, disable=None):

        bot_name, bot_data = self._get_bot_data(bot_id)

        if bot_data:
            if top:
                bot_data['border']['top'] = top

            if bottom:
                bot_data['border']['bottom'] = bottom

            if disable is not None:
                bot_data['dsblin'] = disable

            if self._update_bot_data(bot_id, bot_data):
                pass
                # print(f"Bot {bot_name}/{bot_id} has been successfully updated")
            else:
                print(f"Failed to update bot {bot_id}")

    def start(self, bot_id):

        bot_url = BOT_URL + bot_id + '/start'

        try:
            response = self.session.request("PUT", bot_url)
            response.raise_for_status()
            return True

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        except Exception as err:
            print(f'Other error occurred: {err}')

        return False

    def stop(self, bot_id):

        bot_url = BOT_URL + bot_id + '/stop'

        try:
            response = self.session.request("PUT", bot_url)
            response.raise_for_status()
            return True

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        except Exception as err:
            print(f'Other error occurred: {err}')

        return False

    def close(self, bot_id):

        bot_url = BOT_URL + bot_id + '/close'

        try:
            response = self.session.request("PUT", bot_url)
            response.raise_for_status()
            return True

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

        except Exception as err:
            print(f'Other error occurred: {err}')

        return False
