#models.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, username, user_id, hobby=None, favorite_food=None, address=None):
        #引数であるDBからのデータをオブジェクトにぶち込む
        self.id = id
        self.email = email
        self.password = password
        self.username = username
        self.user_id = user_id
        self.hobby = hobby
        self.favorite_food = favorite_food
        self.address = address


    pass