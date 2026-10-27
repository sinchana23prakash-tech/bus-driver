from app.models.user import User
from app.extensions import db

def test_initial_admin_setup_lifecycle(client, app):
    # In clean test DB where no users exist
    with app.app_context():
        User.query.delete()
        db.session.commit()

    # Setup status check
    status_res = client.get('/api/auth/setup-status')
    assert status_res.status_code == 200
    assert status_res.get_json()['needs_initial_setup'] is True

    # Perform initial setup
    res = client.post('/api/auth/setup-initial-admin', json={
        'username': 'firstadmin',
        'email': 'firstadmin@college.edu',
        'password': 'StrongPassword@123',
        'full_name': 'First Fleet Admin',
        'phone_number': '9876543210'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert 'access_token' in data
    assert data['user']['role'] == 'ADMIN'

    # Second call must be locked out with 403
    res2 = client.post('/api/auth/setup-initial-admin', json={
        'username': 'secondadmin',
        'email': 'second@college.edu',
        'password': 'StrongPassword@123',
        'full_name': 'Another Admin'
    })
    assert res2.status_code == 403
    assert 'already been completed' in res2.get_json()['error']

def test_user_login_success_and_failure(client, test_users):
    # Valid login
    res = client.post('/api/auth/login', json={
        'identifier': 'testadmin',
        'password': 'AdminPass@123'
    })
    assert res.status_code == 200
    assert 'access_token' in res.get_json()
    assert res.get_json()['user']['role'] == 'ADMIN'

    # Invalid password
    res_bad = client.post('/api/auth/login', json={
        'identifier': 'testadmin',
        'password': 'WrongPassword'
    })
    assert res_bad.status_code == 401
    assert 'Invalid credentials' in res_bad.get_json()['error']

    # Non-existent user
    res_none = client.post('/api/auth/login', json={
        'identifier': 'nobody',
        'password': 'SomePassword'
    })
    assert res_none.status_code == 401

def test_inactive_user_cannot_login(client, app, test_users):
    with app.app_context():
        driver = User.query.get(test_users['driver1'].id)
        driver.is_active = False
        db.session.commit()

    res = client.post('/api/auth/login', json={
        'identifier': 'driver1',
        'password': 'DriverPass@123'
    })
    assert res.status_code == 403
    assert 'deactivated' in res.get_json()['error']
