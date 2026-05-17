
# __init__.py

from flask import Flask
# ★★★ mainのインポートは削除 ★★★
from . import db # dbは残します
from flask_login import LoginManager
from .models import User

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE='users.db',
    )
    app.debug = True
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(pk_id): # 引数のカンマは取っておきましょう
        from flaskr.db import get_db
        db_con = get_db()
        
        # 1. SQLに user_id, hobby, favorite_food, address を追加する
        user_data = db_con.execute(
            'SELECT id, username, email, password, user_id, hobby, favorite_food, address FROM users WHERE id = ?', 
            (pk_id,)
        ).fetchone()
        
        if user_data is None:
            return None
        
        # 2. ユーザーオブジェクトを作る時に、すべての引数を渡す
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            password=user_data['password'],
            username=user_data['username'],
            user_id=user_data['user_id'],      # ← これが必須！
            hobby=user_data['hobby'],          # ついでに追加
            favorite_food=user_data['favorite_food'], # ついでに追加
            address=user_data['address']       # ついでに追加
        )
        return user
    
    
    
    # ★★★ 関数内でインポートする（インポート遅延） ★★★
    from . import main 
    from . import auth
    from . import user
    from . import message # 追加
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(message.bp)

    return app