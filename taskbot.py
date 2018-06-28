#!/usr/bin/env python3

import os
import json
import requests
import time
import urllib
from Classes.token import Token
from Classes.initialize import Initialize
from Classes.operation import Operation

import sqlalchemy

import db
from db import Task

HELP = """
 /new NOME
 /todo ID
 /doing ID
 /done ID
 /delete ID
 /list
 /rename ID NOME
 /dependson ID ID...
 /duplicate ID
 /priority ID PRIORITY{low, medium, high}
 low priority = \U0001F535
 medium priority = \U0001F315
 high priority = \U0001F534
 /help
"""

Initialization = Initialize()
Operation = Operation()


def handling_exception(msg,task_id,chat):
    query = db.session.query(Task).filter_by(id=task_id, chat=chat)
    try:
        task = query.one()
    except sqlalchemy.orm.exc.NoResultFound:
        Initialization.send_message("_404_ Task {} not found x.x".format(task_id), chat)
        return 1
    return task

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))

    return max(update_ids)

def deps_text(task, chat, preceed=''):
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

        if i + 1 == len(task.dependencies.split(',')[:-1]):
            line += '└── [[{}]] {} {} {}\n'.format(dep.id, icon, dep.name, dep.priority)
            line += deps_text(dep, chat, preceed + '    ')
        else:
            line += '├── [[{}]] {} {} {}\n'.format(dep.id, icon, dep.name, dep.priority)
            line += deps_text(dep, chat, preceed + '│   ')

        text += line

    return text

def msgsplit(text, msg):
        if msg != '':
            if len(msg.split(' ', 1)) > 1:
                text = msg.split(' ', 1)[1]
            msg = msg.split(' ', 1)[0]
        return text, msg

def rename(text, msg, chat):
            if not msg.isdigit():
                Initialization.send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                task = handling_exception(msg,task_id,chat)
                if task == 1:
                    return

                if text == '':
                    Initialization.send_message("You want to modify task {}, but you didn't provide any new text".format(task_id), chat)
                    return

                old_text = task.name
                task.name = text
                db.session.commit()
                Initialization.send_message("Task {} redefined from {} to {}".format(task_id, old_text, text), chat)

def duplicate(msg, chat):
            if not msg.isdigit():
                Initialization.send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                task = handling_exception(msg,task_id,chat)
                if task == 1:
                    return


                dtask = Task(chat=task.chat, name=task.name, status=task.status, dependencies=task.dependencies,
                             parents=task.parents, priority=task.priority, duedate=task.duedate)
                db.session.add(dtask)

                for t in task.dependencies.split(',')[:-1]:
                    qy = db.session.query(Task).filter_by(id=int(t), chat=chat)
                    t = qy.one()
                    t.parents += '{},'.format(dtask.id)

                db.session.commit()
                Initialization.send_message("New task *TODO* [[{}]] {} {}".format(dtask.id, dtask.name, dtask.priority), chat)

def delete(msg, chat):
            if not msg.isdigit():
                Initialization.send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                task = handling_exception(msg,task_id,chat)
                if task == 1:
                    return

            if task.parents != '':
                Initialization.send_message("Cannot delete a dependent based task", chat)
                return

            else:
                for t in task.dependencies.split(',')[:-1]:
                    qy = db.session.query(Task).filter_by(id=int(t), chat=chat)
                    t = qy.one()
                    t.parents = t.parents.replace('{},'.format(task.id), '')

                db.session.delete(task)
                db.session.commit()
                Initialization.send_message("Task [[{}]] deleted".format(task_id), chat)

def todo(msg, chat):
    for task_id in msg.split(' '):
        if not task_id.isdigit():
            Initialization.send_message("You must inform the task id", chat)
        else:
            msg2 = msg.split()
            task_id = int(task_id)
            task = handling_exception(msg, task_id, chat)
            if task == 1:
                return

        task.status = 'TODO'
        db.session.commit()
        Initialization.send_message("*TODO* task [[{}]] {} {}".format(task.id, task.name, task.priority), chat)

def doing(msg, chat):
    for task_id in msg.split(' '):
        if not task_id.isdigit():
            Initialization.send_message("You must inform the task id", chat)
        else:
            msg2 = msg.split()
            task_id = int(task_id)
            task = handling_exception(msg, task_id, chat)
            if task == 1:
                return

        task.status = 'DOING'
        db.session.commit()
        Initialization.send_message("*DOING* task [[{}]] {} {}".format(task.id, task.name, task.priority), chat)

def done(msg, chat):
    for task_id in msg.split(' '):
        if not task_id.isdigit():
            Initialization.send_message("You must inform the task id", chat)
        else:
            msg2 = msg.split()
            task_id = int(task_id)
            task = handling_exception(msg, task_id, chat)
            if task == 1:
                return

        task.status = 'DONE'
        db.session.commit()
        Initialization.send_message("*DONE* task [[{}]] {} {}".format(task.id, task.name, task.priority), chat)

