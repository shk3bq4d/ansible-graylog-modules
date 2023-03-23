# /* ex: set fenc=utf-8 expandtab ts=4 sw=4 : */
from ansible.module_utils.urls import Request, to_text
from urllib.error import URLError
import urllib
import json
import base64
from pprint import pprint


class GraylogApi():

    def __init__(self, username, password, endpoint, validate_certs=True):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.session = Request(headers={ 'Content-Type': 'application/json', 'X-Requested-By': 'Graylog API', 'Accept': 'application/json' },
            use_proxy=True, timeout=10, validate_certs=validate_certs)

    def login(self):
        url = '/api/system/sessions'
        payload= {'username': self.username, 'password': self.password, 'host': self.endpoint}
        session = self.create(url, payload)
        session_string = session['session_id'] + ':session'
        session_bytes = session_string.encode('utf-8')
        session_token = base64.b64encode(session_bytes)
        self.session.headers['Authorization'] = 'Basic '+session_token.decode()

    def do_request(self, url, method, payload=None):
        acceptable_status = [200, 201, 204]
        data=None
        full_url = self.endpoint + urllib.parse.quote(url)
        if payload:
            data=bytes(json.dumps(payload), encoding='utf8')
        try:
            response = self.session.open(method, full_url, data=data)
        except (URLError, ConnectionResetError) as error:
            pprint(vars(error))
            pprint(error.file.read())
            pprint(error.fp.read())
            pprint(vars(error.hdrs))
            raise Exception(error, f'for url {full_url} and data {data}')

        if response.status not in acceptable_status:
            raise Exception('Status {0}, Message {1}'.format(info['msg'], info['body']))
        try:
            content = json.loads(to_text(response.read(), errors='surrogate_or_strict'))
        except (AttributeError, json.decoder.JSONDecodeError):
            content = None
        return content

    def exists(self, item_type, search_key, name, list_result_keyA=None):
        url = '/api/'+ item_type
        response = self.get(url)
        if list_result_keyA is None:
            list_result_keyA = []
            slash = '/'
            item_typeA = item_type.split(slash)
            s = len(item_typeA)
            for k in range(s):
                list_result_keyA.append(slash.join(item_typeA[k:s]))
        elif type(list_result_keyA) == str:
            list_result_keyA = [list_result_keyA]
        for item_typeb in list_result_keyA:
            if item_typeb in response:
                for item in response[item_typeb]:
                    if name == item[search_key]:
                        return True, item
        return False, None

    def create(self, url, payload):
        return self.do_request(url, 'post', payload)

    def update(self, url, payload):
        return self.do_request(url, 'put', payload)

    def delete(self, url):
        return self.do_request(url, 'delete')

    def get(self, url):
        return self.do_request(url, 'get')

