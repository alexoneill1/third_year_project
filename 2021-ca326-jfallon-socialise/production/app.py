from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, make_response, json #Import the flask module
from flask_mysqldb import MySQL #Allows for a mysql connection
import yaml #to write configuration files(hide sensitive information)
import MySQLdb.cursors #Allow for database queries to be returned in different data structures e.g. dictionary
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_cors import CORS#This is imported to Prevent an error
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #tried to stop js file from caching

#configure the database

db = yaml.load(open("db.yaml"))
app.config["MYSQL_HOST"] = db["mysql_host"] # This is sensitive information and we don't want to expose it. So we create a db.yaml file in order to store this information.
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]

app.secret_key = 'socialise is our third year project'
#instatiate an object for the mysql module
mysql = MySQL(app)

socketio = SocketIO(app, cors_allowed_origins='*')#Prevent an error

mail = Mail(app) #The send emails to the user flask_mail is used and configured below. https://pythonhosted.org/Flask-Mail/

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'socialise3rdyearproject@gmail.com'
app.config['MAIL_PASSWORD'] = 'socialise2021'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



#Create account and login route deleted as it's all stored in /welcome

def user_creates_event(user_id, req): #Get the details of the event coming from the POST request
    eventName = req["eventName"]
    #print(eventName)
    location = req["location"]
    date = req["date"]
    numberOfPeople = req["numberOfPeople"]
    lat = req["lat"]
    lng = req["lng"]
                
    #print("lat:" + lat)
    #print("lng:" + lng)

    cur = mysql.connection.cursor()#This allows us to execute queries on our mysql database
    cur.execute("INSERT INTO events(user_id, event_name, location, date, number_of_people, latitude, longitude) VALUES(%s, %s, %s, %s, %s, %s, %s)",(user_id, eventName, location, date, numberOfPeople, lat, lng))#Insert the user_id, name location, date, number of people, lat and lng into the events table. The user_id is a foreign key to the users table's id
    mysql.connection.commit()#Execute this command
    cur.close()#Close cursor as not using it anymore

def store_event_lat_lng_in_session(req): #Want to store the latitude and longitude of the marker when a user clicks on it
#print('yes it worked')
    lat = req['lat'] #Get the lat
    lng = req['lng']#get the lng

    session['lat'] = lat #Store the lat and lng in the session. Every time a user clicks on an event, the session gets overwrote
    session['lng'] = lng

@app.route("/home", methods =["GET","POST"])#This gets the POST request from javascript and allows me to access the values sent over
def home():
    if "id" in session: #Check to see if a user has logged in

        if request.method == "POST": #Two different post requests happen on this route. Both are defined below
            req = request.get_json()#get the json data and Converts into python dictionary
            #print(req)


            if "eventName" in req:#This post request occurs when a user creates an event. The form containing the details such as event name, location, date, and coordinates are sent to the server and inserted into the database in the events table.
                user_creates_event(get_user_id(), req)
                make_response("Successfully created an event", 200)
                
            
            if req['lat']: #This post request waits for a user to click on an event marker on the map. Once clicked, the latitude and longitude of the marker is sent from the js to the server.          
                store_event_lat_lng_in_session(req)

        #If there's no POST request, then get all events from the database whenever /home is loaded
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)#This is a Cursor class that returns rows as dictionaries and stores the result set in the client.
        cur.execute("SELECT * FROM events") #Select all events in the database
        events = cur.fetchall()#This returns a tuple of dictionaries called events
        if events != None:
            #print(len(events))
            #print(events)
            #print([events[0]])
            res = events
            return render_template("index.html", res=json.dumps(res))  #Once we json.dump, "res"(result) becomes a json array. This can then be received from our javascript side

        return render_template("index.html")
    else:
        flash("You are not logged in!")
        return redirect("/welcome")

#The user can now click on the map on the homepage(index.html). This click will trigger an event to display a form to the user.
#The user fills out this form and clicks submit.
#When they click submit 2 things happen:
#1: The content of the form gets displayed as a popup in the location that the user clicks
#2: A POST request is sent to the server and from here the data is inserted into the database.

#Now, every time the home page is reloaded, the data is retrieved from the database and displayed as markers on the map.

#Getter functions to access the session data
def get_first_name():
    first_name = session["first_name"]
    return first_name

def get_last_name():
    last_name = session["last_name"]
    return last_name
def get_full_name():
    full_name = session["full_name"]
    return full_name
def get_user_id():
    user_id = session["id"]
    return user_id

