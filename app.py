from datetime import datetime, timedelta

from flask import (
    Flask,
    render_template,
    request,
    make_response,
)
from db import (
    db,
    migrate,
)
from models.user import User
from admin import admin

app = Flask(__name__)
app.config.from_pyfile("configs.py")


admin.init_app(app)


db.init_app(app)



##
db.init_app(app)
migrate.init_app(app, db)


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