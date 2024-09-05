from flask import Flask, render_template, request, flash, redirect, url_for, session
from models import db, User, Database
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)
app.config.from_object("config")
db.init_app(app)

def formatNumber(value):
    if value < 1_000:
        return str(value)
    elif value < 1_000_000:
        return f"{value / 1_000:.1f}K"
    else:
        return f"{value / 1_000_000:.1f}M"

app.jinja_env.filters["formatNumber"] = formatNumber

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

@app.route("/databases", methods=["GET", "POST"])
def databases():
    if not session.get("username"):
        return redirect(url_for("login"))

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file detected", "danger")
            return render_template("databases.html") # return redirect(request.url)
        file = request.files["file"]
        if not file.filename:
            flash("No file detected", "danger")
            return render_template("databases.html")
        
        if file:
            filename = secure_filename(file.filename)
            fileSize = len(file.read())
            file.seek(0)

            newDB = Database(name=filename, fileSize=fileSize)
            db.session.add(newDB)
            db.session.commit()

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], str(newDB.id))
            file.save(filepath)

            flash("Upload successful", "success")
            return redirect(url_for("databases"))

    databases = Database.query.all()
    return render_template("databases.html", databases=databases)

@app.route("/databases/<int:id>", methods=["GET", "POST"])
def viewDB(id):
    if not session.get("username"):
        return redirect(url_for("login"))
    
    database = Database.query.filter_by(id=id).first()
    if not database:
        # flash("No database was found with that ID", "danger")
        return redirect(url_for("databases"))
    
    if request.method == "POST":
        name = request.form["name"]
        if name and len(name) > 1 and len(name) < 100:
            database.name = name
            db.session.commit()
            return redirect(request.url)
    
    return render_template("database.html", database=database)

@app.route("/databases/delete/<int:id>")
def removeDB(id):
    if not session.get("username"):
        return redirect(url_for("login"))
    
    database = Database.query.filter_by(id=id).first()

    if database:
        try:
            path = os.path.join("static/uploads", str(database.id))
            if os.path.exists(path): os.remove(path)

            db.session.delete(database)
            db.session.commit()
        except Exception as e:
            flash("Unknown error occurred: " + str(e), "danger")
            return redirect(url_for("databases"))

    flash("Removal successful", "success")
    return redirect(url_for("databases"))

@app.route("/search", methods=["GET", "POST"])
def search():
    if not session.get("username"):
        return redirect(url_for("login"))
    
    if request.method == "POST":
        query = request.form.get("query").strip()
        if query:
            start = time.time()
            results = []
            entries = 0 # Change to in-database addition
            databases = Database.query.all()
            for database in databases:
                path = os.path.join("static/uploads", str(database.id))
                with open(path, 'r') as db:
                    lines = db.readlines()
                    entries += len(lines)
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            results.append({
                                "text": line.strip(),
                                "line": i + 1,
                                "filename": database.name
                            })
            return render_template("search.html", query=query, results=results, speed=round(time.time()-start, 5), dbnum=len(Database.query.all()), entries=entries)
    
    return render_template("search.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)