from flask import Flask, render_template, request, flash, redirect, url_for, session
from models import db, User
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config.from_object("config")
db.init_app(app)

@app.route("/debug")
def debug():
    return render_template("base.html")

@app.route("/")
def index():
    if not session.get("username"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            flash("Login successful", "success")
            session["username"] = user.username
            return redirect(url_for("index"))
        else:
            flash("Wrong credentials", "danger")

    return render_template("login.html")
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)