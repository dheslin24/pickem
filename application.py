#!/usr/bin/env python3

from cs50 import SQL 
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from flask_sslify import SSLify
# from flask_session import Sessions
from passlib.apps import custom_app_context as pwd_context
#from tempfile import mkdtemp
from werkzeug.serving import make_ssl_devcert, run_simple
import sys

from helpers import *

print("python version: {}".format(sys.version))

'''
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('ssl.key')
context.use_certificate_file('ssl.cert')
'''

# configure application
app = Flask(__name__)
#sslify = SSLify(app)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# run_simple('localhost', 5000, application, ssl_context=('/home/pi/pickem/dheslin/ssl.cert', '/home/pi/pickem/dheslin/ssl.key'))
# custom filter
##app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///pickem.db")


# INDEX - main page.
@app.route("/")
@login_required
def index():

    users = db.execute("SELECT userid, username FROM users")
    print("user list from db {}".format(users))
    print("user test dh {}".format(users[0]["userid"]))

    i = 0
    for user in users:
        uid = users[i]["userid"]
        # check if they have any picks at all first
        has_picks = db.execute("SELECT DISTINCT userid FROM picks WHERE userid = :uid", uid=uid)
        print("has picks return: {}".format(has_picks))

        if not has_picks:
            wins = 0
            db.execute("UPDATE wins SET wins = :wins WHERE userid = :uid", uid=uid, wins=wins)
            print("testdh in not userid: {} has {} wins".format(uid, wins))
        else:
            wins = tally_wins(uid)
            print("wins in else {}".format(wins))
            db.execute("UPDATE wins SET wins = :wins WHERE userid = :uid", uid=uid, wins=wins)
            print("testdh in else userid: {} has {} wins".format(uid, wins))
        i = i + 1
        wins = 0

    standings = db.execute("SELECT users.username, wins.wins \
        FROM users INNER JOIN wins ON users.userid=wins.userid \
        ORDER BY wins.wins DESC")

    print("standings: {}".format(standings))

    return render_template("standings.html", standings=standings)


def calc_winner(gameid):
    fav_team   = db.execute("SELECT fav_team    FROM results WHERE gameid = :gameid", gameid=gameid)
    dog_team   = db.execute("SELECT dog_team    FROM results WHERE gameid = :gameid", gameid=gameid)
    fav_score  = db.execute("SELECT fav_score   FROM results WHERE gameid = :gameid", gameid=gameid)
    dog_score  = db.execute("SELECT dog_score   FROM results WHERE gameid = :gameid", gameid=gameid)
    line       = db.execute("SELECT line        FROM games   WHERE gameid = :gameid", gameid=gameid)

    winner = []

    # retrieve row 0 in dict that is returned by db.execute above
    # should never have more than 1 row
    if fav_score[0]["fav_score"] + line[0]["line"] > dog_score[0]["dog_score"]:
        winner = fav_team[0]["fav_team"]
    else:
        winner = dog_team[0]["dog_team"]

    return winner


