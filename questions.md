1.  `test_login_success`: Not getting `status code 302 when it suppose to be 200 with the following set up:

```py
class AuthenticationTestCase(TestCase):
    def setUp(self):
        print("INSIDE SET UP")

    def test_login_success(self):
        with app.test_client() as client:
            res = client.post('/login', data={
                'username': 'ben',
                'password': '123'
                }, follow_redirects=False)

            self.assertEqual(res.status_code, 302)
```

-   Is CSRF relevant in this testing context?
-   Is database interaction necessary for login testing? In this case, I am using data from database which concern me. What is the best practice of handling this? 

2.  How to simulate a scenario where a logged-in user tries to update a feedback entry that does not belong to him/her?

```py
def test_access_denied_for_wrong_user(self):
        with app.test_client() as client:
            client.post('/login', data={
                'username': 'ben',
                'password': '123'
                }, follow_redirects=True)

            res = client.post('/feedback/1/update')
```