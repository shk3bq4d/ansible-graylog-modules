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
    roles = api.get('/api/roles')
    logging.debug('roles: '+str(roles))
    assert len(roles['roles']) == 5

def test_post():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    role = api.create('/api/roles', {'name': 'test-role', 'description': 'test', 'permissions': ['views:read:*'], 'read_only': True})
    logging.debug('created role: ' + str(role))
    roles = api.get('/api/roles')
    assert len(roles['roles']) == 6

def test_update():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    role = api.update('/api/roles/test-role', {'name': 'test-role', 'description': 'test', 'permissions': ['views:read:*','streams:read:*'], 'read_only': True})
    test_role = api.get('/api/roles/test-role')
    assert 'streams:read:*' in test_role['permissions']

def test_delete():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    role = api.delete('/api/roles/test-role')
    roles = api.get('/api/roles')
    assert len(roles['roles']) == 5

def test_role_exists():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    exists, data = api.exists('roles', 'name', 'Admin')
    assert exists
    assert data['name'] == 'Admin'
    exists, data = api.exists('roles', 'name', 'blarg')
    assert not exists
    assert not data

def test_users_exists():
    api = GraylogApi(USER, PASSWORD, ENDPOINT)
    api.login()
    exists, data = api.exists('users', 'username', 'admin')
    assert exists