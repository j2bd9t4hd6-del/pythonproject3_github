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
        delete_messages_db()
        # テーブルを再度作成
        create_users_table()
        create_messages_table()
        # 初期データ挿入
        insert_initial_users()
        insert_initial_messages()
        click.echo('Initialized the database.')
    @app.cli.command('init-messages-db')
    def init_message_db_command():
        delete_messages_db()
        create_messages_table()
        insert_initial_messages()
        click.echo('Initialized the message database.')

def create_users_table():
    db = get_db()
    db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, user_id TEXT UNIQUE NOT NULL, username TEXT NOT NULL, password TEXT NOT NULL, hobby TEXT, favorite_food TEXT, address TEXT UNIQUE NOT NULL)')
    db.commit() 

def create_messages_table():
    db = get_db()
    db.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT, sender_address TEXT NOT NULL, recipient_address TEXT NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, is_delivered BOOLEAN DEFAULT 0)')
    db.commit()

def delete_users_db():
    db = get_db()
    db.execute("DROP TABLE IF EXISTS users")
    db.commit()

def delete_messages_db():
    db = get_db()
    db.execute("DROP TABLE IF EXISTS messages")
    db.commit()

def insert_initial_users():
    db = get_db()

    hashed_password_1 = generate_password_hash('yaosumi')

    hashed_password_2 = generate_password_hash('example')

    db.execute("""INSERT INTO users
                (email, user_id, password, username, hobby, favorite_food, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ('atsugorilla@gmail.com', 'atsuki', hashed_password_1, 'atsuki', 'reading', 'あんかけチャーハン', 'あお-い-001')
                )
    
    db.execute("""INSERT INTO users
                (email, user_id, password, username, hobby, favorite_food, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ('example@gmail.com', 'example', hashed_password_2, 'example', 'swimming', 'pizza', 'あお-い-002')
                )
    db.commit()

def insert_initial_messages():
    db = get_db()
    db.execute("""INSERT INTO messages
                (body, sender_address, recipient_address)
                VALUES (?, ?, ?)""",
                ('Hello, this is a test message.', 'あお-い-001', 'あお-い-002')
                )
    db.execute("""INSERT INTO messages
                (body, sender_address, recipient_address) 
                VALUES (?, ?, ?)""",
                ('Hi! This is another test message.', 'あお-い-002', 'あお-い-001')
                )
    db.commit()