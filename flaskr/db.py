#db.py
import sqlite3
import click
from flask import g, current_app
from werkzeug.security import generate_password_hash
DATABASE = 'users.db'


def get_db():
    if 'db' not in g:
       db_path = current_app.config.get('DATABASE', DATABASE)
       g.db = sqlite3.connect(
           db_path,
           detect_types=sqlite3.PARSE_DECLTYPES
       )
       g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)

    # 初期化コマンドを定義
    @app.cli.command('init-db')
    def init_db_command():
        # テーブルを削除
        delete_users_db()  

        # テーブルを再度作成
        create_users_table()
        # 初期データ挿入
        insert_initial_users()

        click.echo('Initialized the database.')


def create_users_table():
    db = get_db()
    db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, user_id TEXT UNIQUE NOT NULL, username TEXT NOT NULL, password TEXT NOT NULL, hobby TEXT, favorite_food TEXT)')
    db.commit() 

def delete_users_db():
    db = get_db()
    db.execute("DROP TABLE IF EXISTS users")
    db.commit()

def insert_initial_users():
    db = get_db()

    hashed_password_1 = generate_password_hash('yaosumi')

    hashed_password_2 = generate_password_hash('example')

    db.execute("""INSERT INTO users
                (email, user_id, password, username, hobby, favorite_food)
                VALUES (?, ?, ?, ?, ?, ?)""",
                ('atsugorilla@gmail.com', 'atsuki', hashed_password_1, 'atsuki', 'reading', 'あんかけチャーハン')
                )
    
    db.execute("""INSERT INTO users
                (email, user_id, password, username, hobby, favorite_food)
                VALUES (?, ?, ?, ?, ?, ?)""",
                ('example@gmail.com', 'example', hashed_password_2, 'example', 'swimming', 'pizza')
                )
    db.commit()