def get_email_address():
    return session["email_address"]

def get_password():
    return session["password"]

def get_event_id():
    return session['event_id']

def get_bio_from_db(): #gets the user's profile bio from the db and returns it
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)#This is a Cursor class that returns rows as dictionaries and stores the result set in the client.
    cur.execute("SELECT user_profile.profile_bio FROM user_profile join users on users.id = user_profile.user_id WHERE user_id = %s", (get_user_id(), ))
    user_bio = cur.fetchone()#This returns a dictionary called user_bio
    if user_bio != None:#If there is a bio related to that user in the dictionary
        bio = user_bio["profile_bio"]#Store the bio in the variable bio

    else:
        bio = ""#Otherwise set the bio to an empty string
    return bio

#Deleted bio change and edit profile as it is all contained in profile



def get_my_events_from_db(user_id): #Get the user's events that they have joined
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)#This is a Cursor class that returns rows as dictionaries and stores the result set in the client.
    cur.execute("select events.event_id, event_name, location, date, latitude, longitude from events join event_participants on events.event_id = event_participants.event_id where event_participants.user_id = %s", (user_id, ))
    # #Select the event data from the database using the latitude and longitude
    user_events = cur.fetchall()
    return user_events

def change_profile_bio(user_id):
    #user_id = session["id"]#Get the user's id from the session
    bio = request.form["profile_bio"]#Grab the bio from the form the user just filled and store in a variable called "bio"
    session["bio"] = bio#Store the bio in the session so we can quickly access it whenever
    cur = mysql.connection.cursor()#This allows us to execute queries on our mysql database

    if cur.execute("select user_id from user_profile where user_id = %s",(user_id, )) != None: #In order to make sure the user can edit their bio at any time, we need to check if the bio has already been created.
        cur.execute("DELETE FROM user_profile WHERE user_id = %s",(user_id, ))#If it has been created, it would therefore be in the database and so we need to delete the old entry so as to avoid a database duplicate error.
        mysql.connection.commit()#Execute this Delete command
        cur.execute("INSERT INTO user_profile(user_id, profile_bio) VALUES(%s, %s)",(user_id, [bio], ))#Once it has been deleted, we can then insert the new bio into the database
        mysql.connection.commit()#Execute this Insert command
        #return redirect("/profile")

    else:#Otherwise, the user has never created a bio and therefore we can just insert it in directly into the database.
        cur.execute("INSERT INTO user_profile(user_id, profile_bio) VALUES(%s, %s)",(user_id, [bio]))#Insert the user_id and the bio value into the user_profile table. The user_id is a foreign key to the users table's id
        mysql.connection.commit()#Execute this command
        cur.close()#Close cursor as not using it anymore
        return redirect("/profile")

@app.route("/profile", methods =["GET","POST"])
def profile():
    if "id" in session:##This if statement is used to check if the user has logged in, if they haven't then they can't access any profile page
        
        #Get the user's events that they have joined
        user_events = get_my_events_from_db(get_user_id())
        #print(user_events)

        ###adding in profile bio code
        if request.method == "POST":#When the user clicks submit on the form a POST request is sent

            change_profile_bio(get_user_id()) #Call this function if a user wants to change their profile description
        
        #get the user's bio from the database
        bio = get_bio_from_db()
        return render_template("profile.html", full_name=get_full_name(), bio=bio, user_events=json.dumps(user_events))#Display to the user

    else:
        flash("You are not logged in!")#If the user hasn't logged in, they are redirected back to the login page.
        return redirect("/welcome")



def get_event_messages_from_db(event_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)#This allows us to execute queries on our mysql database
    cur.execute("select users.first_name, users.last_name, event_messages.message, event_messages.event_id from users join event_messages on users.id = event_messages.user_id where event_messages.event_id = %s", (event_id, ))
    event_messages = cur.fetchall()#This returns a dictionary called event
    if event_messages != None:
        #print(event_messages)
        event_messages = event_messages
        return event_messages

def get_event_participants_from_db(event_id):
    #Getting the participants of the event if they are already a member
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)#This allows us to execute queries on our mysql database
        cur.execute("select participant_id, users.first_name, users.last_name, user_id, event_id from users join event_participants on users.id = event_participants.user_id where event_id = %s",(event_id, )) #Check to see if that user is already apart of the event
        participants = cur.fetchall()#Grab the row from the database
        return participants

