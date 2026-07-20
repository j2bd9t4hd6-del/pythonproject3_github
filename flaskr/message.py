#message.py
#このファイルは、メッセージの送受信に関連する機能を提供します。
from flask import Blueprint, request, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from .db import get_db
from datetime import datetime, timedelta
import random
bp = Blueprint('message', __name__, url_prefix='/message')

def get_scheduled_time():
    # 現在の時刻を取得
    now = datetime.now()
    target_day = now + timedelta(days=2)
    #午前9時から午後5時の間に設定する
    target_minute  = random.randint( 9 * 60, 17 * 60 )
    scheduled_time = target_day.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=target_minute)
    return scheduled_time.strftime('%Y-%m-%d %H:%M:%S')

@bp.route('/send', methods=['POST', 'GET'])
@login_required
def send_message():
    if request.method == 'POST':


        db = get_db()
        sender_address = request.form.get('sender_address')
        recipient_address = request.form.get('recipient_address')
        sender_name = request.form.get('sender_name')
        recipient_name = request.form.get('recipient_name')
        body = request.form.get('body')
        #sender_address, sender_name, recipient_name, bodyが空の時はそのまま送信する（空のままDBに保存される）

        #recipient_addressが空の場合は何もしない
        if not recipient_address:
            return render_template('send_message.html', error="Recipient address is required.")
        else:
            #recipient_addressがDBに存在するか確認(存在しなければ何もしない)
            user = db.execute('SELECT * FROM users WHERE address = ?', (recipient_address,)).fetchone()
            if user is None:
                return render_template('send_message.html', error="Recipient address does not exist.")
            
        # メッセージ郵送ロジックをここに実装
        scheduled_time = get_scheduled_time()
        db.execute("""INSERT INTO messages
                    (body, sender_address, sender_name, recipient_address, recipient_name, scheduled_at)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (body, sender_address, sender_name, recipient_address, recipient_name, scheduled_time)
                    )
        db.commit()
        return render_template('send_message.html', success="Message sent successfully!")
    else:
        return render_template('send_message.html')

#未読のメッセージを取得して表示するためのルート
#表示される手紙は、投函予定時刻をすぎてからのものとする
@bp.route('/inbox')
@login_required
def inbox():
    db = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_address = current_user.address
    messages = db.execute('SELECT * FROM messages WHERE recipient_address = ? AND is_delivered = 0 AND scheduled_at <= ? ORDER BY id ASC', (user_address, now)).fetchall()
    return render_template('inbox.html', messages=messages)

#メッセージを既読にするためのルート
@bp.route('/mark_as_read', methods=['POST'])
@login_required
def mark_as_read():
    db = get_db()
    db.execute('UPDATE messages SET is_delivered = 1, receiving_timestamp = CURRENT_TIMESTAMP WHERE recipient_address = ? AND is_delivered = 0', (current_user.address,))
    db.commit()
    return redirect(url_for('message.inbox'))

#保管したメッセージを表示するためのルート
@bp.route('/archive')
@login_required
def archive():
    db = get_db()
    user_address = current_user.address
    messages = db.execute('SELECT * FROM messages WHERE recipient_address = ? AND is_delivered = 1 ORDER BY id ASC', (user_address,)).fetchall()
    return render_template('archive.html', messages=messages)

#保管した手紙を捨てるためのルート
@bp.route('/delete_message', methods=['POST'])
@login_required
def delete_message():
    db = get_db()
    message_id = request.form.get('message_id')
    db.execute('DELETE FROM messages WHERE id = ? AND recipient_address = ?', (message_id, current_user.address))
    db.commit()
    return redirect(url_for('message.archive'))