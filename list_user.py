"""This script queries telegram and gets all benevoles from channel"""
import re
import datetime
import csv
import os
from pathlib import Path
from dotenv import load_dotenv

# pylint: disable=unused-import
from telethon import TelegramClient, sync

env_path = Path('.') / '.env.local'
load_dotenv(dotenv_path=env_path)

PATH = './export/'
# list of analyzed channel. For an unknown reason, we have to put - 100 in front of it
LIST_CHANNEL_ID = [
    1286842538, # GDB
    1231642142, # Bénévoles
    1266573038, # Bénévoles proches
    1175189547  # Bar
]

client = TelegramClient('labase', os.getenv('API_ID'), os.getenv('API_HASH')).start()

# get all the channels that I can access
channels = {d.entity.username: d.entity
            for d in client.get_dialogs()
            if d.is_channel}

list_channel = []
list_user = {}

for d in client.get_dialogs():
    if d.is_channel:
        # remove - 100 in front of channel id sent back by API.
        CHANNEL_ID = int(str(d.id)[4:])
        if CHANNEL_ID not in LIST_CHANNEL_ID:
            continue

        list_channel.append(d)

        # get all the users
        for p in client.get_participants(d):
            if p.id not in list_user:
                try:
                    was_online = p.status.was_online
                except AttributeError:
                    was_online = datetime.datetime.now()

                first_name = p.first_name or ''
                last_name = p.last_name or ''
                username = p.username or ''
                list_user[p.id] = {
                    'first_name': first_name,
                    'last_name':last_name,
                    'username': username,
                    'id': p.id,
                    'was_online': was_online,
                    'channels': []
                }
                # Remove non characters in channel name
                list_user[p.id].get('channels').append(
                    re.sub(r'[^A-Za-z éàèô]+', '', d.name).strip()
                )

list_user_sorted = sorted(list_user.items(), key = lambda kv:(kv[1].get('first_name'), kv[0]))

for u in list_user_sorted:
    print(
        u[1].get('id'),
        u[1].get('first_name'),
        u[1].get('last_name'),
        u[1].get('was_online').strftime('%d/%m/%Y %H:%M'),
        u[1].get('channels')
    )

print('Found : ' + str(len(list_user_sorted)))
if not os.path.isdir(PATH):
    os.mkdir(PATH)

now = datetime.datetime.now()
with open(PATH+'/benevoles_'+now.strftime('%Y_%m_%d_%H_%M')+'.csv', mode='w') as benevole_file:
    fieldnames = ['id', 'Prénom', 'Nom', 'Date de dernière connexion','Canaux']
    benevole_writer = csv.writer(
        benevole_file,
        delimiter=',',
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL
    )
    benevole_writer.writerow(fieldnames)

    for u in list_user_sorted:
        benevole_writer.writerow([
            u[1].get('id'),
            u[1].get('first_name'),
            u[1].get('last_name'),
            u[1].get('was_online').strftime('%d/%m/%Y %H:%M'),
            u[1].get('channels')
        ])
