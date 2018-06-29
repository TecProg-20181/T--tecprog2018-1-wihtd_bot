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


Initialization = Initialize()
Operation = Operation()

def msgsplit(text, msg):
        if msg != '':
            if len(msg.split(' ', 1)) > 1:
                text = msg.split(' ', 1)[1]
            msg = msg.split(' ', 1)[0]
        return text, msg

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

        elif command == '/senddate':
            text = ''
            text, msg = msgsplit(text, msg)
            Operation.senddate(text, msg, chat)

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
            Operation.dependson(text, msg, chat)

        elif command == '/priority':
            text = ''
            text, msg = msgsplit(text, msg)
            Operation.priority(text, msg, chat)

        elif command == '/start':
            Operation.start(chat)

        elif command == '/help':
            Operation.help(chat)

        else:
            Initialization.send_message("I'm sorry dave. I'm afraid I can't do that.", chat)


def main():
    last_update_id = None

    while True:
        print("Updates")
        updates = Initialization.get_updates(last_update_id)

        if len(updates["result"]) > 0:
            last_update_id = Initialization.get_last_update_id(updates) + 1
            handle_updates(updates)

        time.sleep(0.5)


if __name__ == '__main__':
    main()
