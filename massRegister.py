import requests
import csv
import sys
import json
from bs4 import BeautifulSoup
import time
try:
    filepath=sys.argv[1]
except IndexError:
    filepath = input("What is the filepath of the csv with people")
finally:
    with open(filepath, "r", newline="") as fp:
        reader=csv.reader(fp, delimiter=",", quotechar='"')
        next(reader, None)
        for row in reader:
            time.sleep(0.1)
            urlNew = f"http://10.147.137.251/station/scan/"
            session = requests.Session()
            response = session.get(urlNew)
            soup = BeautifulSoup(response.text, "html.parser")
            csrfElement = soup.find("input", {"name": "csrfmiddlewaretoken"})
            csrfToken = csrfElement["value"]
            headers = {
                "Referer": urlNew
            }
            payloadFirst = {"csrfmiddlewaretoken": csrfToken, 'barcode': row[4]}
            response = session.post(urlNew, data=payloadFirst, headers=headers)
            urlUser = f"http://10.147.137.251/station/new-user/{row[4]}/"
            time.sleep(0.1)
            csrfElement = soup.find("input", {"name": "csrfmiddlewaretoken"})
            csrfToken = csrfElement["value"]
            payload = {"csrfmiddlewaretoken": csrfToken, 'first_name': row[1], 'last_name': row[2], 'email': row[3]}
            response = session.post(urlUser, data=payload, headers=headers)
