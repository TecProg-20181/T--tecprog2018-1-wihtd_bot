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
        self.task = ''
        self.dtask = ''
        self.Initialization = Initialize()

    def handling_exception(self, msg, task_id, chat):
        query = db.session.query(Task).filter_by(id=task_id, chat=chat)
        try:
            self.task = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            Initialization.send_message("_404_ Task {} not found x.x".format(task_id), chat)
            return 1
        return self.task

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

    def rename(self, text, msg, chat):
        if not msg.isdigit():
            Initialization.send_message("You must inform the task id", chat)
        else:
            task_id = int(msg)
            self.task = self.handling_exception(msg,task_id,chat)
            if self.task == 1:
                return

            if text == '':
                Initialization.send_message("You want to modify task {}, but you didn't provide any new text".format(task_id), chat)
                return

            old_text = self.task.name
            self.task.name = text
            db.session.commit()
            Initialization.send_message("Task {} redefined from {} to {}".format(task_id, old_text, text), chat)

    def delete(self, msg, chat):
                if not msg.isdigit():
                    Initialization.send_message("You must inform the task id", chat)
                    return
                else:
                    task_id = int(msg)
                    self.task = self.handling_exception(msg,task_id,chat)
                    if self.task == 1:
                        return

                if self.task.parents != '':
                    Initialization.send_message("Cannot delete a dependent based task", chat)
                    return

                else:
                    for t in self.task.dependencies.split(',')[:-1]:
                        qy = db.session.query(Task).filter_by(id=int(t), chat=chat)
                        t = qy.one()
                        t.parents = t.parents.replace('{},'.format(task.id), '')

                db.session.delete(self.task)
                db.session.commit()
                Initialization.send_message("Task [[{}]] deleted".format(task_id), chat)

    def todo(self, msg, chat):
        for task_id in msg.split(' '):
            if not task_id.isdigit():
                Initialization.send_message("You must inform the task id", chat)
            else:
                msg2 = msg.split()
                task_id = int(task_id)
                self.task = self.handling_exception(msg, task_id, chat)
                if self.task == 1:
                    return

            self.task.status = 'TODO'
            db.session.commit()
            Initialization.send_message("*TODO* task [[{}]] {} {}".format(self.task.id, self.task.name, self.task.priority), chat)

    def doing(self, msg, chat):
        for task_id in msg.split(' '):
            if not task_id.isdigit():
                Initialization.send_message("You must inform the task id", chat)
            else:
                msg2 = msg.split()
                task_id = int(task_id)
                self.task = self.handling_exception(msg, task_id, chat)
                if self.task == 1:
                    return

            self.task.status = 'DOING'
            db.session.commit()
            Initialization.send_message("*DOING* task [[{}]] {} {}".format(self.task.id, self.task.name, self.task.priority), chat)

    def done(self, msg, chat):
        for task_id in msg.split(' '):
            if not task_id.isdigit():
                Initialization.send_message("You must inform the task id", chat)
            else:
                msg2 = msg.split()
                task_id = int(task_id)
                self.task = self.handling_exception(msg, task_id, chat)
                if self.task == 1:
                    return

            self.task.status = 'DONE'
            db.session.commit()
            Initialization.send_message("*DONE* task [[{}]] {} {}".format(self.task.id, self.task.name, self.task.priority), chat)

    def deps_text(self, task, chat, preceed=''):
        text = ''

        for i in range(len(self.task.dependencies.split(',')[:-1])):
            line = preceed
            query = db.session.query(Task).filter_by(id=int(self.task.dependencies.split(',')[:-1][i]), chat=chat)
            dep = query.one()

            icon = '\U0001F195'
            if dep.status == 'DOING':
                icon = '\U000023FA'
            elif dep.status == 'DONE':
                icon = '\U00002611'

            if i + 1 == len(self.task.dependencies.split(',')[:-1]):
                line += '└── [[{}]] {} {} {}\n'.format(dep.id, icon, dep.name, dep.priority)
                line += self.deps_text(dep, chat, preceed + '    ')
            else:
                line += '├── [[{}]] {} {} {}\n'.format(dep.id, icon, dep.name, dep.priority)
                line += self.deps_text(dep, chat, preceed + '│   ')

            text += line

        return text

    def duplicate(self, msg, chat):
                if not msg.isdigit():
                    Initialization.send_message("You must inform the task id", chat)
                else:
                    task_id = int(msg)
                    self.task = self.handling_exception(msg,task_id,chat)
                    if self.task == 1:
                        return


                    self.dtask = Task(chat=self.task.chat, name=self.task.name, status=self.task.status, dependencies=self.task.dependencies,
                                 parents=self.task.parents, priority=self.task.priority, duedate=self.task.duedate)
                    db.session.add(self.dtask)

                    for t in self.task.dependencies.split(',')[:-1]:
                        qy = db.session.query(Task).filter_by(id=int(t), chat=chat)
                        t = qy.one()
                        t.parents += '{},'.format(self.dtask.id)

                    db.session.commit()
                    Initialization.send_message("New task *TODO* [[{}]] {} {}".format(self.dtask.id, self.dtask.name, self.dtask.priority), chat)

    def list(self, msg, chat):
                a = ''

                a += '\U0001F4CB Task List\n'
                query = db.session.query(Task).filter_by(parents='', chat=chat).order_by(Task.id)
                for self.task in query.all():
                    icon = '\U0001F195'
                    if self.task.status == 'DOING':
                        icon = '\U000023FA'
                    elif self.task.status == 'DONE':
                        icon = '\U00002611'

                    a += '[[{}]] {} {} {}\n'.format(self.task.id, icon, self.task.name, self.task.priority)
                    a += self.deps_text(self.task, chat)

                Initialization.send_message(a, chat)
                a = ''

                a += '\U0001F4DD _Status_\n'
                query = db.session.query(Task).filter_by(status='TODO', chat=chat).order_by(Task.id)
                a += '\n\U0001F195 *TODO*\n'
                for self.task in query.all():
                    a += '[[{}]] {} {}\n'.format(self.task.id, self.task.name, self.task.priority)
                query = db.session.query(Task).filter_by(status='DOING', chat=chat).order_by(Task.id)
                a += '\n\U000023FA *DOING*\n'
                for self.task in query.all():
                    a += '[[{}]] {} {}\n'.format(self.task.id, self.task.name, self.task.priority)
                query = db.session.query(Task).filter_by(status='DONE', chat=chat).order_by(Task.id)
                a += '\n\U00002611 *DONE*\n'
                for self.task in query.all():
                    a += '[[{}]] {} {}\n'.format(self.task.id, self.task.name, self.task.priority)

                Initialization.send_message(a, chat)
