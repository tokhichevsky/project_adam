import os
import random

import psycopg2


class DataBase:
    def __init__(self):
        DATABASE_URL = os.environ['DATABASE_URL']
        self.connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.cursor = self.connection.cursor()
        self.generate_tables()

    def generate_tables(self):
        try:
            self.cursor.execute('SELECT * FROM "users"')
        except Exception:
            self.connection.rollback()
            print("Tables don't exist. Creating...")
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "users" (
	                "telegram_id" integer NOT NULL,
	                "username" VARCHAR(255) NOT NULL UNIQUE,
	                "is_admin" BOOLEAN NOT NULL DEFAULT 'FALSE',
	                CONSTRAINT "users_pk" PRIMARY KEY ("telegram_id")
                ) WITH (
                    OIDS=FALSE
                );
                """
            )
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "files" (
	                "hash" VARCHAR(255) NOT NULL,
	                "status" VARCHAR(255) NOT NULL DEFAULT 'unchecked',
	                "filepath" VARCHAR(255) NOT NULL UNIQUE,
	                "source" VARCHAR(255),
	                "checked_by" integer,
	                CONSTRAINT "files_pk" PRIMARY KEY ("hash")
                ) WITH (
                    OIDS=FALSE
                );
                """
            )
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "instagrams" (
	                "username" VARCHAR(255) NOT NULL,
	                "last_update" timestamp without time zone NOT NULL DEFAULT '2001-01-01 00:00:00'::timestamp without time zone,
	                "approved_photos" integer NOT NULL DEFAULT '0',
	                "unapproved_photos" integer NOT NULL DEFAULT '0',
	                CONSTRAINT "instagrams_pk" PRIMARY KEY ("username")
                ) WITH (
                    OIDS=FALSE
                );
                """
            )
            self.cursor.execute(
                'ALTER TABLE "files" ADD CONSTRAINT "files_fk0" FOREIGN KEY ("checked_by") REFERENCES "users"("telegram_id");'
            )
            self.cursor.execute(
                'ALTER TABLE "files" ADD CONSTRAINT "files_fk1" FOREIGN KEY ("source") REFERENCES "instagrams"("username");'
            )
            self.connection.commit()

    def add_instagram_user(self, username: str):
        self.cursor.execute(
            "SELECT COUNT(*) FROM instagrams WHERE username = %s", (username,)
        )
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                "INSERT INTO instagrams (username) VALUES(%s)", (username,)
            )
            print("Added new instagram user '{}'".format(username))
            self.connection.commit()

    def add_user(self, telegram_id, username: str, is_admin: bool = False):
        self.cursor.execute(
            "SELECT COUNT(*) FROM users WHERE telegram_id = %s", (telegram_id,)
        )
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                "INSERT INTO users VALUES(%s, %s, %s)", (telegram_id, username, is_admin)
            )
            print("Added new user: [{}, {}, {}]".format(telegram_id, username, is_admin))
            self.connection.commit()

    def add_photo(self, hash: str, filepath: str, source: str or int = None):
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM files WHERE hash = %s", (hash,)
            )
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute(
                    "INSERT INTO files (hash, filepath, source) VALUES(%s, %s, %s)", (hash, filepath, source)
                )
                self.connection.commit()
                return "Изображение добавлено в базу."
            else:
                return "Данное изображение уже имеется в базе."
        except Exception as e:
            return e

    def get_records(self, table: str, names: list, additional_rules="*"):
        self.cursor.execute('SELECT {} FROM {}'.format(additional_rules, table))
        records = self.cursor.fetchall()
        result = []
        for record in records:
            instaobj = {}
            for name, field in zip(names, record):
                instaobj[name] = field
            result.append(instaobj)
        return result

    def get_instagram_user(self, username: str):
        self.cursor.execute("SELECT * FROM instagrams WHERE username = %s", (username,))
        record = self.cursor.fetchone()
        return {"username": record[0], "last_update": record[1], "approved_photos": record[2],
                "unapproved_photos": record[3]}

    def update_timestamp_for_instagram(self, username: str):
        try:
            self.cursor.execute(
                "UPDATE instagrams SET last_update = now() WHERE username = %s", (username,)
            )
            self.connection.commit()
        except Exception as e:
            print(e)

    def get_random_photos(self, num: int = 10, status: str = "unchecked"):

        self.cursor.execute("SELECT COUNT(*) FROM files WHERE status = %s;", (status,))
        records_num = self.cursor.fetchone()[0]
        random_records = random.shuffle(range(0, records_num + 1))[:num]
        sql = ' UNION '.join(
            ["(SELECT * FROM files WHERE status = '{}' LIMIT 1 OFFSET {})".format(status, record) for record in
             random_records])
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        return [{"hash": row[0], "status": row[1], "filepath": row[2], "source": row[3], "checked_by": row[4]} for row
                in answer]

    def get_photos_for_deleting(self):
        self.cursor.execute("SELECT * FROM files WHERE status = 'deleted';")
        answer = self.cursor.fetchall()
        return [{"hash": row[0], "status": row[1], "filepath": row[2], "source": row[3], "checked_by": row[4]} for row
                in answer]

    def set_photo_status(self, hash: str, status: str):
        if status in ["unchecked", "checked", "published"]:
            try:
                self.cursor.execute("UPDATE files SET status = {} WHERE hash = '{}'".format(status, hash))
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()
                print(e)

    def delete_photo(self, hash: str):
        try:
            self.cursor.execute("DELETE FROM files WHERE hash = {}".format(hash))
            self.connection.commit()
            return "Изображение успешно удалено."
        except Exception as e:
            self.connection.rollback()
            return e


    def get_image_info(self, hash: str):
        self.cursor.execute(
            "SELECT * FROM files WHERE hash=%s", (hash,)
        )
        record = self.cursor.fetchone()
        return {"hash": record[0], "status": record[1], "filepath": record[2], "source": record[3],
                "checked_by": record[4]}

    def set_admin(self, login: str):
        try:
            self.cursor.execute("UPDATE users SET is_admin = TRUE WHERE username = '{}'".format(login))
            self.connection.commit()
            return "Пользователь {} успешно сделан администратором".format(login)
        except Exception as e:
            self.connection.rollback()
            return e

    def is_admin(self, login: str or int):
        try:
            if type(login) == int:
                self.cursor.execute("SELECT is_admin FROM users WHERE telegram_id = '{}'".format(login))
                return self.cursor.fetchone()[0]
            elif type(login) == str:
                self.cursor.execute("SELECT is_admin FROM users WHERE login = '{}'".format(login))
                return self.cursor.fetchone()[0]
        except Exception as e:
            print(e)
        return False

    def delete_last_rows(self, table: str = "files", num: int = 1000, key_field: str = "hash"):
        try:
            self.cursor.execute(
                "DELETE FROM {0} WHERE {1} IN (SELECT {1} FROM {0} ORDER BY {1} DESC LIMIT {2})".format(table, key_field,
                                                                                                       num))
            self.connection.commit()
            print("Из таблицы {} успешно удалено {} записей".format(table, num))
        except Exception as e:
            self.connection.rollback()
            print(e)



    def execute(self, sql: str):
        try:
            self.cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            return e
        return "Команда успешно выполнена"
