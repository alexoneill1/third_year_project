from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import json
import csv


app = Flask(__name__)

@app.route('/login')         #declaring a route www.domain.ie/sayhello...
def mygreeting():               
    return render_template('login.html')

@app.route('/signin')         #declaring a route www.domain.ie/sayhello...
def signin():               
    return render_template('signin.html')

@app.route('/createaccount')         #declaring a route www.domain.ie/sayhello...
def createaccount():               
    return render_template('createaccount.html')

@app.route('/homepage')         #declaring a route www.domain.ie/sayhello...
def homepage():
    if request.method == "POST":
        #formdata is a dict
        formdata = request.form
        name = formdata['name']
        
        if name != None and name != "":
            return render_template('homepage.html', name=name)
        else:
            return "error"

    else:
        return render_template('homepage.html')


if __name__ == "__main__":
    app.run()                   #call the app


#running on http://127.0.0.1:5000/

