from module_utils.graylog import GraylogApi
import logging

USER = 'admin'
PASSWORD = 'testpass'
ENDPOINT = 'http://localhost:9000'

def test_token():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    logging.debug('token: '+str(api.session.headers['Authorization']))
    assert 'Authorization' in api.session.headers.keys()

def test_get():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    roles = api.get(ENDPOINT+'/api/roles')
    logging.debug('roles: '+str(roles))
    assert len(roles['roles']) == 5

def test_post():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    role = api.create(ENDPOINT+'/api/roles', {'name': 'test-role', 'description': 'test', 'permissions': ['views:read:*'], 'read_only': True})
    logging.debug('created role: ' + str(role))
    roles = api.get(ENDPOINT+'/api/roles')
    assert len(roles['roles']) == 6

def test_update():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    role = api.update(ENDPOINT+'/api/roles/test-role', {'name': 'test-role', 'description': 'test', 'permissions': ['views:read:*','streams:read:*'], 'read_only': True})
    test_role = api.get(ENDPOINT+'/api/roles/test-role')
    assert 'streams:read:*' in test_role['permissions']

def test_delete():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    role = api.delete(ENDPOINT+'/api/roles/test-role')
    roles = api.get(ENDPOINT+'/api/roles')
    assert len(roles['roles']) == 5

def test_role_exists():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    assert api.exists('roles', 'name', 'Admin')
    assert not api.exists('roles', 'name', 'blarg')

def test_users_exists():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    assert api.exists('users', 'username', 'admin')