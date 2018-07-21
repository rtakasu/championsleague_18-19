from flask import render_template
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))

#     user = User.query.filter_by(username=form.username.data).first()
#     if user is None or not user.check_password(form.password.data):
#         flash('Invalid username or password')
#         return redirect(url_for('login'))
#     login_user(user, remember=form.remember_me.data)
#     return redirect(url_for('index'))
    # return render_template('login.html', title='Sign In', form=form)