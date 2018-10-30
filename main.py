from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzrus2018@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "mGFSD45%$#$hYYeDSF"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id')) #need to place in __init__ because there's no variable = 2 'True'

    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password): #need to add username for signup function to take in the parameter
        self.username = username
        self.password = password

@app.before_request
def before_request():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
    
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users, title='Blog Users')

@app.route('/blog')
def blog():
    posts = Blog.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    
    if user_id:
        posts = Blog.query.filter_by(author_id=user_id)
        return render_template('user.html', posts=posts, title="User Posts")
    if blog_id:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post )

    return render_template('blog.html', posts=posts, title='All Blog Posts')

@app.route('/newpost', methods=['GET', 'POST'])
def new_post(): 
    author = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        title_error = ''
        body_error = ''

        if not blog_title:
            title_error = "[Field Required]"
        if not blog_body:
            body_error = "[Field Required]"

        if not body_error and not title_error:
            submit = Blog(blog_title, blog_body, author)     
            db.session.add(submit)
            db.session.commit()        
            return redirect('/blog?id={}'.format(submit.id)) 
        else:
            return render_template('newpost.html', title='New Blog Entry', title_error=title_error, 
                body_error=body_error, blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Blog Entry')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()      
        if user and user.password == password:                      
            session['username'] = username
            flash('Login Successful')
            return redirect('/newpost')
        else:
            flash('Invalid username or password')
    
    return render_template('login.html', title='Login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if password != verify:
            flash('Password does not match', "error")
        elif len(username) < 3 or len(password) < 3:
            flash('Username and password must be more than 3 characters', 'error')
        elif existing_user:
            flash('User already exists', 'error')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html', title='Signup')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog') 

if  __name__ == "__main__":
    app.run()