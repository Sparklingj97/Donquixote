from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, request, session, make_response
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

##
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:woojin@localhost/flask' # 'mySQL://id:pw@localhost/flask'
app.config['SECRET_KEY'] = 'asldjalksjdklasd'
admin = Admin(app)
db = SQLAlchemy(app)

##
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(db.Model):
    """
    from app import db
    db.create_all()
    """
    __tablename__ = "user"

    idx = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    email = db.Column(db.String(20), unique=True)
    passwd = db.Column(db.String(20))
    created = db.Column(db.DateTime, default=datetime.now)
    # no __init__()

class Comment(db.Model):
    __tablename__ = "comment"

    idx = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    who = db.Column(db.Integer, db.ForeignKey('user.idx'))
    created = db.Column(db.DateTime, default=datetime.now)

class Post(db.Model):
    __tablename__ = "post"

    idx = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())
    who = db.Column(db.Integer, db.ForeignKey('user.idx'))
    created = db.Column(db.DateTime, default=datetime.now)
    image = db.Column(db.String())
    video = db.Column(db.String())
    chang = db.Column(db.Integer)
    category = db.Column(db.String(20))

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(Post, db.session))

# 로그인 되있으면 메인, 아니면 로그인창
@app.route("/")
def hello():
    return login()

@app.route("/main")
def main():
    return render_template("index.html")

def login():
    username = request.cookies.get('username', None)
    useremail = request.cookies.get('useremail', None)
    if username and useremail:
        found = User.query.filter(
        User.name == username,
        User.email == useremail,
        ).first()
        if found:
            return render_template(
                "index.html"
            )
    return render_template(
        "login.html"
    )
#로그인 후 제출
@app.route("/success", methods=["POST"])
def success():
    username = request.form['email']
    passwd = request.form['password']
    autologin = request.form.get('autoLogin', 'off')
    return search(username, passwd, autologin)

# 유저 검색 예제
def search(email, pw, autologin, is_web=True):
    found = User.query.filter(
        User.email == email,
        User.passwd == pw,
    ).first()
    if found:
        if is_web:
            resp = make_response(render_template(
                "index.html"
            ))
            resp.set_cookie("username", found.name)
            resp.set_cookie("useremail", found.email)

            if autologin == "on":
                expire_date = datetime.now()
                expire_date = expire_date + timedelta(days=90)
                resp.set_cookie("username", expires=expire_date)
                resp.set_cookie("useremail", expires=expire_date)
                return resp
            else:
                return resp
        else:
            return found
    if is_web:
        return 'failed'
    else:
        return None

@app.route("/logout")
def logout():
    resp = make_response(render_template(
        "login.html"
    ))
    resp.set_cookie("username", expires=datetime.now())
    resp.set_cookie("useremail", expires=datetime.now())
    return resp

# 회원탈퇴 예제
@app.route("/delete/<name>/<email>/<pw>")
def delete(name, email, pw):
    found = search(name, email, pw, is_web=False)
    db.session.delete(found)
    db.session.commit()
    return 'deleted!'

@app.route("/register")
def register():
    return render_template("register.html")

# 회원가입 제출
@app.route("/register_check")
def register_success():
    name = request.form['name']
    email = request.form['email']
    passwd = request.form['passwd']
    ver_passwd = request.form['ver_passwd']
    if passwd == ver_passwd and name != "" and email != "" and passwd != "" and ver_passwd != "":
        return create(name, email, passwd)
    else:
        return register()

# 유저 생성 예제
def create(name, email, passwd):
    new = User()
    new.name = name
    new.email = email
    new.passwd = passwd
    db.session.add(new)
    db.session.commit()
    return login()


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)