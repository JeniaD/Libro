from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.config.from_object("config")

@app.route("/debug")
def debug():
    return render_template("base.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.args.get("login")
        password = request.args.get("password")

        flash("Login successful", "success")
        return redirect(url_for("index"))

    return render_template("login.html")
    

if __name__ == "__main__":
    app.run(debug=True)