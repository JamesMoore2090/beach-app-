from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app import db, mail
from app.auth import auth_bp
from app.models import User
from flask_mail import Message


def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=False)
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = get_serializer().dumps(user.email, salt='password-reset')
            reset_url = url_for('auth.reset_confirm', token=token, _external=True)
            msg = Message('Password Reset', recipients=[user.email])
            msg.body = f'Click to reset your password: {reset_url}'
            mail.send(msg)
        flash('If that email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_confirm(token):
    try:
        expiry = current_app.config['PASSWORD_RESET_EXPIRY']
        email = get_serializer().loads(token, salt='password-reset', max_age=expiry)
    except (SignatureExpired, BadSignature):
        flash('Reset link is invalid or expired.', 'danger')
        return redirect(url_for('auth.reset_request'))

    if request.method == 'POST':
        password = request.form.get('password')
        if not password or len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/reset_confirm.html', token=token)
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash('Password updated. Please log in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_confirm.html', token=token)


@auth_bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        birthday = request.form.get('birthday')
        role = request.form.get('role', 'user')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/add_user.html')
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        if birthday:
            from datetime import date
            user.birthday = date.fromisoformat(birthday)
        db.session.add(user)
        db.session.commit()
        flash(f'User {name} created.', 'success')
        return redirect(url_for('auth.add_user'))
    return render_template('auth/add_user.html')
