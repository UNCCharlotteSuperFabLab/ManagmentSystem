import mysql.connector
from users import User, Users
import datetime
from dotenv import dotenv_values
from time import sleep
from typing import List

class Visits():
    def __init__(self, user_controller:Users):
        self.config = dotenv_values("/Users/philip/Projects/fablab/ManagmentSystem/.env")
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="fablab",
            password=self.config.get("MYSQL_USER_PASSWORD"),
            database="fablab"
        )
        self.user_controller = user_controller
    
    def scan(self, niner_id:int) -> User:
        now = datetime.datetime.now()
        user = self.user_controller.find_or_create_user(niner_id)
        with self.mydb.cursor() as cur:
            cur.execute(f"SELECT * FROM visits WHERE user_id={niner_id} AND status='IN'")
            result = cur.fetchone()
            if result:
                cur.execute(f"UPDATE visits SET exit_time=NOW(), status='OUT' WHERE user_id={niner_id} AND status='IN'")
                print("sign out")
            else:
                cur.execute(f"INSERT INTO visits (user_id,enter_time,status) VALUES ({niner_id}, NOW(), 'IN')")
                print("sign in")
            self.mydb.commit()
        return user
            
    def get_signed_in_users(self) -> List[User]:
        with self.mydb.cursor() as cur:
            cur.execute(f"SELECT users.* FROM users INNER JOIN visits ON users.niner_id = visits.user_id WHERE visits.status ='IN'")
            users = []
            for row in cur.fetchall():
                users.append(User.from_database(row))
            return users
    

if __name__ == "__main__":
    visits = Visits(Users())
    for i in range(8):
        print(visits.scan(801276949))
        if i % 2 == 0:
            visits.scan(801256059)
        print(visits.get_signed_in_users())
        sleep(1)