def insert_user_into_participants_table(user_id, event_id): #Need to normalise this table(get rid of first name and last name as they are already stored in the users table)
    #Inserting the user into the participants table if not already there
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("select user_id, event_id from event_participants where user_id = %s and event_id = %s",(user_id, event_id, )) #Check to see if that user is already apart of the event
    result = cur.fetchone()#Grab the row from the database
    if result == None: #If the user has not already joined the event
        cur.execute("INSERT INTO event_participants (event_id, user_id) VALUES(%s, %s)",(event_id, user_id, )) #Insert that user into the database as a participant of that event
        mysql.connection.commit()#Execute this Insert command
        cur.close()

@app.route('/eventpage', methods =["GET","POST"])
def event():
    if 'lat' in request.args: #If the user is on the my-events page, when they click a link, the lat and lng will be part of the query string. We want to grab these coordinates and put them in our session
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        #print(lat)

        session['lat'] = lat #Store the lat and lng in the session
        session['lng'] = lng
        
    if 'lat' in session:
    #Latitude and longitude are found in the /home route (when a user clicks on a marker). Then these coordinates are stored in the session
    
        latitude = session['lat'] #Store the latitude and longitude in a variable
        longitude = session['lng']

        #Grab the data from the database associated with that specific event using the latitude and longitude coming from the session. Eventpage can only be accessed if
        #a marker was clicked(only if the post request has been made)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)#This is a Cursor class that returns rows as dictionaries and stores the result set in the client.
        cur.execute("select event_id, user_id, event_name, location, date, number_of_people from events where latitude = %s and longitude = %s", (latitude, longitude, ))
        #Select the event data from the database using the latitude and longitude
        event = cur.fetchone()#This returns a dictionary called event
        #print(event)
        event_name = event["event_name"]
        location = event["location"]
        date = event["date"]
        #print(event_name, location, date)
        event_id = event['event_id'] #Get the event id that the user clicked
        session['event_id'] = event_id

        #PARTICIPANTS
        # #Inserting the user into the participants table if not already there
        insert_user_into_participants_table(get_user_id(), get_event_id())

        #Getting the participants of the event if they are already a member
        participants = get_event_participants_from_db(get_event_id())

        #MESSAGES
        #if any messages have been sent already, we want to get these messages and display on the page
        event_messages = get_event_messages_from_db(get_event_id())
        

        #need to convert the event_id into a string so that the chat room works(using event_id as the chatroom number)
        event_id = str(event_id) #The chat room needs to be supplied as a string

        #Want the latitude and longitude stored in a dictionary as this will be passed over to our javascript file and from there will display a marker on a new map at this position
        latlon = {
            'latitude': latitude,
            'longitude': longitude
        }

        return render_template('event.html', room=event_id, user_id=get_user_id(), username=get_full_name(), event_name=event_name, location=location, date=date, participants=json.dumps(participants), event_messages=json.dumps(event_messages), latlon=json.dumps(latlon))
    else:
        return redirect('/home')

#When a user creates an event, the event_id is used as the room name
#The user then chats within that chat room

#Socketio used for chat functionality
#https://flask-socketio.readthedocs.io/en/latest/ where i learned about socketio
#socketio has "events". These defaults events are "connect", "disconnect", "message". Here socketio.on means you are listening for a certain event. In the following code it is listening for the events "join_room" and "send_message"

@socketio.on('join_room')#This event is triggered when "socket.emit('join_room')" is executed in javascript
def join_room_event(json_data): #This json data has the username and room of the user who has connected and joined
    join_room(json_data['room']) #User joins the room once they connect

@socketio.on('send_message')
def send_message_event(json_data):
    socketio.emit('receive_message', json_data, room=json_data['room']) #We want to only send the data to the room in which the message is coming from. We only want the users in the same room to see the message
    #'receive_message' is the name of the custom event and this is handled in javascript
    
    #print(json_data)
    #insert message into database
    cur = mysql.connection.cursor()#This allows us to execute queries on our mysql database
    cur.execute("INSERT INTO event_messages(event_id, user_id, message) VALUES(%s, %s, %s)",(int(json_data['room']), int(json_data['user_id']), json_data['message']))#Insert the user_id, name location, date, number of people, lat and lng into the events table. The user_id is a foreign key to the users table's id
    mysql.connection.commit()#Execute this command
    cur.close()#Close cursor as not using it anymore


    #Users can now join an event. When they click join event, their username is put into the database associated with that event and on loading the eventpage
    #all participates who have joined are displayed on the page for all users to see.

