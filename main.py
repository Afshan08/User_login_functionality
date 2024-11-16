from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
name = ''

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = './static/files'
db = SQLAlchemy(app)

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(252))
    password = db.Column(db.String(100))
    name = db.Column(db.String(110), unique=True)
#Line below only required once, when creating DB. 
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    global name
    if request.method == 'POST':

        if User.query.filter_by(name=request.form.get('email')).first():
            #User is already logged in
            flash("You have already signed up with this user name in. log in instead ")
            return redirect(url_for('login'))

        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        final_password = generate_password_hash(password, 'pbkdf2', salt_length=8)
        entry = User( email=email,
                      password=final_password,
                      name=name)
        db.session.add(entry)
        db.session.commit()
        load_user(entry)
        print(final_password)
        return redirect(url_for(f'secrets', name=name))
    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        user = User.query.filter_by(name=name).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('secrets'))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
def download():
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        'cheat_sheet.pdf',
        as_attachment=False
    )



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


