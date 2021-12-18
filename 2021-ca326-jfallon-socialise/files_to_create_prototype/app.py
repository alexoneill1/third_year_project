from flask import Flask, render_template, request, redirect, session, url_for, flash #Import the flask module
from flask_mysqldb import MySQL #Allows for a mysql connection
import yaml #to write configuration files(hide sensitive information)
import MySQLdb.cursors


app = Flask(__name__)
#configure the database
db = yaml.load(open("db.yaml"))
app.config["MYSQL_HOST"] = db["mysql_host"] # This is sensitive information and we don't want to expose it. So we create a db.yaml file in order to store this information.
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]

app.secret_key = 'socialise is our third year project'
#instatiate an object for the mysql module
mysql = MySQL(app)

#Add a route to handle the case when a request is been made to the server.
@app.route("/create-account", methods=["GET", "POST"])
def insert_into_database():
    if request.method == "POST": #when the submit button on the form is pressed, a post request is made on the server
        #We want to use this POST request to fetch the form data.
        userDetails = request.form
        first_name = userDetails["first_name"]#name and email are the names which we gave to the form text fields
        last_name = userDetails["last_name"]
        email_address = userDetails["email_address"]
        password = userDetails["password"]
        cur = mysql.connection.cursor()#This allows us to execute queries on our mysql database
        cur.execute("INSERT INTO users(first_name, last_name, email_address, password) VALUES(%s, %s, %s, %s)",(first_name, last_name, email_address, password))#Insert the values into the database
        mysql.connection.commit()#Execute this command
        cur.close()#Close cursor as not using it anymore
        flash("You successfully created an account!")
        return redirect("/login")
    return render_template("create-account.html")#Looks for this file within a folder called templates

#@app.route("/users") # This route will display all the users
#def users():
    #cur = mysql.connection.cursor() #Get a connection to the database
    #resultValue = cur.execute("SELECT * FROM users") #use this select command to get all users
    #if resultValue > 0: #Check if the result is greater than 0(to show there are users in the database)
        #userDetails = cur.fetchall() # Fetch all the users and store in userDetails variable
        #return render_template("users.html", userDetails=userDetails)


@app.route("/login", methods =["GET", "POST"]) 
def login(): 
    msg = "" 
    if request.method == "POST" and "email_address" in request.form and "password" in request.form: 
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
            session["id"] = user["id"] 
            session["email_address"] = user["email_address"]
            session["first_name"] = user["first_name"]
            session["last_name"] = user["last_name"]
            session["full_name"] = user["first_name"] + " " + user["last_name"]
            #name = user["first_name"] + " " + user["last_name"]
           # msg = "Logged in successfully!"
            return redirect("/home")
            #return render_template("index.html", name=name)
        else: 
            msg = "Incorrect username or password!"
    
    return render_template("login.html", msg = msg)

@app.route("/home")
def home():
    if "id" in session:
        return render_template("index.html")
    else:
        flash("You are not logged in!")
        return redirect("/login")


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

def get_bio_from_db():#As this code is used in profile and edit profile, defined a function to access it in both pages. It gets the user's profile bio from the db and returns it
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)#This is a Cursor class that returns rows as dictionaries and stores the result set in the client.
    cur.execute("SELECT user_profile.profile_bio FROM user_profile join users on users.id = user_profile.user_id WHERE user_id = %s", (get_user_id(), ))
    user_bio = cur.fetchone()#This returns a dictionary called user_bio
    if user_bio != None:#If there is a bio related to that user in the dictionary
        bio = user_bio["profile_bio"]#Store the bio in the variable bio

    else:
        bio = ""#Otherwise set the bio to an empty string
    return bio
    #return render_template("edit-profile.html", full_name=get_full_name(), bio=bio)#Display to the user
@app.route("/edit-profile")
def edit_profile():

    return render_template("edit-profile.html")

@app.route("/biochange",methods =["GET","POST"])
def bio_change():

    if "id" in session:##This if statement is used to check if the user has logged in, if they haven't then they can't access any profile page or edit profile page

        if request.method == "POST":#When the user clicks submit on the form a POST request is sent
            #user_id = session["id"]#Get the user's id from the session
            bio = request.form["profile_bio"]#Grab the bio from the form the user just filled and store in a variable called "bio"
            session["bio"] = bio#Store the bio in the session so we can quickly access it whenever
            cur = mysql.connection.cursor()#This allows us to execute queries on our mysql database

            if cur.execute("select user_id from user_profile where user_id = %s",(get_user_id(), )) != None: #In order to make sure the user can edit their bio at any time, we need to check if the bio has already been created.
                cur.execute("DELETE FROM user_profile WHERE user_id = %s",(get_user_id(),))#If it has been created, it would therefore be in the database and so we need to delete the old entry so as to avoid a database duplicate error.
                mysql.connection.commit()#Execute this Delete command
                cur.execute("INSERT INTO user_profile(user_id, profile_bio) VALUES(%s, %s)",(get_user_id(), [bio],))#Once it has been deleted, we can then insert the new bio into the database
                mysql.connection.commit()#Execute this Insert command

            else:#Otherwise, the user has never created a bio and therefore we can just insert it in directly into the database.
                cur.execute("INSERT INTO user_profile(user_id, profile_bio) VALUES(%s, %s)",(get_user_id(), [bio]))#Insert the user_id and the bio value into the user_profile table. The user_id is a foreign key to the users table's id
                mysql.connection.commit()#Execute this command
                cur.close()#Close cursor as not using it anymore
                return redirect("/profile")
        
        if "bio" in session:#When the user clicks submit on the form, the bio will have been put into the session
            bio = session["bio"]#This retrieves the bio from the session and displays in the edit-profile page when they click submit
            return render_template("biochange.html", full_name=get_full_name(), bio=bio)
        
        else:
            bio = get_bio_from_db()
            return render_template("biochange.html", full_name=get_full_name(), bio=bio)#Display to the user
    else:
        flash("You are not logged in!")#If the user hasn't logged in, they are redirected back to the login page.
        return redirect("/login")

@app.route("/profile")
def profile():
    if "id" in session:##This if statement is used to check if the user has logged in, if they haven't then they can't access any profile page

        bio = get_bio_from_db()
        return render_template("profile.html", full_name=get_full_name(), bio=bio)#Display to the user
    else:
        flash("You are not logged in!")#If the user hasn't logged in, they are redirected back to the login page.
        return redirect("/login")


#Need to create a edit-profile page which is separate to the profile page. The edit page will be the one i already have(the form and the text), the profile will just have the text
#so if a user has already entered in data, it will be in the database and you can retrieve it from there and display on profile page. 2nd last else statment in the profile
# function above should work.
#Might need an if statement to check if there's a bio in the database, if there is display, otherwise just display their name and no bio

#Also look into how to do pop ups on the homepage rather than redirecting to a new page.

#when a user clicks on profile for the first time-It will only display their name and the form.
#when a user types in their bio for the first time, it stores in a session and then displays this for the user.--This however is not saved when the user logs out.
#implemented a way to grab the information from the database and display on the profile page.
#So if the user_profile has a bio in the database then it gets that. This acts as a way of saving their information to their profile page
#implemented an if statment to check if the profile_bio in user_profile has an id. If it does, we want to update it to reflect the new form data. Otherwise just insert into the database.

#Implemented a way to be able to restrict the user to only create account and login pages at first until they login. They can't access the profile page or home page until they log in.

@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("email_address", None)
    session.pop("first_name", None)
    session.pop("last_name", None)
    session.pop("bio", None)
    flash("Logged out successfully!", "info")
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)