def send_confirmation_email(email_address, first_name, password): #Refactored code, now have confirmation email in a function
    msg = Message('Confirmation email', sender = 'socialise3rdyearproject@gmail.com', recipients=[email_address]) #sends an email to the user who created an account.
    msg.body = 'Hi ' + first_name + ',' + '\n' + '\n' + 'Thanks for joining Socialise!' + '\n' + '\n' + 'To access your account, please login with your email address and password.' + '\n' + '\n' + 'Email Address: ' + email_address + '\n' +'Password: ' + password + '\n' + '\n' + 'Kind regards, ' + '\n' + 'The Socialise Team'
    mail.send(msg)

def create_account(): #Function that when called, creates the users account by inserting their details into the database
    #if "first_name" in request.form: #Check to see if it's a create account POST request
    userDetails = request.form
    first_name = userDetails["first_name"]#name and email are the names which we gave to the form text fields
    last_name = userDetails["last_name"]
    email_address = userDetails["email_address"]
    password = userDetails["password"]
    cur = mysql.connection.cursor()#This allows us to execute queries on our mysql database
    cur.execute("INSERT INTO users(first_name, last_name, email_address, password) VALUES(%s, %s, %s, %s)",(first_name, last_name, email_address, password))#Insert the values into the database
    mysql.connection.commit()#Execute this command
    cur.close()#Close cursor as not using it anymore
    #flash("You successfully created an account! Please login below")
        
    send_confirmation_email(email_address, first_name, password) #Sends a confirmation email to the user when their account has been created.

#def login():
    
@app.route("/welcome", methods =["GET","POST"])
def welcome():
    if "id" in session:
        return redirect("/home")

    if request.method == "POST": #when the submit button on the form is pressed, a post request is made on the server
        if "first_name" in request.form:
            create_account()
        


        #We wanted the user to be logged in immediately after they create an account so they wouldn't have to re-enter any details.
        #Logging in will work in this case and in the case where the user just wants to log in to an existing account.
        #Login functionality:
        msg = "" 
        if request.method == "POST" and "email_address" in request.form and "password" in request.form: #Check if it's a login POST request
            email_address = request.form["email_address"] 
            password = request.form["password"] 
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)#This is a Cursor class that returns rows as dictionaries and stores the result set in the client.
            cur.execute("SELECT * FROM users WHERE email_address = % s AND password = % s", (email_address, password, )) 
            user = cur.fetchone() #This method retrieves the next row of a query result set and returns a single sequence, or None if no more rows are available
            if user: #If it found a user using the credentials provided then:
                session["loggedin"] = True # Session is the way flask handles logging in and logging out of the web app.
                #It stores the active user’s ID in the session, and let you log them in and out easily.
                # Let you restrict views (webpages) to logged-in (or logged-out) users.
                #A way of passing information around the web pages
                #https://flask-session.readthedocs.io/en/latest/ used this site to learn about sessions
                session["id"] = user["id"] 
                session["email_address"] = user["email_address"]
                session["first_name"] = user["first_name"]
                session["last_name"] = user["last_name"]
                session["full_name"] = user["first_name"] + " " + user["last_name"]
                session["password"] = user["password"]
                #name = user["first_name"] + " " + user["last_name"]
            # msg = "Logged in successfully!"
                return redirect("/home")
                #return render_template("index.html", name=name)
            else: 
                msg = "Incorrect username or password!"
        
        return render_template('welcome.html', msg = msg)
    return render_template('welcome.html')


@app.route('/my-events', methods =["GET","POST"])
def my_events():
    #Grab the data from the database(all the user's events that they have joined)
    #Display on webpage in a list/table
    #Want a button that brings the user to that specific event
    #Have a button that onclick, gets the coordinates of the event(how does it get the coordinates? what to query with?), store in session and return redirect to /eventpage.
    #/eventpage should handle the rest once coordinates are provided.
    user_events = get_my_events_from_db(get_user_id()) #Call the function defined above as it's used in /profile too
    
    return render_template('my-events.html', user_events=json.dumps(user_events))

@app.route("/logout") #Pop everything from the session when a user logs-out. Redirect to the welcome page
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("email_address", None)
    session.pop("first_name", None)
    session.pop("last_name", None)
    session.pop("bio", None)
    session.pop("lat", None)
    session.pop("lng", None)
    session.pop("password", None)
    session.pop("event_id", None)
    flash("Logged out successfully!", "info")
    return redirect("/welcome")

