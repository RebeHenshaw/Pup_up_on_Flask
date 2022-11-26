from cs50 import SQL
from flask import Flask, redirect, render_template, session, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import random
import helpers

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:////home/rlhenshaw/mysite/Pup_up/doggo.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Homepage allows you to search for pups without logging in.
@app.route('/', methods=["GET"])
def dog():
        return render_template("dog.html")


# only accepts GET requests to find a random dog
@app.route('/get_dog')
def get_dog():
    zipcode = request.args.get("zip")
    if not zipcode:
        return render_template("error.html", error="bad zip")
    url = f"?type=dog&size=small,medium,large,xlarge&location={zipcode}&distance=10"
    data = requests.get(helpers.URL_BASE + url, headers=helpers.HEADER).json()
    try:

        dog_number = random.randint(0, len(data['animals']) - 1)
    except:
        return render_template('error.html', error="Zipcode didn't return any results")
    dog = data['animals'][dog_number]
    photo = helpers.get_image(dog)
    info = helpers.get_info(dog, photo)
    thought = helpers.get_thought(dog)
    return render_template("get_dog.html", info=info, thought=thought)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username") or not request.form.get("password"):
            error = "All Fields Required"
            return render_template('login.html', error=error)

        # Query database for username
        person = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(person) != 1 or not check_password_hash(person[0]["hash"], request.form.get("password")):
            error = "Invalid Credentials"
            return render_template('login.html', error=error)

        # Remember which user has logged in
        session["user_id"] = person[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # get username
        username = request.form.get("username")

        # check username was provided
        if not username:
            error = "All Fields Required"
            return render_template("register.html", error=error)

        # check if username is valid
        exists = db.execute("SELECT * FROM users WHERE username = ?", username)
        if exists:
            error = "Username unavailable"
            return render_template("register.html", error=error)

        # get password twice
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # check if blank
        if not password or not confirmation:
            error = "All Fields Required"
            return render_template("register.html", error=error)

        # check if passwords do not match.
        if not password == confirmation:
            error = "Passwords Must Match"
            return render_template("register.html", error=error)

        # hash the password
        hash = generate_password_hash(password)

        # if pass all checks, create user (insert into database)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        # log user in once registered
        person = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = person[0]["id"]
        return redirect("/")

    return render_template("register.html")

@app.route("/saved", methods=["GET", "POST"])
def save():
    # makes sure user is logged in
    try:
        loggedin = session["user_id"]
    except:
        error= "You must be logged in to have saved dogs."
        return render_template("login.html", error=error)
    if request.method == "GET":
        # requests dogs from database order by date saved
        ids = db.execute("SELECT dog_id FROM users_dogs WHERE user_id = ? ORDER BY date_saved", session["user_id"])
        # list of dicts to list
        saved_ids = []
        for each in ids:
            for k, v in each.items():
                saved_ids.append(v)
        saved = db.execute("SELECT * FROM dogs WHERE id IN (?)", saved_ids)
        if not saved:
            return render_template("saved.html", message="No saved dogs")
        return render_template("saved.html", saved=saved)
    if request.method == "POST":
        # get the dog info from hidden form elements
        url = request.form.get("url")
        # is the dog in the data base? check the url
        dog_id = db.execute("SELECT id FROM dogs WHERE url = ?", url)
        if dog_id:

            # don't let a user save twice
            already_saved = db.execute("SELECT dog_id FROM users_dogs WHERE user_id = ?", session["user_id"])
            saved_ids = [] # dogs user already saved
            for each in already_saved:
                for k, v in each.items():
                    saved_ids.append(v)
            # update number of saves

            if not dog_id[0]['id'] in saved_ids:
                db.execute("UPDATE dogs SET saves = saves+1 WHERE id = ?", dog_id[0]['id'])
                db.execute("INSERT INTO users_dogs (user_id, dog_id) VALUES (?, ?)", session["user_id"], dog_id[0]['id'])
        else:
            # insert into dogs
            name = request.form.get("name")
            image = request.form.get("photo")
            age = request.form.get("age")
            breed = request.form.get("breed")
            db.execute("INSERT INTO dogs(url, image_url, name, age, breed, saves) VALUES (?, ?, ?, ?, ?, ?)", url, image, name, age, breed, 1 )
            dog_id = db.execute("SELECT id FROM dogs WHERE url = ?", url)
            # updated users_dogs
            db.execute("INSERT INTO users_dogs (user_id, dog_id) VALUES (?, ?)", session["user_id"], dog_id[0]['id'])

        return redirect("/saved")

@app.route("/delete", methods=["GET", "POST"])
def delete():
    """Deletes saved dog from user and reduces saved count, but keeps the dog in the dog table"""
    id = request.form.get('id')
    if not id:
        return redirect('/saved')
    db.execute("DELETE FROM users_dogs WHERE user_id = ? AND dog_id = ?", session['user_id'], id)
    db.execute("UPDATE dogs SET saves = saves - 1 WHERE id = ?", id)
    return redirect('/saved')

