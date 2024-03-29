from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient

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
            message = "Username already exists. Please choose a different one."
            return render_template("regirstration.html", message=message, alert_class="alert-danger")

        user_data = {
            'username': username,
            'email': email,
            'password': password
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
        
        if user and user['password'] == password:
            session['username'] = user['username']
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid users. Please try again."
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

if __name__ == "__main__":
    app.run(debug=True)
