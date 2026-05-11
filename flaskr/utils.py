# utils.py
import random

def get_scenario(user):
    chara_A = "寧"
    chara_B = "苛"
    b_id = [
            "パッとしない",
            "でたらめな",
                   "変な",
                 ]
    a_hobby = [
            "意外とアウトドアなところあるんだね！",
                 "イメージ通りかも。",
                 "わかるー！結構興奮するんだよね！",
                 "なんていうか、変わってるね。"
                 ]
    a_hobby_none =[
            "趣味、なしかぁ。まあ、忙しいもんね…"
                 ]
    b_hobby = [
            "なんだか無理して書いてそうだな。",
                   "俺は嫌いだ。"
                   ]
    b_hobby_none = [
                   "つまらないやつだな",
                 ]
    a_food = [
        "たしかに、あれは癖になるよね…",
                   "なんだか渋いチョイスだね。",
                   "え、それって食べられるの…？"]
    a_food_none = [
                   "あれ、好きな食べ物、ないの？良くも悪くも、好き嫌いがないってこと？",                   
                   ]
    b_food = [
                    "悪くない。",
                   "とんでもないバカ舌だな。",
                   "精神年齢は5歳以下だな。"]
    b_food_none = [
                   "どうでもいい"
                 ]
    b_hobby_food_none = [
                   "趣味もなし、好きな食べ物もなしか。いったい何が楽しくて生きてるんだ？"
                   ]

    b_id_choice = random.choice(b_id)
    if user.hobby != "なし":
        a_hobby_choice = f"へー！{ user.hobby }が趣味なんだ！{ random.choice(a_hobby) }"
        b_hobby_choice = random.choice(b_hobby)
    else:
        a_hobby_choice = random.choice(a_hobby_none)
        b_hobby_choice = random.choice(b_hobby_none)
    if user.favorite_food != "なし":
        a_food_choice = f"あと、好きな食べ物は{ user.favorite_food }なんだって。{ random.choice(a_food) }"
        b_food_choice = random.choice(b_food)
    else:
        a_food_choice = random.choice(a_food_none)
        b_food_choice = random.choice(b_food_none)
    if user.hobby == "なし" and user.favorite_food == "なし":
        b_food_choice = random.choice(b_hobby_food_none)

    scenario1 = [
        (chara_A, f"えーっと…この人は…{ user.username }さん。だって"),
        (chara_B, "了解。IDとアドレス、登録番号を。早く。"),
        (chara_A, f"{ user.user_id }、{ user.email }、{ user.id }番だよ"),
        (chara_B, f"{ user.user_id }か、{ b_id_choice }IDだな。"),
        (chara_A, "うーん、そうかな？"),
        (chara_B, "ほかに情報は？"),
        (chara_A, f"ええと…{ a_hobby_choice }"),
        (chara_B, f"{ b_hobby_choice }"),
        (chara_A, "あ、あははー…まあ、そうかも。"),
        (chara_A, f"{ a_food_choice }"),
        (chara_B, f"{ b_food_choice }"),
        (chara_A, "まあ、こんなとこかな。"),
        (chara_B, "さっさと次にいこう。")

    ]
    return scenario1
