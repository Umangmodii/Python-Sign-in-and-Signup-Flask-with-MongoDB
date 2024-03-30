from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
app.secret_key = "12345"  # Set a secret key for session management

# Configure MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['Flask_Form']
users_collection = db['Registration']

@app.route("/", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            message = "Username already exists! Please choose a different one."
            return render_template("regirstration.html", message=message, alert_class="alert-danger")

        # Hash the password before saving to the database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            'username': username,
            'email': email,
            'password': hashed_password
        }
        users_collection.insert_one(user_data)
        
        message = "Registration successful! Please log in."
        alert_class = "alert-success"
        return render_template("login.html", message=message, alert_class=alert_class)

    return render_template("regirstration.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users_collection.find_one({'username': username})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['username'] = user['username']
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials! Please try again."
            return render_template("login.html", error=error)
    
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session['username'])
    else: 
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("login"))

@app.route("/forget-password", methods=['GET', 'POST'])
def forget_password():
    if request.method == "POST":
        email = request.form.get("email")
        new_password = request.form.get("new_password")
        
        user = users_collection.find_one({'email': email})
        if user:
            # Update the user's password in the database
            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            users_collection.update_one({'email': email}, {'$set': {'password': hashed_new_password}})
            message = "Password changed successfully! Please log in with your new password."
            return render_template("login.html", message=message, alert_class="alert-success")
        else:
            error = "Email not found! Please try again."
            return render_template("forget-password.html", error=error)
    
    return render_template("forget-password.html")

if __name__ == "__main__":
    app.run(debug=True)
