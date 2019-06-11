import shutil
import argparse
import logging
import os
import sys
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# 还原备份文件
def onStartup(backups):
    for backup in backups:
        try:
            logger.info("start restore %s to %s" % (backup['dest']+'.zip', backup['src']))
            shutil.unpack_archive(backup['dest']+'.zip', backup['src'])
        except Exception as identifier:
            logger.error(identifier)


# 备份配置文件
def onShutdown(backups):
    for backup in backups:
        try:
            logger.info("start backup %s to %s" % (backup['dest']+'.zip', backup['src']))
            shutil.make_archive(backup['dest'], 'zip', backup['src'])
        except Exception as identifier:
            logger.error(identifier)


def onHandleLinks(links, isBackup=True):
    desktopDir = links['deskDir']
    storeDir = links['storeDir']
    if not os.path.exists(desktopDir) or not os.path.exists(storeDir):
        return
    logger.info("On Handle Links, from %s to %s" % (desktopDir if isBackup else storeDir, storeDir if isBackup else desktopDir))
    dest = []
    src = []
    for dirpath, dirnames, filenames in os.walk(desktopDir):
        for filename in filenames:
            if isBackup:
                src.append(filename)
            else:
                dest.append(filename)

    for dirpath, dirnames, filenames in os.walk(storeDir):
        for filename in filenames:
            if isBackup:
                dest.append(filename)
            else:
                src.append(filename)

    tmp = []
    for link in src:
        if link not in dest:
            tmp.append(link)

    if len(tmp) > 0:
        for link in tmp:
            if isBackup:
                shutil.copyfile(os.path.join(desktopDir, link), os.path.join(storeDir, link))
            else:
                shutil.copyfile(os.path.join(storeDir, link), os.path.join(desktopDir, link))


def read_config(config_file):
    with open(config_file) as file:
        return json.loads(file.read())
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='task on startup or shutdown')

    parser.add_argument('-t', '--type', action='store',
                        choices={'startup', 'shutdown'}, default='startup', help='startup or shutdown task')

    parser.add_argument('-c', '--config', action='store', type=str, required=True, dest='config_file', help='backup config file path')

    args = parser.parse_args()
    config_file = args.config_file

    if not os.path.exists(config_file):
        logger.error("config file: %s not exists" % config_file)
        sys.exit(0)

    logger.info("read config: %s" % config_file)
    config = read_config(config_file)

    if 'backup' in config:
        logger.info("start handle backup")
        backup = config['backup']

        if args.type == 'startup':
            onStartup(backup)
        else:
            onShutdown(backup)

    if 'links' in config:
        logger.info("start handle links")
        links = config['links']
        onHandleLinks(links, args.type != 'startup')
