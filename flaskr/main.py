# flaskr/main.py
from flask import (
    Blueprint, g, render_template, request, redirect, url_for, flash, session
)
from flask_login import current_user, login_required
from flaskr.db import get_db
from .utils import get_scenario
bp = Blueprint('main', __name__)


@bp.route("/")
@bp.route("/mypage")
@login_required
def mypage():
    scenario = get_scenario(current_user)

    return render_template('mypage.html', user=current_user, scenario=scenario)    


