import mysql.connector
from dotenv import dotenv_values
from dataclasses import dataclass
from typing import List, Optional
from canvasapi import Canvas
from canvasapi.user import User as CanvasUser


import requests

@dataclass()
class User:
  niner_id:int
  first_name:str
  last_name:str
  email:str
  canvas_id:Optional[int]=None,
  pronouns:str=None
  
  @classmethod
  def from_database(cls, row) -> 'User':
    return cls(row[0], row[1], row[2], row[3], row[4], row[5])

class Users:
  mydb: mysql.connector.MySQLConnection
  def __init__(self, mysql_connection:mysql.connector.MySQLConnection):
    self.mydb = mysql_connection
    API_URL="https://instructure.charlotte.edu"
    self.canvas = Canvas(API_URL, self.config["CANVAS_API_KEY"])
    self.course = self.canvas.get_course(231237)
    
  
  def test_connection(self):
    # Get a cursor
    cur = self.mydb.cursor()
    # Execute a query
    cur.execute("SELECT CURDATE()")
    # Fetch one result
    row = cur.fetchone()
    print("Current date is: {0}".format(row[0]))
    
  def __del__(self):
    self.mydb.close()
  
  def add_user(self, user:User) -> bool:
    cur = self.mydb.cursor()
    try:
      statement = f"""INSERT INTO users (niner_id,{',first_name' if user.first_name else ''},{',last_name' if user.last_name else ''},{',email' if user.email else ''}{',canvas_id' if user.canvas_id else ''})
                VALUES ({user.niner_id} '{',' + user.first_name if user.first_name else ''}' '{',' + user.last_name if user.last_name else ''}' '{',' + user.email if user.email else ''}' '{',' + user.canvas_id if user.canvas_id else ''}');"""
      cur.execute(statement)
      self.mydb.commit()
      val = True
    except Exception as e:
      print(e)
      val = False
    cur.close()
    return val
  
  def add_or_update(self, user:User) -> bool:
    user_fetch = self._get_users(f"niner_id={user.niner_id}")
    if user_fetch:
      with self.mydb.cursor() as cur:
        statement = f"UPDATE users SET first_name='{user.first_name}',last_name='{user.last_name}',email='{user.email}' WHERE niner_id={user.niner_id}"
        cur.execute(statement)
        self.mydb.commit()
    else:
      self.add_user(user)
  
  def _get_users(self, where:str=None) -> List[User]:
    cur = self.mydb.cursor()
    statment = f"SELECT * FROM users {f'WHERE {where}' if where else ''};"
    cur.execute(statment)
    result = []
    for row in cur.fetchall():
      result.append(User.from_database(row))
    return result
  
  def get_all_users(self) -> List[User]:
    return self._get_users()
  
  def find_or_create_user(self, niner_id: int) -> User:
    users = self._get_users(f"niner_id={niner_id}")
    if users and users[0].first_name:
      return users[0]

    url = "https://ninerengage.charlotte.edu/api/discovery/swipe/attendance"
    headers = {"Cookie": self.config["NINER_ENGAGE_COOKIE"],
               "X-Xsrf-Token": self.config["NINER_ENGAGE_TOKEN"]}

    data = {
      "swipe": niner_id,
      "token": "2JMG74X3ZRNY969YJX5786QBJAE285KD"
    }
    try:
      response = requests.post(url, headers=headers, json=data)
      if response.status_code != 200:
        print(response.status_code)
      val_dic = response.json()
      first_name = val_dic["user"]["firstName"]
      last_name = val_dic["user"]["lastName"]
      email = val_dic["user"]["campusEmail"]
    except Exception as e:
      print(e)
      first_name = None
      last_name = None
      email = None
    
    user = User(niner_id, first_name, last_name, email)
    self.add_or_update(user)
    return user
  
  def update_with_canvas(self, user:User):
    if user.canvas_id:
      return
    canvasID = None
    pronouns = None
    for couse_user in self.course.get_users():
      couse_user: CanvasUser
      profile = couse_user.get_profile()
      if profile["primary_email"] == user.email:
        canvasID = profile["id"]
        pronouns = profile["pronouns"]
        break
    if not canvasID:
      print("SEND CANVAS EMAIL HERE")
      return #Send email invite?
    with self.mydb.cursor() as cur:
      statement = f"UPDATE users SET canvas_id={canvasID} {f",pronouns='{pronouns}'" if pronouns else ''} WHERE niner_id={user.niner_id}"
      cur.execute(statement)
      user.canvas_id = canvasID
      user.pronouns = pronouns
      self.mydb.commit()




if __name__ == "__main__":
  config = dotenv_values("/Users/philip/Projects/fablab/ManagmentSystem/.env")
  connection = mysql.connector.connect(
      host="localhost",
      user="fablab",
      password=config.get("MYSQL_USER_PASSWORD"),
      database="fablab"
    )
  users = Users(connection)
  users.test_connection()
  #users.add_user(User(801276949, "Philip", "Smith", "psmit145@charlotte.edu"))
  philip = users.find_or_create_user(801276949)
  varshi = users.find_or_create_user(801256059)
  
  users.update_with_canvas(philip)
  users.update_with_canvas(varshi)
  
  print(philip, varshi)