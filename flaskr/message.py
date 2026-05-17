#message.py
#このファイルは、メッセージの送信に関連する機能を提供します。
from flask import Blueprint, request, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from .db import get_db
bp = Blueprint('message', __name__, url_prefix='/message')

@bp.route('/send', methods=['POST', 'GET'])
@login_required
def send_message():
    if request.method == 'POST':


        db = get_db()
        sender_address = current_user.address
        recipient_address = request.form.get('recipient_address')
        body = request.form.get('body')
        # メッセージ送信ロジックをここに実装
        db.execute("""INSERT INTO messages
                    (body, sender_address, recipient_address)
                    VALUES (?, ?, ?)""",
                    (body, sender_address, recipient_address)
                    )
        db.commit()
        return 'Message sent successfully'
    else:
        return render_template('send_message.html')

@bp.route('/inbox')
@login_required
def inbox():
    db = get_db()
    user_address = current_user.address
    messages = db.execute('SELECT * FROM messages WHERE recipient_address = ? AND is_delivered = 0 ORDER BY id ASC', (user_address,)).fetchall()
    return render_template('inbox.html', messages=messages)