import os
from datetime import date
from flask import render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.main import main_bp
from app.models import BeachWeek, DinnerRSVP, MenuItem, BlogPost, Picture

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.context_processor
def inject_beach_weeks():
    beach_weeks = BeachWeek.query.order_by(BeachWeek.year.desc()).all()
    return dict(beach_weeks=beach_weeks)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    # Find current or upcoming beach week
    current_week = BeachWeek.query.filter(
        BeachWeek.start_date <= today, BeachWeek.end_date >= today
    ).first()
    next_week = BeachWeek.query.filter(BeachWeek.start_date > today)\
        .order_by(BeachWeek.start_date).first()
    blog_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(10).all()
    return render_template('main/dashboard.html',
                           current_week=current_week, next_week=next_week,
                           today=today, blog_posts=blog_posts)


@main_bp.route('/year/<int:year>/rooms')
@login_required
def room_assignments(year):
    bw = BeachWeek.query.filter_by(year=year).first_or_404()
    return render_template('main/rooms.html', beach_week=bw)


@main_bp.route('/year/<int:year>/menu')
@login_required
def menu(year):
    bw = BeachWeek.query.filter_by(year=year).first_or_404()
    days = sorted(set(item.day for item in bw.menu_items))
    user_rsvps = {r.menu_item_id: r for r in
                  DinnerRSVP.query.filter_by(user_id=current_user.id).all()}
    return render_template('main/menu.html', beach_week=bw, days=days, user_rsvps=user_rsvps)


@main_bp.route('/rsvp/<int:item_id>', methods=['POST'])
@login_required
def toggle_rsvp(item_id):
    item = db.session.get(MenuItem, item_id)
    if not item:
        abort(404)
    if item.meal_type != 'dinner':
        flash('RSVP is only available for dinner.', 'warning')
        return redirect(url_for('main.menu', year=item.beach_week.year))

    rsvp = DinnerRSVP.query.filter_by(menu_item_id=item_id, user_id=current_user.id).first()
    if rsvp:
        new_status = 'not_here' if rsvp.status == 'attending' else 'attending'
        rsvp.status = new_status
    else:
        rsvp = DinnerRSVP(menu_item_id=item_id, user_id=current_user.id, status='not_here')
        db.session.add(rsvp)
    db.session.commit()
    return redirect(url_for('main.menu', year=item.beach_week.year))


@main_bp.route('/year/<int:year>/chores')
@login_required
def chores(year):
    bw = BeachWeek.query.filter_by(year=year).first_or_404()
    return render_template('main/chores.html', beach_week=bw)


@main_bp.route('/year/<int:year>/pictures')
@login_required
def pictures(year):
    bw = BeachWeek.query.filter_by(year=year).first_or_404()
    return render_template('main/pictures.html', beach_week=bw)


@main_bp.route('/year/<int:year>/pictures/upload', methods=['POST'])
@login_required
def upload_picture(year):
    bw = BeachWeek.query.filter_by(year=year).first_or_404()
    file = request.files.get('photo')
    if not file or not allowed_file(file.filename):
        flash('Please upload a valid image file.', 'danger')
        return redirect(url_for('main.pictures', year=year))

    filename = secure_filename(file.filename)
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(year))
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))

    pic = Picture(
        beach_week_id=bw.id,
        uploaded_by=current_user.id,
        file_path=f'{year}/{filename}',
        caption=request.form.get('caption', ''),
    )
    db.session.add(pic)
    db.session.commit()
    flash('Picture uploaded!', 'success')
    return redirect(url_for('main.pictures', year=year))


@main_bp.route('/blog')
@login_required
def blog_list():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('main/blog_list.html', posts=posts)


@main_bp.route('/blog/new', methods=['GET', 'POST'])
@login_required
def blog_new():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        beach_week_id = request.form.get('beach_week_id') or None
        post = BlogPost(title=title, content=content,
                        author_id=current_user.id, beach_week_id=beach_week_id)
        db.session.add(post)
        db.session.flush()

        # Handle attached pictures
        files = request.files.getlist('photos')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'blog')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                pic = Picture(
                    beach_week_id=int(beach_week_id) if beach_week_id else None,
                    uploaded_by=current_user.id,
                    file_path=f'blog/{filename}',
                )
                db.session.add(pic)
                db.session.flush()
                post.pictures.append(pic)

        db.session.commit()
        flash('Post created!', 'success')
        return redirect(url_for('main.blog_list'))
    beach_weeks = BeachWeek.query.order_by(BeachWeek.year.desc()).all()
    return render_template('main/blog_new.html', beach_weeks_list=beach_weeks)


@main_bp.route('/blog/<int:post_id>')
@login_required
def blog_detail(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('main/blog_detail.html', post=post)
