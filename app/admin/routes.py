from functools import wraps
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_mail import Message
from app import db, mail
from app.admin import admin_bp
from app.models import User, BeachWeek, RoomAssignment, MenuItem, Chore


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_required
def admin_home():
    beach_weeks = BeachWeek.query.order_by(BeachWeek.year.desc()).all()
    users = User.query.order_by(User.name).all()
    return render_template('admin/home.html', admin_beach_weeks=beach_weeks, users=users)


# --- Beach Week ---

@admin_bp.route('/beach-week/add', methods=['GET', 'POST'])
@admin_required
def add_beach_week():
    if request.method == 'POST':
        from datetime import date
        year = int(request.form['year'])
        start = date.fromisoformat(request.form['start_date'])
        end = date.fromisoformat(request.form['end_date'])
        if BeachWeek.query.filter_by(year=year).first():
            flash(f'Beach week for {year} already exists.', 'danger')
            return render_template('admin/beach_week_form.html')
        bw = BeachWeek(year=year, start_date=start, end_date=end)
        db.session.add(bw)
        db.session.commit()
        flash(f'Beach week {year} created!', 'success')
        return redirect(url_for('admin.admin_home'))
    return render_template('admin/beach_week_form.html')


@admin_bp.route('/beach-week/<int:year>/edit', methods=['GET', 'POST'])
@admin_required
def edit_beach_week(year):
    bw = BeachWeek.query.filter_by(year=year).first_or_404()
    if request.method == 'POST':
        from datetime import date
        bw.start_date = date.fromisoformat(request.form['start_date'])
        bw.end_date = date.fromisoformat(request.form['end_date'])
        db.session.commit()
        flash(f'Beach week {year} updated.', 'success')
        return redirect(url_for('admin.admin_home'))
    return render_template('admin/beach_week_form.html', beach_week=bw)


# --- Room Assignments ---

@admin_bp.route('/beach-week/<int:year>/rooms', methods=['GET', 'POST'])
@admin_required
def edit_rooms(year):
    bw = BeachWeek.query.filter_by(year=year).first_or_404()
    users = User.query.order_by(User.name).all()
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        user_ids = request.form.getlist('user_ids')
        if room_name and user_ids:
            for uid in user_ids:
                ra = RoomAssignment(beach_week_id=bw.id, room_name=room_name, user_id=int(uid))
                db.session.add(ra)
            db.session.commit()
            flash('Room assignment added.', 'success')
        return redirect(url_for('admin.edit_rooms', year=year))
    return render_template('admin/rooms.html', beach_week=bw, users=users)


@admin_bp.route('/room-assignment/<int:ra_id>/delete', methods=['POST'])
@admin_required
def delete_room(ra_id):
    ra = db.session.get(RoomAssignment, ra_id)
    if ra:
        year = ra.beach_week.year
        db.session.delete(ra)
        db.session.commit()
        flash('Room assignment removed.', 'success')
        return redirect(url_for('admin.edit_rooms', year=year))
    flash('Not found.', 'danger')
    return redirect(url_for('admin.admin_home'))


# --- Menu ---

@admin_bp.route('/beach-week/<int:year>/menu', methods=['GET', 'POST'])
@admin_required
def edit_menu(year):
    bw = BeachWeek.query.filter_by(year=year).first_or_404()
    users = User.query.order_by(User.name).all()
    if request.method == 'POST':
        from datetime import date
        day = date.fromisoformat(request.form['day'])
        meal_type = request.form['meal_type']
        description = request.form['description']
        user_ids = request.form.getlist('assigned_users')
        item = MenuItem(beach_week_id=bw.id, day=day, meal_type=meal_type, description=description)
        for uid in user_ids:
            user = db.session.get(User, int(uid))
            if user:
                item.assigned_users.append(user)
        db.session.add(item)
        db.session.commit()
        flash('Menu item added.', 'success')
        return redirect(url_for('admin.edit_menu', year=year))
    days = sorted(set(item.day for item in bw.menu_items))
    return render_template('admin/menu.html', beach_week=bw, days=days, users=users)


@admin_bp.route('/menu-item/<int:item_id>/delete', methods=['POST'])
@admin_required
def delete_menu_item(item_id):
    item = db.session.get(MenuItem, item_id)
    if item:
        year = item.beach_week.year
        db.session.delete(item)
        db.session.commit()
        flash('Menu item removed.', 'success')
        return redirect(url_for('admin.edit_menu', year=year))
    flash('Not found.', 'danger')
    return redirect(url_for('admin.admin_home'))


# --- Chores ---

@admin_bp.route('/beach-week/<int:year>/chores', methods=['GET', 'POST'])
@admin_required
def edit_chores(year):
    bw = BeachWeek.query.filter_by(year=year).first_or_404()
    users = User.query.order_by(User.name).all()
    if request.method == 'POST':
        from datetime import date
        description = request.form['description']
        user_ids = request.form.getlist('assigned_users')
        day = request.form.get('day') or None
        chore = Chore(
            beach_week_id=bw.id,
            description=description,
            day=date.fromisoformat(day) if day else None,
        )
        for uid in user_ids:
            user = db.session.get(User, int(uid))
            if user:
                chore.assigned_users.append(user)
        db.session.add(chore)
        db.session.commit()
        flash('Chore added.', 'success')
        return redirect(url_for('admin.edit_chores', year=year))
    return render_template('admin/chores.html', beach_week=bw, users=users)


@admin_bp.route('/chore/<int:chore_id>/delete', methods=['POST'])
@admin_required
def delete_chore(chore_id):
    chore = db.session.get(Chore, chore_id)
    if chore:
        year = chore.beach_week.year
        db.session.delete(chore)
        db.session.commit()
        flash('Chore removed.', 'success')
        return redirect(url_for('admin.edit_chores', year=year))
    flash('Not found.', 'danger')
    return redirect(url_for('admin.admin_home'))


# --- Users ---

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.admin_home'))
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        user.role = request.form.get('role', user.role)
        birthday = request.form.get('birthday')
        if birthday:
            from datetime import date
            user.birthday = date.fromisoformat(birthday)
        else:
            user.birthday = None
        password = request.form.get('password')
        if password:
            user.set_password(password)
        db.session.commit()
        flash(f'User {user.name} updated.', 'success')
        return redirect(url_for('admin.admin_home'))
    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.admin_home'))
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('admin.admin_home'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} deleted.', 'success')
    return redirect(url_for('admin.admin_home'))


# --- Email ---

@admin_bp.route('/email', methods=['GET', 'POST'])
@admin_required
def send_email():
    if request.method == 'POST':
        subject = request.form.get('subject')
        body = request.form.get('body')
        users = User.query.all()
        recipients = [u.email for u in users]
        if recipients:
            msg = Message(subject=subject, recipients=recipients, body=body)
            mail.send(msg)
            flash(f'Email sent to {len(recipients)} users.', 'success')
        else:
            flash('No users to email.', 'warning')
        return redirect(url_for('admin.send_email'))
    return render_template('admin/email.html')