# this is an attempt to iterate through user db, and run calc_winner for each pick
def tally_wins(user):
    # i will try to JOIN this with picks table
    # users = db.execute("SELECT username, userid FROM users")
    wins = 0

    # this below will only return the most latest picks by the userid passed in
    # this way we can keep history of changes
    picks = db.execute("SELECT *, max(timestamp) AS latest FROM picks \
        WHERE userid=:user GROUP BY userid", user=user)

    print("latest picks for user {}".format(picks))

    # how many results are there?
    total_results = db.execute("SELECT max(gameid) FROM results")
    print("total results = {}".format(total_results[0]["max(gameid)"]))

    # DH TODO - will revisit this below to properly iterate.  needed db changes i think.
    # this works for now
    
    if total_results[0]["max(gameid)"] == 0 or total_results[0]["max(gameid)"] == None:
        return wins

    if total_results[0]["max(gameid)"] >= 1:
        if calc_winner(1) == picks[0]["pick_1"]:
            wins = wins + 1

    if total_results[0]["max(gameid)"] >= 2:
        if calc_winner(2) == picks[0]["pick_2"]:
            wins = wins + 1

    if total_results[0]["max(gameid)"] >= 3:
        if calc_winner(3) == picks[0]["pick_3"]:
            wins = wins + 1

    if total_results[0]["max(gameid)"] >= 4:
        if calc_winner(4) == picks[0]["pick_4"]:
            wins = wins + 1

    if total_results[0]["max(gameid)"] >= 5:
        if calc_winner(5) == picks[0]["pick_5"]:
            wins = wins + 1

    if total_results[0]["max(gameid)"] >= 6:
        if calc_winner(6) == picks[0]["pick_6"]:
            wins = wins + 1

    if total_results[0]["max(gameid)"] >= 7:
        if calc_winner(7) == picks[0]["pick_7"]:
            wins = wins + 1

    if total_results[0]["max(gameid)"] >= 8:
        if calc_winner(8) == picks[0]["pick_8"]:
            wins = wins + 1

    if total_results[0]["max(gameid)"] >= 9:
        if calc_winner(9) == picks[0]["pick_9"]:
            wins = wins + 1

    if total_results[0]["max(gameid)"] >= 10:
        if calc_winner(10) == picks[0]["pick_10"]:
            wins = wins + 1

    if total_results[0]["max(gameid)"] >= 11:
        if calc_winner(11) == picks[0]["pick_11"]:
            wins = wins + 1

    print("wins total test {}".format(wins))

    return wins


# Admin - Make Visible Routine
# this will control which 'view_picks' html is displayed
# this is to control when users can see other users picks
# 0 - before any game is played, pre WC round
# 1 - display all WC picks
# 2 - display all DIV picks
# 3 - display all CONF picks
# 4 - display ALL picks (sb & tie break included)
def make_visible():
    week_num = db.execute("SELECT week_number FROM week")
    make_visible = week_num[0]['week_number']
    print("make visible routine is {}".format(make_visible))
    return make_visible


# routine to change make visible setting
# see make visible routine.. this controls what users can see and pick
@app.route("/set_week", methods=["GET", "POST"])
@login_required
def set_week():
    if request.method == "POST":
        week = request.form.get("set_week")
        db.execute("UPDATE week SET week_number = :week WHERE id = 0", week=week)
        return render_template("standings.html")

    else:
        user = session['userid']
        chk_user = db.execute("SELECT IsAdmin FROM users WHERE userid = :user", user=user)
        if chk_user[0]['IsAdmin'] == "N":
            return render_template("apology.html")
        return render_template("set_week.html")

# Admin routine - just a page with links to the real admin tools
# checks to make sure you're actually an admin
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    user = session['userid']
    chk_user = db.execute("SELECT IsAdmin FROM users WHERE userid = :user", user=user)
    if chk_user[0]['IsAdmin'] == "N":
        return render_template("apology.html")
    return render_template("admin.html")


#Display standings routine
@app.route("/standings", methods=["GET", "POST"])
@login_required
def standings():

    users = db.execute("SELECT userid, username FROM users")
    print("user list from db {}".format(users))
    print("user test dh {}".format(users[0]["userid"]))

    i = 0
    for user in users:
        uid = users[i]["userid"]
        # check if they have any picks at all first
        has_picks = db.execute("SELECT DISTINCT userid FROM picks WHERE userid = :uid", uid=uid)
        print("has picks return: {}".format(has_picks))

        # had to put this in as if some user havent picked yet, it crashes - this protects
        if not has_picks:
            wins = 0
            db.execute("UPDATE wins SET wins = :wins WHERE userid = :uid", uid=uid, wins=wins)
            print("testdh in not userid: {} has {} wins".format(uid, wins))
        else:
            wins = tally_wins(uid)
            print("wins in else {}".format(wins))
            db.execute("UPDATE wins SET wins = :wins WHERE userid = :uid", uid=uid, wins=wins)
            print("testdh in else userid: {} has {} wins".format(uid, wins))
        i = i + 1
        wins = 0

    standings = db.execute("SELECT users.username, wins.wins FROM users \
        INNER JOIN wins ON users.userid=wins.userid \
        ORDER BY wins.wins DESC")

    print("standings: {}".format(standings))

    return render_template("standings.html", standings=standings)