def list(msg, chat):
            a = ''

            a += '\U0001F4CB Task List\n'
            query = db.session.query(Task).filter_by(parents='', chat=chat).order_by(Task.id)
            for task in query.all():
                icon = '\U0001F195'
                if task.status == 'DOING':
                    icon = '\U000023FA'
                elif task.status == 'DONE':
                    icon = '\U00002611'

                a += '[[{}]] {} {} {}\n'.format(task.id, icon, task.name, task.priority)
                a += deps_text(task, chat)

            Initialization.send_message(a, chat)
            a = ''

            a += '\U0001F4DD _Status_\n'
            query = db.session.query(Task).filter_by(status='TODO', chat=chat).order_by(Task.id)
            a += '\n\U0001F195 *TODO*\n'
            for task in query.all():
                a += '[[{}]] {} {}\n'.format(task.id, task.name, task.priority)
            query = db.session.query(Task).filter_by(status='DOING', chat=chat).order_by(Task.id)
            a += '\n\U000023FA *DOING*\n'
            for task in query.all():
                a += '[[{}]] {} {}\n'.format(task.id, task.name, task.priority)
            query = db.session.query(Task).filter_by(status='DONE', chat=chat).order_by(Task.id)
            a += '\n\U00002611 *DONE*\n'
            for task in query.all():
                a += '[[{}]] {} {}\n'.format(task.id, task.name, task.priority)

            Initialization.send_message(a, chat)

def dependson(text, msg, chat):
            if not msg.isdigit():
                Initialization.send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                task = handling_exception(msg,task_id,chat)
                if task == 1:
                    return

                if text == '':
                    for i in task.dependencies.split(',')[:-1]:
                        i = int(i)
                        q = db.session.query(Task).filter_by(id=i, chat=chat)
                        t = q.one()
                        t.parents = t.parents.replace('{},'.format(task.id), '')

                    task.dependencies = ''
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
                                taskdep.parents += str(task.id) + ','
                            except sqlalchemy.orm.exc.NoResultFound:
                                Initialization.send_message("_404_ Task {} not found x.x".format(depid), chat)
                                continue

                            deplist = task.dependencies.split(',')
                            if str(depid) not in deplist:
                                task.dependencies += str(depid) + ','

                db.session.commit()
                Initialization.send_message("Task {} dependencies up to date".format(task_id), chat)

def priority(text, msg, chat):
            if not msg.isdigit():
                Initialization.send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                task = handling_exception(msg,task_id,chat)
                if task == 1:
                    return

                if text == '':
                    task.priority = ''
                    Initialization.send_message("_Cleared_ all priorities from task {}".format(task_id), chat)
                else:
                    if text.lower() not in ['high', 'medium', 'low']:
                        Initialization.send_message("The priority *must be* one of the following: high, medium, low", chat)
                    else:
                        if text.lower() == 'low':
                            task.priority = '\U0001F535'
                        elif text.lower() == 'medium':
                            task.priority = '\U0001F315'
                        else:
                            task.priority = '\U0001F534'

                        Initialization.send_message("*Task {}* priority has priority *{}*".format(task_id, text.lower()), chat)
                db.session.commit()
def start(chat):
            Initialization.send_message("Welcome! Here is a list of things you can do.", chat)
            Initialization.send_message(HELP, chat)

def help(chat):
            Initialization.send_message("Here is a list of things you can do.", chat)
            Initialization.send_message(HELP, chat)

def handle_updates(updates):
    for update in updates["result"]:
        if 'message' in update:
            message = update['message']
        elif 'edited_message' in update:
            message = update['edited_message']
        else:
            print('Can\'t process! {}'.format(update))
            return

        command = message["text"].split(" ", 1)[0]
        msg = ''
        if len(message["text"].split(" ", 1)) > 1:
            msg = message["text"].split(" ", 1)[1].strip()

        chat = message["chat"]["id"]

        print(command, msg, chat)

        if command == '/new':
            Operation.new(msg, chat)

        elif command == '/rename':
            text = ''
            text, msg = msgsplit(text, msg)
            rename(text, msg, chat)

        elif command == '/duplicate':
            duplicate(msg, chat)

        elif command == '/delete':
            delete(msg, chat)

        elif command == '/todo':
            todo(msg, chat)

        elif command == '/doing':
            doing(msg, chat)

        elif command == '/done':
           done(msg, chat)

        elif command == '/list':
            list(msg, chat)

        elif command == '/dependson':
            text = ''
            text, msg = msgsplit(text, msg)
            dependson(text, msg, chat)

        elif command == '/priority':
            text = ''
            text, msg = msgsplit(text, msg)
            priority(text, msg, chat)

        elif command == '/start':
            start(chat)

        elif command == '/help':
            help(chat)

        else:
            Initialization.send_message("I'm sorry dave. I'm afraid I can't do that.", chat)


def main():
    last_update_id = None

    while True:
        print("Updates")
        updates = Initialization.get_updates(last_update_id)

        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)

        time.sleep(0.5)


if __name__ == '__main__':
    main()
