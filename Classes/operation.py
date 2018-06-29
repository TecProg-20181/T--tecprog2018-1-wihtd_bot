from Classes.initialize import Initialize
from datetime import datetime

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

    def start(self, chat):
                self.Initialization.send_message("Welcome! Here is a list of things you can do.", chat)
                self.Initialization.send_message(Initialization.help, chat)

    def help(self, chat):
                self.Initialization.send_message("Here is a list of things you can do.", chat)
                self.Initialization.send_message(Initialization.help, chat)

    def handling_exception(self, msg, task_id, chat):
        query = db.session.query(Task).filter_by(id=task_id, chat=chat)
        try:
            self.task = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            Initialization.send_message("_404_ Task {} not found x.x".format(task_id), chat)
            return 1
        return self.task

    def githubIssue_create(self, title):
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
        self.githubIssue_create(self.task.name)

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

    def dependson(self, text, msg, chat):
                if not msg.isdigit():
                    Initialization.send_message("You must inform the task id", chat)
                else:
                    task_id = int(msg)
                    self.task = self.handling_exception(msg,task_id,chat)
                    if self.task == 1:
                        return

                    if text == '':
                        for i in self.task.dependencies.split(',')[:-1]:
                            i = int(i)
                            q = db.session.query(Task).filter_by(id=i, chat=chat)
                            t = q.one()
                            t.parents = t.parents.replace('{},'.format(self.task.id), '')

                        self.task.dependencies = ''
                        Initialization.send_message("Dependencies removed from task {}".format(task_id), chat)
                    else:
                        for depid in text.split(' '):
                            if not depid.isdigit():
                                Initialization.send_message("All dependencies ids must be numeric, and not {}".format(depid), chat)
                            else:
                                depid = int(depid)
                                query = db.session.query(Task).filter_by(id=depid, chat=chat)
                                try:
                                    taskdep = query.one()
                                    taskdep.parents += str(self.task.id) + ','
                                except sqlalchemy.orm.exc.NoResultFound:
                                    Initialization.send_message("_404_ Task {} not found x.x".format(depid), chat)
                                    continue

                                deplist = self.task.dependencies.split(',')
                                if str(depid) not in deplist:
                                    self.task.dependencies += str(depid) + ','

                    db.session.commit()
                    Initialization.send_message("Task {} dependencies up to date".format(task_id), chat)

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
                        t.parents = t.parents.replace('{},'.format(self.task.id), '')

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

        for i in range(len(task.dependencies.split(',')[:-1])):
            line = preceed
            query = db.session.query(Task).filter_by(id=int(task.dependencies.split(',')[:-1][i]), chat=chat)
            dep = query.one()

            icon = '\U0001F195'
            if dep.status == 'DOING':
                icon = '\U000023FA'
            elif dep.status == 'DONE':
                icon = '\U00002611'

            if i + 1 == len(self.task.dependencies.split(',')[:-1]):
                if self.task.duedate == None:
                    line += '└── [[{}]] {} {} {}\n'.format(dep.id, icon, dep.name, dep.priority)
                else:
                    line += '└── [[{}]] {} {} {} *Send date:* {}\n'.format(dep.id, icon, dep.name, dep.priority, dep.duedate)
                line += self.deps_text(dep, chat, preceed + '    ')
            else:
                if self.task.duedate == None:
                    line += '├── [[{}]] {} {} {}\n'.format(dep.id, icon, dep.name, dep.priority)
                else:
                    line += '├── [[{}]] {} {} {} *Send date:* {}\n'.format(dep.id, icon, dep.name, dep.priority, dep.duedate)
                line += self.deps_text(dep, chat, preceed + '│   ')

            text += line

        return text

    def priority(self, text, msg, chat):
                if not msg.isdigit():
                    Initialization.send_message("You must inform the task id", chat)
                else:
                    task_id = int(msg)
                    self.task = self.handling_exception(msg,task_id,chat)
                    if self.task == 1:
                        return

                    if text == '':
                        self.task.priority = ''
                        Initialization.send_message("_Cleared_ all priorities from task {}".format(task_id), chat)
                    else:
                        if text.lower() not in ['high', 'medium', 'low']:
                            Initialization.send_message("The priority *must be* one of the following: high, medium, low", chat)
                        else:
                            if text.lower() == 'low':
                                self.task.priority = '\U0001F535'
                            elif text.lower() == 'medium':
                                self.task.priority = '\U0001F315'
                            else:
                                self.task.priority = '\U0001F534'

                            Initialization.send_message("*Task {}* priority has priority *{}*".format(task_id, text.lower()), chat)
                    db.session.commit()

    def senddate(self, text, msg, chat):
        if not msg.isdigit():
            Initialization.send_message("You must inform the task id", chat)
        else:
            task_id = int(msg)
            self.task = self.handling_exception(msg,task_id,chat)
            if self.task == 1:
                return

            if text == '':
                self.task.duedate = ''
                Initialization.send_message("You wanted to set task {} senddate, but you didn't provide a date".format(task_id), chat)
                return

            try:
                datetime.strptime(text, '%d/%m/%Y')
            except ValueError:
                Initialization.send_message("Invalid date - (format: day/mounth/year)", chat)
                return 1

            self.task.duedate = datetime.strptime(text, '%d/%m/%Y')
            Initialization.send_message("Task {} date set to {}".format(task_id, text), chat)
            db.session.commit()

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

                    if self.task.duedate == None:
                        a += '[[{}]] {} {}\n'.format(self.task.id, self.task.name, self.task.priority)
                    else:
                        a += '[[{}]] {} {} *Send Date:* {}\n'.format(self.task.id, self.task.name, self.task.priority, self.task.duedate)
                    a += self.deps_text(self.task, chat)

                Initialization.send_message(a, chat)
                a = ''

                a += '\U0001F4DD _Status_\n'
                query = db.session.query(Task).filter_by(status='TODO', chat=chat).order_by(Task.id)
                a += '\n\U0001F195 *TODO*\n'
                for self.task in query.all():
                    if self.task.duedate == None:
                        a += '[[{}]] {} {}\n'.format(self.task.id, self.task.name, self.task.priority)
                    else:
                        a += '[[{}]] {} {} *Send Date:* {}\n'.format(self.task.id, self.task.name, self.task.priority, self.task.duedate)
                query = db.session.query(Task).filter_by(status='DOING', chat=chat).order_by(Task.id)
                a += '\n\U000023FA *DOING*\n'
                for self.task in query.all():
                    if self.task.duedate == None:
                        a += '[[{}]] {} {}\n'.format(self.task.id, self.task.name, self.task.priority)
                    else:
                        a += '[[{}]] {} {} *Send Date:* {}\n'.format(self.task.id, self.task.name, self.task.priority, self.task.duedate)
                query = db.session.query(Task).filter_by(status='DONE', chat=chat).order_by(Task.id)
                a += '\n\U00002611 *DONE*\n'
                for self.task in query.all():
                    if self.task.duedate == None:
                        a += '[[{}]] {} {}\n'.format(self.task.id, self.task.name, self.task.priority)
                    else:
                        a += '[[{}]] {} {} *Send Date:* {}\n'.format(self.task.id, self.task.name, self.task.priority, self.task.duedate)

                Initialization.send_message(a, chat)
                return
