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

def msgsplit(text, msg):
        if msg != '':
            if len(msg.split(' ', 1)) > 1:
                text = msg.split(' ', 1)[1]
            msg = msg.split(' ', 1)[0]
        return text, msg

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
            Operation.rename(text, msg, chat)

        elif command == '/duplicate':
            Operation.duplicate(msg, chat)

        elif command == '/delete':
            Operation.delete(msg, chat)

        elif command == '/todo':
            Operation.todo(msg, chat)

        elif command == '/doing':
            Operation.doing(msg, chat)

        elif command == '/done':
            Operation.done(msg, chat)

        elif command == '/list':
            Operation.list(msg, chat)

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
