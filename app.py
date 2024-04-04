import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for

app = Flask(__name__)

#Key FireBase detail
config = {
    'apiKey': "AIzaSyBFNw4UVBT8vHWNvh-JmTnk04YZuNGpTjE",
    'authDomain': "authentical-34a24.firebaseapp.com",
    'projectId': "authentical-34a24",
    'storageBucket': "authentical-34a24.appspot.com",
    'messagingSenderId': "911914926881",
    'appId': "1:911914926881:web:74c81134ba21c3b3e6b460",
    'measurementId': "G-NSHQRDWQTN",
    'databaseURL': "https://authentical-34a24-default-rtdb.asia-southeast1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()  
db = firebase.database()


person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}
#End setup website

#Login
@app.route("/")
def login():
    if person["is_logged_in"] == True:
        return redirect(url_for('welcome'))
    else:
        return render_template("sign-in.html")
    

#Sign up - Register
@app.route("/signup")
def signup():
    return render_template("sign-up.html")

#Welcome Page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template("index.html")
    else:
        return redirect(url_for('login'))
    
#if someone clikcs on login, they are redirected to /result
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        try:

            user = auth.sign_in_with_email_and_password(email, password)

            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]

            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]

            #set user session 
            #session['user'] = person["email"]

            return redirect(url_for('welcome'))
        except:

            return redirect(url_for('login'))
    else:
        if person['is_logged_in'] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))
        
#If someone clicks on register, they are redireted to /register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        name = result["name"]

        try:
            auth.create_user_with_email_and_password(email, password)

            user = auth.sign_in_with_email_and_password(email, password)

            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["name"] = name
            person["uid"] = user["localId"]

            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)

            request.cookies.pop()
            return redirect(url_for('welcome'))
        except:
            return redirect(url_for('register'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))
        
@app.route("/logout", methods=["POST", "GET"])
def logout():
    person["is_logged_in"] = False
    person["uid"] = ""
    person["email"] = ""
    person["name"] = ""
    return redirect(url_for('welcome'))


@app.after_request
def add_nocache_headers(response):
  response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Expires'] = '0'
  return response



if __name__ == "__main__":
    app.run()