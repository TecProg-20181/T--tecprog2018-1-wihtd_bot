from Classes.initialize import Initialize

import sqlalchemy

import db
from db import Task
import os
import json
import requests

Initialization = Initialize()

githublogin = "githublogin.txt"
fp = open(githublogin, 'r')
USERNAME = fp.readline()
LOGIN = list(USERNAME.split(' '))

class Operation():
    def __init__(self):
        self.task = None
        self.msg = None
        self.chat = None
        self.name = None
        self.status = None
        self.dependencies = None
        self.parents = None
        self.priority = None
        self.Initialization = Initialize()

    def make_github_issue(self, title):
        url = 'https://api.github.com/repos/TecProg-20181/T--tecprog2018-1-wihtd_bot/issues'
        # Create an authenticated session to create the issue
        session = requests.Session()
        session.auth = (LOGIN[0], LOGIN[1].rstrip())
        # Create our issue
        issue = {'title': title
                 }
        # Add the issue to our repository
        r = session.post(url, json.dumps(issue))


    def new(self, msg, chat):
        self.task = Task(chat=chat, name=msg, status='TODO', dependencies='', parents='', priority='')
        db.session.add(self.task)
        db.session.commit()
        Initialization.send_message("New task *TODO* [[{}]] {}".format(self.task.id, self.task.name), chat)
        self.make_github_issue(self.task.name)