# View all picks routine
# DH TODO - need to add for loop to iterate over table and display results
@app.route("/view_picks")
@login_required
def view_picks():

    all_picks = db.execute("SELECT *, users.username, max(timestamp) AS latest \
        FROM picks \
        INNER JOIN users ON users.userid=picks.userid \
        GROUP BY picks.userid" \
        )

    # the make visible calls are to control what users can see
    # they can't see other users until picks are locked in
    if make_visible() == 0:
        return render_template("view_picks_0.html", all_picks=all_picks)
    if make_visible() == 1:
        return render_template("view_picks_wc.html", all_picks=all_picks)
    if make_visible() == 2:
        return render_template("view_picks_div.html", all_picks=all_picks)
    if make_visible() == 3:
        return render_template("view_picks_conf.html", all_picks=all_picks)
    if make_visible() == 4:
        return render_template("view_picks.html", all_picks=all_picks)


# LOGIN routine
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["userid"] = rows[0]["userid"]
        print("userid is: {}".format(rows[0]["userid"]))

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# LOGOUT routine
@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))


# Make Picks routine
@app.route("/make_picks", methods=["GET", "POST"])
@login_required
def make_picks():
    if request.method == "POST":

        # gets picks from radio button options in make_picks
        w1g1 = request.form.get("Week 1 Game 1")
        w1g2 = request.form.get("Week 1 Game 2")
        w1g3 = request.form.get("Week 1 Game 3")
        w1g4 = request.form.get("Week 1 Game 4")
        w2g1 = request.form.get("Week 2 Game 1")
        w2g2 = request.form.get("Week 2 Game 2")
        w2g3 = request.form.get("Week 2 Game 3")
        w2g4 = request.form.get("Week 2 Game 4")
        w3g1 = request.form.get("Week 3 Game 1")
        w3g2 = request.form.get("Week 3 Game 2")
        sb   = request.form.get("Super Bowl")

        # this is number entry form accepting integer for 'tie break'
        sbtb = request.form.get("Tie Break")

        # insert into db users picks & tie break
        result = db.execute("INSERT INTO picks (userid, pick_1, pick_2, pick_3, pick_4, pick_5, pick_6, pick_7, pick_8, pick_9, pick_10, pick_11, sb_tie_break) \
            VALUES (:session, :pick_1, :pick_2, :pick_3, :pick_4, :pick_5, :pick_6, :pick_7, :pick_8, :pick_9, :pick_10, :pick_11, :sb_tie_break)", \
            session=session["userid"], pick_1=w1g1, pick_2=w1g2, pick_3=w1g3, pick_4=w1g4, pick_5=w2g1, pick_6=w2g2, pick_7=w2g3, pick_8=w2g4, pick_9=w3g1, pick_10=w3g2, pick_11=sb, sb_tie_break=sbtb)

        # changed to index from display below just to be able to load for now
        return redirect(url_for("index"))

    else:
        all_games_wc = db.execute("SELECT * FROM games WHERE gameid < 5")
        all_games_div = db.execute("SELECT * FROM games WHERE gameid > 4 AND gameid < 9")
        all_games_conf = db.execute("SELECT * FROM games WHERE gameid = 9 OR gameid = 10")
        all_games_sb = db.execute("SELECT * FROM games WHERE gameid = 11")


        # controls which / how many picks are displayed
        if make_visible() == 0:
            return render_template("make_picks_wc.html", all_games_wc=all_games_wc)
        if make_visible() == 1:
            return render_template("make_picks_div.html", all_games_div=all_games_div)
        if make_visible() == 2:
            return render_template("make_picks_conf.html", all_games_conf=all_games_conf)
        if make_visible() == 3:
            return render_template("make_picks_sb.html", all_games_sb=all_games_sb)
        # once superbowl picks are in (level 4) - it's locked.  can't make any more picks, hence apology.html
        if make_visible() == 4:
            return render_template("apology.html")


