from ansible.module_utils.urls import Request, to_text
#compat with python2
try:
    from urllib.error import URLError
except ImportError:
    import urllib2
    URLError = urllib2.URLError
import json
import base64


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
        try:
            if not payload:
                response = self.session.open(method, self.endpoint + url)
            else:
                response = self.session.open(method, self.endpoint + url, data=bytes(json.dumps(payload), encoding='utf8'))
        except (URLError, ConnectionResetError) as error:
            raise Exception(error)

        if response.status not in acceptable_status:
            raise Exception('Status {0}, Message {1}'.format(info['msg'], info['body']))
        try:
            content = json.loads(to_text(response.read(), errors='surrogate_or_strict'))
        except (AttributeError, json.decoder.JSONDecodeError):
            content = None
        return content

    def exists(self, item_type, search_key, name):
        url = '/api/'+ item_type
        response = self.get(url)
        for item in response[item_type]:
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

