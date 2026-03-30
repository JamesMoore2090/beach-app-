from flask import render_template
from flask_login import login_required
from app.main import main_bp


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html')
