import telebot
import sqlite3 as sq


TOKEN = 'YOUR_TOKEN'


class DataBase:
    def __init__(self, name):
        self.name = name

    def execute_query(self, query):
        con = sq.connect(self.name)
        with con:
            cur = con.cursor()
            cur.execute(query)
            con.commit()

    def insert_user(self, user_id, host):
        query = f"INSERT INTO users VALUES('{user_id}', '{host}')"
        self.execute_query(query)

    def delete_user(self, user_id):
        query = f"DELETE FROM users WHERE name='{user_id}'"
        self.execute_query(query)


class TelegramNotifier:

    def __init__(self, token, db_name):
        self.tb = telebot.TeleBot(token, parse_mode=None)
        self.db = DataBase(db_name)
        self.create_welcome()
        self.create_new_user()
        self.delete_user()


    def create_welcome(self):
        @self.tb.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.tb.reply_to(message,
                              "Я - бот для мониторинга уровня CO2")

    def create_new_user(self):
        @self.tb.message_handler(commands=['new'])
        def create_user(message):
            host = message.text.split()[-1]
            self.db.insert_user(message.from_user.id, host)
            self.tb.reply_to(message,
                             f"Я вас записал {host}")

    def delete_user(self):
        @self.tb.message_handler(commands=['delete'])
        def delete_user(message):
            self.db.delete_user(message.from_user.id)
            self.tb.reply_to(message,
                             'Я вас удалил')

    def show_status(self, id, data):
        photo = data.get('photo')
        self.tb.send_photo(id, photo)
        text = data.get('status')
        self.tb.send_message(id, text)





if __name__ == '__main__':
    bot = TelegramNotifier(TOKEN, 'dropchecker.db')
    bot.tb.infinity_polling()