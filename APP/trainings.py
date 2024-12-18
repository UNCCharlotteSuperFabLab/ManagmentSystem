import mysql.connector
from users import User, Users
from visits import Visits
import datetime
from dotenv import dotenv_values
from time import sleep
from typing import List
from dataclasses import dataclass
from enum import IntEnum

class TrainingLevels(IntEnum):
    no_training = 0
    canvas_course = 10
    red_dot = 20
    green_dot = 30
    dof = 40
    trainer = 50
    certifier = 60
    
@dataclass
class Training:
    id:int
    tool_category_id:int
    user:User
    level:TrainingLevels
    train_date:datetime.datetime
    
    @classmethod
    def from_sql_row(cls, sql_row, user_manager:Users) -> 'Training':
        return cls(sql_row[0], sql_row[1], user_manager.find_or_create_user(sql_row[2]), TrainingLevels(sql_row[3]), sql_row[4])

class Trainings:
    def __init__(self, mysql_connection:mysql.connector.MySQLConnection):
        self.mydb = mysql_connection
        
    def train(self, user:User, training_level:TrainingLevels, tool):
        pass
        
    
    