def deleted_account_email(first_name, email_address):
    msg = Message('Account Deleted', sender = 'socialise3rdyearproject@gmail.com', recipients=[email_address]) #sends an email to the user to confirm they deleted their account
    msg.body = 'Hi ' + first_name + ',' + '\n' + '\n' + 'Sorry to see you go!' + '\n' + '\n' + 'We hope you enjoyed your time on Socialise. Feel free to join again anytime!' + '\n' + '\n' + 'Kind regards, ' + '\n' + 'The Socialise Team'
    mail.send(msg)

@app.route("/delete-account", methods =["GET","POST"])
def delete_account():
    cur = mysql.connection.cursor()#This allows us to execute queries on our mysql database
    cur.execute("delete from users where id = %s", (get_user_id(), ))#Delete the user from the database
    mysql.connection.commit()#Execute this command
    cur.close()#Close cursor as not using it anymore
    flash("Your account has been deleted!")
    
    deleted_account_email(get_first_name(), get_email_address()) #Refactored code and placed in a function

    return redirect('/logout')

def remove_user_from_participants_list(user_id, event_id):
    cur = mysql.connection.cursor()#This allows us to execute queries on our mysql database
    cur.execute("delete from event_participants where user_id = %s and event_id = %s", (user_id, event_id, ))#Delete the user from the event participants list
    mysql.connection.commit()#Execute this command

def remove_user_messages(user_id, event_id):
    cur = mysql.connection.cursor()#This allows us to execute queries on our mysql database
    cur.execute("delete from event_messages where user_id = %s and event_id = %s ", (user_id, event_id, ))#Delete the user's messages from the event messages
    mysql.connection.commit()#Execute this command
    cur.close()#Close cursor as not using it anymore

@app.route("/leave-event", methods=["GET","POST"]) #This deletes the user from the participants of the event and deletes that user's messages
def leave_event():
    remove_user_from_participants_list(get_user_id(), get_event_id()) #Refactored code, now stored in a function

    remove_user_messages(get_user_id(), get_event_id()) #Refactored code, now stored in a function
    
    return redirect("/home")


@app.route("/delete-event", methods=["GET","POST"])
def delete_event():
    cur = mysql.connection.cursor()#This allows us to execute queries on our mysql database
    cur.execute("select event_name from events where user_id = %s and event_id = %s",( get_user_id(), get_event_id(), )) #Check to see if that user created the event
    event = cur.fetchone()
    if event == None: #If it returns None, then we know that user isn't the host and therefore can't delete the event
        #print(event)
        flash('Only the host can delete the event')
        return redirect('/eventpage')
    else:
        cur.execute("delete from events where user_id = %s and event_id = %s", (get_user_id(), get_event_id()))#Delete the event from the database
        mysql.connection.commit()#Execute this command
        return redirect("/home")

def forgot_password_email(email_address, first_name, password):
    msg = Message('Forgot Password', sender = 'socialise3rdyearproject@gmail.com', recipients=[email_address]) #sends an email to the user giving them their password
    msg.body = 'Hi ' + first_name + ',' + '\n' + '\n' + 'Your password for your Socialise account is below!' + '\n' + '\n' +  'Password: '+ password + '\n' + '\n' + 'Kind regards, ' + '\n' + 'The Socialise Team'
    mail.send(msg)

@app.route('/forgot-password', methods=["GET","POST"])
def forgot_password():
    if request.method == "POST": #when the submit button on the form is pressed, a post request is made on the server
        #We want to use this POST request to fetch the form data.
        userDetails = request.form #get the details the user entered into the form
        first_name = userDetails["first_name"]
        last_name = userDetails["last_name"]
        email_address = userDetails["email_address"]

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)#This allows us to execute queries on our mysql database
        cur.execute("SELECT password from users where first_name = %s and last_name = %s and email_address = %s",(first_name, last_name, email_address, ))#Insert the values into the database
        password = cur.fetchone() #Grab the row and store it in a variable called password (password is a dictionary containing the user's password)
        #print(password)
        password = password['password'] #Get the password from the dictionary

        forgot_password_email(email_address, first_name, password) #Refactored code, calls a function to send an email to the user
        
        flash("You successfully recovered your password. Please check your email.")
        return redirect('/welcome')
    return render_template('forgot-password.html')

@app.route('/')
def redirect_to_welcome():
    return redirect('/welcome')


if __name__ == "__main__":
    #app.run(debug=True)
    # app.run(debug=True)
    socketio.run(app, debug=True)