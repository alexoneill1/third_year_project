from app import app
import unittest
import pytest

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['SECRET_KEY'] = 'socialise is our third year project'
        self.app = app.test_client()
    # def login(self, email, password):
    #     tester = app.test_client(self) #Creates the test, where we use to send a request to and test the response
    #     return tester.post('/welcome', data=dict(email_address=email, password=password), follow_redirects=True) #login with correct credentials


    def test_welcome_route(self):
        tester = app.test_client(self) #Creates the test, where we use to send a request to and test the response
        response = tester.get('/welcome', content_type='html/text') #Call the /welcome route 
        self.assertEqual(response.status_code, 200) #and check the response status code equals 200

    
    def test_welcome_page(self):#Test to make sure the welcome page loads correctly. It's important to test the actual data. If we just test the 200 response code, we don't know what data that contains. It could be HTML or JSON etc.
        tester = app.test_client(self) #Creates the test, where we use to send a request to and test the response
        response = tester.get('/welcome', content_type='html/text') #Call the /welcome route 
        self.assertTrue(b'Welcome to SOCIALISE' in response.data) #check if the string 'Welcome to SOCIALISE' is in the response. The 'b' before the string indicates the string is in binary
    
    #Test to check if the login works correctly with the correct credentials provided
    def test_correct_login_credentials(self):
        tester = app.test_client(self)
        response = tester.post('/welcome', data=dict(email_address='jfallon@gmail.com', password='password'), follow_redirects=True) #Test to check if the POST request made on login redirects to the home page(test to check if login worked correctly providing the correct credentials)
        self.assertIn(b'Home', response.data)

    #Test to check if the login works correctly with incorrect credentials provided
    def test_incorrect_login_credentials(self):
        tester = app.test_client(self)
        response = tester.post('/welcome', data=dict(email_address='incorrect@gmail.com', password='password'), follow_redirects=True) #Test to check if the POST request made on login works correctly when incorrect email address or password is provided.
        self.assertIn(b'Incorrect username or password!', response.data) #If the login details are incorrect, should get 'Incorrect username or password!' in the response
    
    def test_logout(self):
        tester = app.test_client(self)
        tester.post('/welcome', data=dict(email_address='jfallon@gmail.com', password='password'), follow_redirects=True) #login with correct credentials
        
        response = tester.get('/logout', follow_redirects=True) #test the /logout route
        self.assertIn(b'Logged out successfully!', response.data) #Check if the string 'Logged out successfully!'is contained in the response


    def test_home_page_requires_login(self):#Test to check if login is required before a user can access the home page
        tester = app.test_client(self)
        response = tester.get('/home', follow_redirects=True) #call the /home route
        self.assertTrue(b'You are not logged in!' in response.data) #If the user isn't logged in, it will be true


    # def test_forgot_password(self):
    #     tester = app.test_client(self)
    #     response = tester.post('/forgot-password', data=dict(first_name='james', last_name='fallon', email_address='jfallon@gmail.com'), follow_redirects=True) #call the /forgot-password route
    #     self.assertTrue(b'You successfully recovered your password. Please check your email.' in response.data) #If it successfully sends the email using the above details, this string will be true.
    
    
    def test_create_account(self): #Test the create account to make sure the user is logged into the home page after they create the account.
        tester = app.test_client(self)
        response = tester.post('/welcome', data=dict(first_name='John', last_name='Doe', email_address='johndoe@gmail.com', password='1234'), follow_redirects=True) #call the /forgot-password route
        self.assertIn(b'Home', response.data)

    # def test_create_event(self):
    #     tester = app.test_client(self)
    #     response = tester.post('/home', data=dict(event_name='Bowling', location='Athlone', date='16/02/2021', number_of_people=10))
    #     self.assertTrue(b'Successfully created an event' in response.data)

    def test_profile_page(self): #Test to check that the profile page can be retrieved
        tester = app.test_client(self) #Creates the test, where we use to send a request to and test the response

        tester.post('/welcome', data=dict(email_address='jfallon@gmail.com', password='password'), follow_redirects=True) #login with correct credentials

        response = tester.get('/profile', content_type='html/text') #Call the /profile route 
        self.assertEqual(response.status_code, 200) #and check the response status code equals 200
    
    def test_profile_page_data(self): #test to check that the profile page is displaying correctly
        tester = app.test_client(self) #Creates the test, where we use to send a request to and test the response

        tester.post('/welcome', data=dict(email_address='jfallon@gmail.com', password='password'), follow_redirects=True) #login with correct credentials

        response = tester.get('/profile', content_type='html/text') #Call the /profile route 
        self.assertTrue(b'Profile' in response.data)
    
    def test_profile_bio(self): #Test to check that the profile page bio can be changed
        tester = app.test_client(self) #Creates the test, where we use to send a request to and test the response

        tester.post('/welcome', data=dict(email_address='jfallon@gmail.com', password='password'), follow_redirects=True) #login with correct credent
        response = tester.get('/profile', content_type='html/text') #Call the /profile route 
        self.assertIn(b'Hey!', response.data) #If the profile bio is 'Hey!' on this account, assert to true
    
    def test_my_events_page(self):
        tester = app.test_client(self)
        tester.post('/welcome', data=dict(email_address='jfallon@gmail.com', password='password'), follow_redirects=True) #login with correct credent
        response = tester.get('/my-events', content_type='html/text') #Call the /profile route 
        self.assertIn(b'A summary of your Events', response.data) #If the profile bio is 'Hey!' on this account, assert to true

    # def test_session_data(self): #Can't test without accessing flask session data
    #     tester = app.test_client(self)
    #     tester.post('/welcome', data=dict(email_address='jfallon@gmail.com', password='password'), follow_redirects=True) #login with correct credent
    #     self.assertTrue(session['id'] == 4)
    
    # def test_event_page(self): #Can't test without accessing flask session data
    #     tester = app.test_client(self)
    #     tester.post('/welcome', data=dict(email_address='jfallon@gmail.com', password='password'), follow_redirects=True) #login with correct credent
    #     response = tester.get('/eventpage', content_type='html/text') #Call the /profile route 
    #     self.assertEqual(response.status_code, 200) #If the profile bio is 'Hey!' on this account, assert to true

    def test_delete_account(self): #if account exists, this will delete the account and the assert statement will be correct. Otherwise it will fail
        tester = app.test_client(self)
        tester.post('/welcome', data=dict(email_address='jamesmmfallon@gmail.com', password='12345'), follow_redirects=True) #login with correct credentials
        
        response = tester.get('/delete-account', follow_redirects=True) #test the /delete-account route
        self.assertIn(b'Your account has been deleted!', response.data) #Check if the string 'Your account has been deleted!'is contained in the response
if __name__ == '__main__':
    unittest.main()