# Admin - set results routine
# eventually the *_score variables below will be updated via api from nfl.com - i hope at least
@app.route("/results", methods=["GET", "POST"])
@login_required
def results():
    if request.method == "POST":

        # gets results from admin screen inputs
        gameid      = request.form.get("gameid")
        fav_team    = request.form.get("fav_team")
        fav_score   = request.form.get("fav_score")
        dog_team    = request.form.get("dog_team")
        dog_score   = request.form.get("dog_score")
        result = db.execute("INSERT INTO results (gameid, fav_team, fav_score, dog_team, dog_score) \
            VALUES (:gameid, :fav_team, :fav_score, :dog_team, :dog_score)", \
            gameid=gameid, fav_team=fav_team, fav_score=fav_score, dog_team=dog_team, dog_score=dog_score)

        # changed this to redirect back to this screen
        # as if you are entering in results you are likely doing more than 1
        return redirect(url_for("results"))

    else:
        # checks that you are in fact an admin first
        user = session['userid']
        chk_user = db.execute("SELECT IsAdmin FROM users WHERE userid = :user", user=user)
        if chk_user[0]['IsAdmin'] == "N":
            return render_template("apology.html")

        return render_template("results.html")

# Admin - create games to be picked routine
@app.route("/games", methods=["GET", "POST"])
#@login_required
def games():
    if request.method == "POST":

        # gets picks from radio button options in make_picks
        gameid      = request.form.get("gameid")
        fav         = request.form.get("fav")
        dog         = request.form.get("dog")
        line        = request.form.get("line")

        result = db.execute("INSERT INTO games (gameid, fav_team, dog_team, line) \
            VALUES (:gameid, :fav_team, :dog_team, :line)", gameid=gameid, fav_team=fav, dog_team=dog, line=line)

        # changed to index from display below just to be able to load for now
        return render_template("games.html")

    else:
        # checks that you are in fact an admin first
        user = session['userid']
        chk_user = db.execute("SELECT IsAdmin FROM users WHERE userid = :user", user=user)
        if chk_user[0]['IsAdmin'] == "N":
            return render_template("apology.html")

        return render_template("games.html")

@app.route("/daily_box", methods=["GET", "POST"])
def daily_box():
    message = "Coming Soon!"

    return render_template("daily_box.html", message=message)

# REGISTER new user
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # ensure password was confirmed
        elif not request.form.get("password_confirm"):
            return apology("must confirm password")

        # ensure email was submitted
        elif not request.form.get("email"):
            return apology("must enter email")

        # encrypt password
        if request.form.get("password") == request.form.get("password_confirm"):
            hash = pwd_context.hash(request.form.get("password"))
        else:
            return apology("password confirmation does not match")

        print("got here insert user")
        #insert username & hash into table
        result = db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", username=request.form.get("username"), password=hash)
        if not result:
            print("got here insert user 2")
            return apology("Username already exists")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # this is to initialize the user in the WINS table, with 0
        # this made it easier to continually update win totals as opposed to insert OR update
        wins = 0
        uid = rows[0]["userid"]
        wins_update = db.execute("INSERT INTO wins (userid, wins) VALUES (:uid, :wins)", uid=uid, wins=wins)

        # remember which user has logged in
        session["userid"] = rows[0]["userid"]

        # redirect user to home page
        return redirect(url_for("index"))

    else:
        return render_template("register.html")
    
if __name__ == "__main__":
    make_ssl_devcert('/home/pi/pickem/dheslin', host='www.bygtech.com')
    #run_simple('0.0.0.0', 5000, app, ssl_context=('/home/pi/pickem/dheslin/ssl.cert', '/home/pi/pickem/dheslin/ssl.key'))
