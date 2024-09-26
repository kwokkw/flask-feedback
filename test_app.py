from unittest import TestCase
from app import app

# app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False 
# app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


# Define class object inherit from `TestCase`
class AuthTestCase(TestCase):
    def setUp(self):
        # Set up test client and database before each test
        print("INSIDE SET UP")

    def test_login_success(self):
        with app.test_client() as client:
            # make requests to flask via `client`
            res = client.post('/login', data={
                'username': 'ben',
                'password': '123'
                }, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('user page', html)

    def test_login_failure(self):
        with app.test_client() as client:
            res = client.post('/login', data={
                'username':'invalid_user',
                'password':'invalid_password'
            }, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Login', html)

    def test_logout(self):
        with app.test_client() as client:
            client.post('/login', data={
                'username': 'ben',
                'password': '123'
                }, follow_redirects=True)
            res = client.get('/logout', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            
    def test_access_denied_without_login(self):
        with app.test_client() as client:
            res = client.get('/users/ben', follow_redirects=True)

            self.assertEqual(res.status_code, 401)

    def test_access_granted_with_login(self):
        with app.test_client() as client:
            client.post('/login', data={
                'username': 'ben',
                'password': '123'
                }, follow_redirects=True)
            res = client.post('/users/ben/feedback/add', follow_redirects=True)

            self.assertEqual(res.status_code, 200)

    def test_access_denied_for_wrong_user(self):
        with app.test_client() as client:
            client.post('/login', data={
                'username': 'ben',
                'password': '123'
                }, follow_redirects=True)

            res = client.post('/feedback/1/update')


    


            
            
