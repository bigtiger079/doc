import shutil
import argparse
import logging
import os
import json

def onStartup(backups):
    for backup in backups:
        shutil.unpack_archive(backup['dest']+'.zip', backup['src'])

def onShutdown(backups):
    for backup in backups:
        shutil.make_archive(backup['dest'], 'zip', backup['src'])   

def read_config(config_file):
    with open(config_file) as file:
        return json.loads(file.read())
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='task on startup or shutdown')

    parser.add_argument('-t', '--type', action='store',
                        choices={'startup','shutdown'}, default='startup', help='startup or shutdown task')

    parser.add_argument('-c', '--config', action='store', type=str, required=True, dest='config_file', help='backup config file path')

    args = parser.parse_args()
    config_file = args.config_file
    
    if not os.path.exists(config_file):
        exit()

    config = read_config(config_file)

    if 'backup' in config:
        backup = config['backup']

        if args.type == 'startup':
            onStartup(backup)
        else:
            onShutdown(backup)
    