import requests
from requests.exceptions import HTTPError
from requests.adapters import HTTPAdapter, Retry
import jwt
from datetime import datetime
from datetime import timedelta

LOGIN_URL = 'https://ginarea.org/api/accounts/login'
BOT_URL = 'https://ginarea.org/api/bots/'


class Ginarea():

    def __init__(self, api_key="login", api_secret="encrypted_password", retries=3):
        self.session = requests.Session()
        self.session.headers['Accept'] = 'application/json'
        self.session.headers['Origin'] = 'https://ginarea.org'
        self.session.headers['Referer'] = 'https://ginarea.org/login'
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['cache-control'] = 'no-cache'
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) Chrome/122.0.0.0 Safari/537.36'

        if retries > 0:
            retries_strategy = Retry(total=retries, backoff_factor=2)

            self.session.mount('https://ginarea.org', HTTPAdapter(max_retries=retries_strategy))

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
            raise HTTPError from http_err

        except Exception as err:
            raise Exception from err

    def _token_expired(self):
        decoded_token = jwt.decode(self.token,
                                   algorithms=['HS256'],
                                   options={'verify_signature': False}
                                   )
        token_expires_time = decoded_token.get('exp') - timedelta(minutes=15).total_seconds()

        if token_expires_time < datetime.now().timestamp():
            return True

        return False

    def _get_bot_data(self, bot_id):

        bot_url = BOT_URL + bot_id

        if self._token_expired():
            self._authenticate()

        try:
            response = self.session.request("Get", bot_url)
            data = response.json()

            return data['name'], data['params'], data['stat']

        except Exception as err:
            raise

    def _update_bot_data(self, bot_id, bot_data):

        bot_url = BOT_URL + bot_id + '/params'

        if self._token_expired():
            self._authenticate()

        try:
            response = self.session.request("PUT", bot_url, json=bot_data, timeout=3)
            response.raise_for_status()
            return True

        except Exception as err:
            raise

    def order_list(self, bot_id):

        bot_url = BOT_URL + bot_id + '/orders?pageSize=100&pageNumber=0&onlyOpened=true'

        if self._token_expired():
            self._authenticate()

        try:
            response = self.session.request("GET", bot_url)
            response.raise_for_status()

            return True

        except Exception as err:
            raise

    def status(self, bot_id):

        bot_name, bot_data, _ = self._get_bot_data(bot_id)

        return {
            'name': bot_name,
            'bottom': bot_data['border']['bottom'],
            'top': bot_data['border']['top'],
            'gridstep': bot_data['gs'],
            'dsblin': bot_data['dsblin'],
            'mode': bot_data.get('mode'),
        }

    def stats(self, bot_id):

        bot_name, bot_data, bot_stats = self._get_bot_data(bot_id)

        return {
            'name': bot_name,
            'orderCount': bot_stats['triggerCount'],
            'gridstep': bot_data['gs'],
            'orderTotal': bot_data['maxOp'],
            'profit': bot_stats['profit'],
            'currentProfit': bot_stats['currentProfit'],
            'averagePrice': bot_data.get('averagePrice')
        }

    def update(self, bot_id, top=None, bottom=None, disable=None, orders=None, gridstep=None, mode=None):

        bot_name, bot_data, _ = self._get_bot_data(bot_id)

        if bot_data:
            if top:
                bot_data['border']['top'] = top

            if bottom:
                bot_data['border']['bottom'] = bottom

            if disable is not None:
                bot_data['dsblin'] = disable

            if orders is not None:
                bot_data['maxOp'] = orders

            if gridstep is not None:
                bot_data['gs'] = gridstep

            if mode is not None:
                bot_data['mode'] = mode

            self._update_bot_data(bot_id, bot_data)

        return bot_name, bot_data

    def start(self, bot_id):

        bot_url = BOT_URL + bot_id + '/start'

        try:
            response = self.session.request("PUT", bot_url)
            response.raise_for_status()
            return True

        except Exception as err:
            raise

    def stop(self, bot_id):

        bot_url = BOT_URL + bot_id + '/stop'

        try:
            response = self.session.request("PUT", bot_url)
            response.raise_for_status()
            return True

        except Exception as err:
            raise

    def close(self, bot_id):

        bot_url = BOT_URL + bot_id + '/close'

        try:
            response = self.session.request("PUT", bot_url)
            response.raise_for_status()
            return True

        except Exception as err:
            raise
