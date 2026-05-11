#user.py
import secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .db import get_db

bp = Blueprint('user', __name__, url_prefix='/user')

#ユーザープロフィール編集機能
@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    db = get_db()
    if request.method == 'POST':

        new_username = request.form['username']
        new_user_id = request.form['user_id']
        new_hobby = request.form['hobby']
        new_favorite_food = request.form['favorite_food']

        error_username = []
        error_user_id = []
        error_hobby = []
        error_favorite_food = []

        #ユーザーIDが使用可能文字か確認（英数字及び‐_が使用できます）
        if  new_user_id and not all((c.isalnum() and c.isascii()) or c in '-_' for c in new_user_id):
            error_user_id.append("ユーザーIDには英数字及び- _のみ使用できます。")

        #ユーザーIDが20字以内であるか確認
        if new_user_id and len(new_user_id) > 20:
            error_user_id.append("ユーザーIDは20字以内である必要があります。")
        
        #使用済みユーザーidでないか確認(空欄の場合はメールアドレスの@より前の部分をユーザーidとするため、空欄はエラーにはしない)
        if new_user_id and db.execute('SELECT id FROM users WHERE user_id = ? AND id != ?', (new_user_id, current_user.id)).fetchone():
            error_user_id.append(f"ユーザーID {new_user_id} はすでに登録されています。")
     
        #ユーザーIDが空欄の場合はランダムなユーザーIDを生成する
        if not new_user_id:
            while True:
                new_id = secrets.token_urlsafe(15)[:20]  # 20文字以内のランダムなユーザーIDを生成
                if not db.execute('SELECT user_id FROM users WHERE user_id = ?', (new_id,)).fetchone():
                    new_user_id = new_id
                    break

        #趣味と好きな食べ物は空欄またはスペースの場合は「なし」とする
        if not new_hobby or new_hobby.strip() == "":
            new_hobby = "なし"
        if not new_favorite_food or new_favorite_food.strip() == "":
            new_favorite_food = "なし"

        #ユーザーネームが50字以内であるか確認
        if len(new_username) > 50:
            error_username.append("ユーザーネームは50字以内である必要があります。")

        #趣味が100字以内であるか確認
        if new_hobby and len(new_hobby) > 100:
            error_hobby.append("趣味は100字以内である必要があります。")
        
        #趣味がちゃんと趣味であるか確認(後ほど実装予定)
        
        #好きな食べ物が100字以内であるか確認
        if new_favorite_food and len(new_favorite_food) > 100:
            error_favorite_food.append("好きな食べ物は100字以内である必要があります。")

        #好きな食べ物がちゃんと食べ物であるか確認(後ほど実装予定)

        if not any([error_username, error_user_id, error_hobby, error_favorite_food]):
             # データベースを更新
            db.execute('UPDATE users SET user_id = ?, hobby = ?, favorite_food = ?, username = ? WHERE id = ?',
                    (new_user_id, new_hobby, new_favorite_food, new_username, current_user.id))
            db.commit()

            return redirect(url_for('main.mypage'))
            
           
       
        else:
            return render_template('edit.html', new_user_id=new_user_id, new_username=new_username, new_hobby=new_hobby, new_favorite_food=new_favorite_food, error_username=error_username, error_user_id=error_user_id, error_hobby=error_hobby, error_favorite_food=error_favorite_food) 
    else:
        return render_template('edit.html', user=current_user, new_user_id=None, new_username=None, new_hobby=None, new_favorite_food=None, error_username=[], error_user_id=[], error_hobby=[], error_favorite_food=[])

