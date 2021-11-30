from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user, current_user, LoginManager, UserMixin

app = Flask(__name__)

app.config['SECRET_KEY'] = 'SECRET KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'POSTGRES URI AND PASSWORD'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Diarypost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
    privacy_level = db.Column(db.Integer)
    editor = db.Column(db.String(30))
    location = db.Column(db.String(30))
    uid = db.Column(db.Integer)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

@app.route('/login')
def login():
    return render_template('login2.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('login'))

    login_user(user, remember=remember)
    return redirect(url_for('journal'))

@app.route('/signup')
def signup():
    return render_template('signup2.html')

@app.route('/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists')
        return redirect(url_for('signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/journal')
def journal():
    posts = Diarypost.query.filter_by(privacy_level = 1).order_by(Diarypost.date_posted.desc()).all()

    return render_template('journal.html', posts=posts)

@app.route('/chron/<int:month><int:year>')
def spec_chron():
    posts = Diarypost.query.order_by(Diarypost.date_posted.desc()).all()

    return render_template('journal.html', posts=posts)

@app.route('/location')
def location():
    posts = Diarypost.query.filter_by(privacy_level=1).order_by(Diarypost.location).all()

    return render_template('journal.html', posts=posts)

@app.route('/loc/<string:loc>')
def spec_location(loc):
    posts = Diarypost.query.filter_by(location=loc, privacy_level=1).order_by(Diarypost.location).all()

    return render_template('journal.html', posts=posts)

@app.route('/myposts')
def about():
    posts = Diarypost.query.filter_by(uid = current_user.id).order_by(Diarypost.date_posted.desc()).all()

    return render_template('myposts.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Diarypost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)

@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/addpost', methods=['POST'])
def addpost():
    title = request.form['title']
    author = request.form['author']
    privacy = request.form['privacy']
    privacy_level=0
    if privacy == 'private':
        privacy_level = 0
    if privacy == 'public':
        privacy_level = 1
    editor = request.form['editor']
    location = request.form['location']
    content = request.form['content']
    uid = current_user.id
    post = Diarypost(title=title, author=author, privacy_level=privacy_level, editor=editor, location=location, content=content, date_posted=datetime.now(), uid=uid)

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('journal'))


if __name__ == '__main__':
    app.run(debug=True)