from Classes.initialize import Initialize

import sqlalchemy

import db
from db import Task

Initialization = Initialize()

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

    def new(self, msg, chat):
        self.task = Task(chat=chat, name=msg, status='TODO', dependencies='', parents='', priority='')
        db.session.add(self.task)
        db.session.commit()
        Initialization.send_message("New task *TODO* [[{}]] {}".format(self.task.id, self.task.name), chat)
