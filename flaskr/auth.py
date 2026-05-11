# auth.py
import secrets
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session, g
)
from flask_login import (current_user, login_required, LoginManager, login_user, logout_user)
from flaskr.db import get_db
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User
bp = Blueprint('auth', __name__, url_prefix='/auth')

# ログインしているユーザーの情報をリクエストごとにg.userに保存する
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()

#サインアップ
@bp.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    
    elif request.method == 'POST':
        #フォームに入力された値を取得
        user_id = request.form.get('user-id')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password-confirm')
        hobby = request.form.get('hobby')
        favorite_food = request.form.get('favorite-food')
        db = get_db()
        #エラーを格納するリストを用意
        error_email = []
        error_password = []
        error_password_confirm = []
        error_username = []
        error_user_id = []
        error_hobby = []
        error_favorite_food = []

        #必須の項目が入力されているか確認
        if not email:
            error_email.append("メールアドレスは必須項目です。")
        if not password:
            error_password.append("パスワードは必須項目です。")
        if not username:
            error_username.append("ユーザーネームは必須項目です。")
        if not password_confirm:
            error_password.append("パスワード（確認）は必須項目です。")

        #使用済みメールアドレスでないか確認
        if db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone():
            error_email.append(f"メールアドレス{email}はすでに登録されています。") 

        #ユーザーIDが使用可能文字か確認（英数字及び‐_が使用できます）
        if user_id and not all((c.isalnum() and c.isascii()) or c in '-_' for c in user_id):
            error_user_id.append("ユーザーIDには英数字及び- _のみ使用できます。")

        #ユーザーIDが20字以内であるか確認
        if user_id and len(user_id) > 20:
            error_user_id.append("ユーザーIDは20字以内である必要があります。")
        
        #使用済みユーザーidでないか確認(空欄の場合はメールアドレスの@より前の部分をユーザーidとするため、空欄はエラーにはしない)
        if user_id and db.execute('SELECT id FROM users WHERE user_id = ?', (user_id,)).fetchone():
            error_user_id.append(f"ユーザーID {user_id} はすでに登録されています。")
     
        #ユーザーIDが空欄の場合はランダムなユーザーIDを生成する
        if not user_id:
            while True:
                new_id = secrets.token_urlsafe(15)[:20]  # 20文字以内のランダムなユーザーIDを生成
                if not db.execute('SELECT user_id FROM users WHERE user_id = ?', (new_id,)).fetchone():
                    user_id = new_id
                    break
        #趣味と好きな食べ物は空欄またはスペースの場合は「なし」とする
        if not hobby or hobby.strip() == "":
            hobby = "なし"
        if not favorite_food or favorite_food.strip() == "":
            favorite_food = "なし"

        #パスワードが使用可能文字か確認(英数字及び!@#$%^&*_-が使用できます)
        if not all((c.isalnum() and c.isascii()) or c in '!@#$%^&*_-' for c in password):
            error_password.append("パスワードには英数字及び!@#$%^&*_-のみ使用できます。")

        #パスワードが8文字以上であるか確認
        if password and len(password) < 8:
            error_password.append("パスワードは8文字以上である必要があります。")

        #パスワードとパスワード（確認）が一致しているか確認
        if password != password_confirm:
            error_password.append("パスワードとパスワード（確認）が一致していません。")
            error_password_confirm.append("パスワードとパスワード（確認）が一致していません。")

        #ユーザーネームが50字以内であるか確認
        if len(username) > 50:
            error_username.append("ユーザーネームは50字以内である必要があります。")

        #趣味が100字以内であるか確認
        if hobby and len(hobby) > 100:
            error_hobby.append("趣味は100字以内である必要があります。")
        
        #趣味がちゃんと趣味であるか確認(後ほど実装予定)
        
        #好きな食べ物が100字以内であるか確認
        if favorite_food and len(favorite_food) > 100:
            error_favorite_food.append("好きな食べ物は100字以内である必要があります。")

        #好きな食べ物がちゃんと食べ物であるか確認(後ほど実装予定)

        #エラーがない場合はユーザーを新規登録してログインする
        if not any([error_email, error_password, error_username, error_user_id, error_hobby, error_favorite_food]):
            hashed_password = generate_password_hash(password)

            #データをインサートして新規登録する
            db.execute(
                """INSERT INTO users
                (email, user_id, password, username, hobby, favorite_food)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (email, user_id, hashed_password, username, hobby, favorite_food)
            )
            db.commit()

            #新規登録したユーザーをデータベースから取得
            user_row = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

            #新規登録したUSERオブジェクトを作成
            user_object = User(
                id=user_row['id'],
                email=user_row['email'],
                password=user_row['password'],
                username=user_row['username'],
                user_id=user_row['user_id'],
                hobby=user_row['hobby'],
                favorite_food=user_row['favorite_food']
            )

            #セッションを確立（login_userはflaskの関数）
            login_user(user_object)

            #クエリパラメータからURLを取得
            next_page = request.args.get('next')
            #クエリパラメータがあればそこへ、なければマイページへ転送
            return redirect(next_page or url_for('main.mypage'))
        
        else: #エラーがある場合はリダイレクトせずエラーを引数にしてHTMLで表示
            return render_template('signup.html', error_email=error_email, error_password=error_password, error_password_confirm=error_password_confirm, error_username=error_username, error_user_id=error_user_id, error_hobby=error_hobby, error_favorite_food=error_favorite_food, email=email, username=username, user_id=user_id, hobby=hobby, favorite_food=favorite_food)  


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':#ゲットリクエストならサイトを返す
        if current_user.is_authenticated:
            return redirect(url_for('main.mypage'))
        return render_template("signin.html")
    
    elif request.method == 'POST':#ポストリクエストならログイン実行
        
        user_id = request.form.get('user-id')
        password = request.form.get('password')
        hobby = request.form.get('hobby')
        favorite_food = request.form.get('favorite-food')

        db = get_db()
        error_user_id = []
        error_password = []
        error_favorite_food = []
        error_hobby = []


        #テーブルの中をユーザー検索
        user_row = db.execute(
        'SELECT * FROM users WHERE email = ? OR user_id = ?', 
        (user_id, user_id) # 両方のハテナに同じ入力値を入れる
        ).fetchone()

        #ユーザーが存在しないか、パスワードが正しくない場合はエラーを表示
        if not user_row or not check_password_hash(user_row['password'], password):
            error_user_id.append("ユーザーIDまたはパスワードが間違っています。")
            error_password.append("ユーザーIDまたはパスワードが間違っています。")
        #趣味が100字以内であるか確認
        if hobby and len(hobby) > 100:
            error_hobby.append("趣味は100字以内である必要があります。")
        
        #趣味がちゃんと趣味であるか確認(後ほど実装予定)
        
        #好きな食べ物が100字以内であるか確認
        if favorite_food and len(favorite_food) > 100:
            error_favorite_food.append("好きな食べ物は100字以内である必要があります。")

        #好きな食べ物がちゃんと食べ物であるか確認(後ほど実装予定)





            
        if not any([error_user_id, error_password, error_favorite_food, error_hobby]):
            #認証に成功したら、食べ物、趣味がそれぞれ空欄の場合は何もしない。更新されていたらデータを更新する。USERオブジェクトを作成。
            

            # 1. まずはフォームの値をそのまま取得
            raw_favorite_food = request.form.get('favorite-food')

            # 2. 更新が必要かどうかの判定
            if raw_favorite_food is not None and raw_favorite_food != "":
                # 前後の空白を消してみる
                cleaned_food = raw_favorite_food.strip()
                
                # 【判定】
                # もし cleaned_food が空になったら、それは「スペースのみ」が入力されたということ
                # その場合は DB を NULL または空文字で更新する（＝消去）
                if cleaned_food == "":
                    favorite_food_new_value = "なし"  # または ""
                else:
                    favorite_food_new_value = cleaned_food
                    
                # あとは今までのデータと違う場合だけ UPDATE
                if favorite_food_new_value != user_row['favorite_food']:
                    db.execute('UPDATE users SET favorite_food = ? WHERE id = ?', (favorite_food_new_value, user_row['id']))
                    db.commit()



            # 1. まずはフォームの値をそのまま取得
            raw_hobby = request.form.get('hobby')

            # 2. 更新が必要かどうかの判定
            if raw_hobby is not None and raw_hobby != "":
                # 前後の空白を消してみる
                cleaned_hobby = raw_hobby.strip()
                
                # 【判定】
                # もし cleaned_hobby が空になったら、それは「スペースのみ」が入力されたということ
                # その場合は DB を NULL または空文字で更新する（＝消去）
                if cleaned_hobby == "":
                    hobby_new_value = "なし"  # または ""
                else:
                    hobby_new_value = cleaned_hobby
                    
                # あとは今までのデータと違う場合だけ UPDATE
                if hobby_new_value != user_row['hobby']:
                    db.execute('UPDATE users SET hobby = ? WHERE id = ?', (hobby_new_value, user_row['id']))
                    db.commit()

            #最新のユーザーデータをデータベースから取得
            user_row = db.execute(
                'SELECT * FROM users WHERE id = ?', (user_row['id'],)
            ).fetchone()

            #最新のユーザーデータをもとにUSERオブジェクトを作成
            user_object = User(
                id=user_row['id'],
                email=user_row['email'],
                password=user_row['password'],
                username=user_row['username'],
                user_id=user_row['user_id'],
                hobby=user_row['hobby'],
                favorite_food=user_row['favorite_food']
            )
            #セッションを確立（login_userはflaskの関数）
            login_user(user_object)

            #クエリパラメータからURLを取得
            next_page = request.args.get('next')
            #クエリパラメータがあればそこへ、なければマイページへ転送
            return redirect(next_page or url_for('main.mypage'))
        else: #エラーがある場合はリダイレクトせずエラーを引数にしてHTMLで表示
            return render_template('signin.html', error_user_id=error_user_id, error_password=error_password, error_favorite_food=error_favorite_food, error_hobby=error_hobby)
#ログアウト        
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


