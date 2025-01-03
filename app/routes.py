from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response
from .database import User, Transaction, MLTask , db 
from .utils import summarize_text
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import RegistrationForm, LoginForm, RechargeForm


main_page = Blueprint('main_page', __name__,template_folder="static")

@main_page.route('/')
def index():
    return render_template('index.html')


# Route for registration
@main_page.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password_hash= generate_password_hash(form.password.data ))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main_page.recharge'))
    return render_template('register.html', form=form)

# Route for login
@main_page.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash ,form.password.data):
            login_user(user)
            return redirect(url_for('main_page.recharge'))
    return render_template('login.html', form=form)

# Route for recharge
@main_page.route('/recharge', methods=['GET', 'POST'])
def recharge():
    form = RechargeForm()
    if form.validate_on_submit():
        print(f"This is current_user on recharge: {current_user}")
        current_user.balance += form.amount.data
        db.session.commit()
        return redirect(url_for('main_page.submit_task'))
    return render_template('recharge.html', form=form)

@main_page.route('/submit_task', methods=['GET', 'POST'])
@login_required 
def submit_task():

    print('Hit submit route!')
    if request.method == 'POST':
        prompt = request.form['text_to_summarize']
        ngrokUrl = request.form['ngrok_url']
        print(f"Received prompt: {prompt}")
        print(f"Received ngrokUrl: {ngrokUrl}")
        
        if current_user.balance > 0:
             # Summarize the text
            summary = summarize_text(prompt, ngrokUrl)
            print('Recieved Summary {summary}')
            # Save the task in the database
            task = MLTask(user_id=current_user.id, prompt=prompt, result=summary)
            db.session.add(task)
            print(f"Balance before deduction: {current_user.balance}")
            current_user.balance -= 10
            print(f"Balance after deduction: {current_user.balance}")
            db.session.commit()
            return render_template('submit_task.html', summary=summary, prompt=prompt, ngrokUrl=ngrokUrl)

        else:
            error = "Insufficient Balance."
            return render_template('submit_task.html', error=error, prompt=prompt, ngrokUrl=ngrokUrl)

    return render_template('submit_task.html')

@main_page.route('/admin/view_users')
def view_users():
    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "balance": user.balance} for user in users]
    return jsonify(user_list)
