import sqlite3

class Database:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread = False)
        self.cursor = self.connection.cursor()
    
    def add_queue(self, chat_id, gender): # Добавление новой очереди
        with self.connection:
            return self.cursor.execute("INSERT INTO `queue` (`chat_id`, `gender`) VALUES (?,?)", (chat_id, gender))
    
    def delete_queue(self, chat_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM `queue` WHERE `chat_id` = ?", (chat_id,))
    
    def delete_chat(self, id_chat):
        with self.connection:
            return self.cursor.execute("DELETE FROM `chats` WHERE `id` = ?", (id_chat,))

    def set_gender(self, chat_id, gender):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM `users` WHERE `chat_id` = ?", (chat_id,)).fetchmany(1)
            if bool(len(user)) == False:
                self.cursor.execute("INSERT INTO `users` (`chat_id`, `gender`) VALUES (?,?)", (chat_id, gender))
                return True
            else:
                return False

    def remove_gender(self, chat_id):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,)).fetchmany(1)
            if len(user) > 0:
                self.cursor.execute("DELETE FROM `users` WHERE chat_id = ?", (chat_id,))
                return True
            else:
                return False

    def get_gender(self, chat_id):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM `users` WHERE `chat_id` = ?", (chat_id,)).fetchmany(1)
            if bool(len(user)):
                for row in user:
                    return row[2]
            else:
                return False

    def get_gender_chat(self, gender):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM `queue` WHERE `gender` = ?", (gender,)).fetchmany(1)
            if bool(len(chat)):
                for row in chat:
                    user_info = [row[1], row[2]]
                    return user_info
            else:
                return [0]

    def get_chat(self):
        with self.connection:
            chat = self.cursor.execute("SELECT * FROM `queue`", ()).fetchmany(1)
            if bool(len(chat)):
                for row in chat:
                    user_info = [row[1], row[2]]
                    return user_info
            else:
                return [0]

    def create_chat(self, chat_one, chat_two):
        with self.connection:
            if chat_two != 0:
                # Создание чата
                self.cursor.execute("DELETE FROM `queue` WHERE `chat_id` = ?", (chat_two,))
                self.cursor.execute("INSERT INTO `chats` (`chat_one`, `chat_two`) VALUES (?,?)", (chat_one, chat_two,))
                return True

            else:
                # Становимся в очередь
                return False

    def get_active_chat(self, chat_id):
        with self.connection:
            # Пытаемся найти чат по chat_one
            chat = self.cursor.execute("SELECT * FROM `chats` WHERE `chat_one` = ?", (chat_id,)).fetchone()
            if chat:
                return [chat[0], chat[2]]  # Возвращаем id и chat_two

            # Пытаемся найти чат по chat_two
            chat = self.cursor.execute("SELECT * FROM `chats` WHERE `chat_two` = ?", (chat_id,)).fetchone()
            if chat:
                return [chat[0], chat[1]]  # Возвращаем id и chat_one

            # Если ничего не найдено, возвращаем False
            return False