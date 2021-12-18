from flask import Flask, render_template, request, redirect, session, url_for #Import the flask module
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
            #name = user["first_name"] + " " + user["last_name"]
           # msg = "Logged in successfully!"
            return redirect("/home")
            #return render_template("index.html", name=name)
        else: 
            msg = "Incorrect username or password!"
    return render_template("login.html", msg = msg)

@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/profile")
def profile():
    #if "email_address" in session:
        first_name = session["first_name"]
        last_name = session["last_name"]
        full_name = first_name + " " + last_name
        return render_template("profile.html", full_name=full_name)


if __name__ == "__main__":
    app.run(debug=True)