from __future__ import annotations

from typing import Dict

import requests

from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import Session, declarative_base

from canvasapi import Canvas
from canvasapi.user import User as CanvasUser

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    niner_id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    canvas_id = Column(Integer, nullable=True)
    pronouns = Column(Text, nullable=True)
    
    def try_to_get_info_from_niner_engage(self, session:Session, config:Dict[str, str]) -> User:
        if self.first_name and self.last_name and self.email:
            if "t" in config.get("VERBOSE_DEBUG", "false").lower(): print(f"Values Already set, shouldnt have run")
            return self
        url = "https://ninerengage.charlotte.edu/api/discovery/swipe/attendance"
        headers = {"Cookie": config["NINER_ENGAGE_COOKIE"],
               "X-Xsrf-Token": config["NINER_ENGAGE_TOKEN"]}
        data = {
            "swipe": self.niner_id,
            "token": config["NINER_ENGAGE_PAYLOAD_TOKEN"]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(response.status_code)
            val_dic = response.json()
            self.first_name = val_dic["user"]["firstName"]
            self.last_name = val_dic["user"]["lastName"]
            self.email = val_dic["user"]["campusEmail"]
            session.add(self)
        else:
            if "t" in config.get("VERBOSE_DEBUG", "false").lower(): print(f"response: {response.status_code} -- {response.text}")

        return self
    
    def try_to_get_info_from_canvas(self, session:Session, config:Dict):
        canvas = Canvas("https://instructure.charlotte.edu", config["CANVAS_API_KEY"])
        
        

    def __repr__(self):
        return f"<User(niner_id={self.niner_id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, canvas_id={self.canvas_id}, pronouns={self.pronouns})>"

