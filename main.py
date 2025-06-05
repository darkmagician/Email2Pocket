from imap_tools import MailBox
from config import settings
import pocket
import config
import logging
import requests
import time
import threading
import wallabag

logger = logging.getLogger(__name__)


# https://pypi.org/project/imap-tools/


def processLink(subject, link):
    logger.info(f"processLink  {subject}-{link}")
    if pocket.isEnabled():
        pocket.addLink(link, subject, ['wechat'])
    if wallabag.isEnabled():
        wallabag.addLink(link, subject, ['wechat'])
    return True


# def listFolders(mailbox, folder='', level=0):
#     current_folder = mailbox.folder.get()
#     logger.info(f"list {current_folder}")
#     if folder:
#         mailbox.folder.set(folder)
#     logger.info(f"list {folder}")
#     for f in mailbox.folder.list(folder):
#         logger.info(f"=>folder {f}")

#         if level > 1:
#             continue
#         listFolders(mailbox, f.name, level + 1)
#     mailbox.folder.set(current_folder)


def check():
    mailcfg = settings['mail']
    inbox = mailcfg['inbox']
    processsed = mailcfg['processsed']
    imap_host = mailcfg['imap_host']
    imap_user = mailcfg['imap_user']
    imap_pass = mailcfg['imap_pass']
    idle_interval = mailcfg['idle_interval']
    idle_max = 1 + mailcfg['idle_max_time'] // idle_interval
    sleep_sec = mailcfg['error_interval']
    while True:
        try:

            with MailBox(imap_host).login(imap_user, imap_pass) as mailbox:
                # listFolders(mailbox)
                while True:
                    logger.info("checking mailbox")
                    for msg in mailbox.fetch():
                        subject = msg.subject
                        link = msg.text
                        mid = msg.uid
                        logger.info(f"Found mail {msg.date} {mid} {subject}/{link}")
                        if processLink(subject, link):
                            mailbox.move(mid, processsed)
                            logger.info(f"mail {mid} is processed")
                        else:
                            logger.info(f"mail {mid} is not processed")
                    for x in range(idle_max):
                        responses = mailbox.idle.wait(timeout=idle_interval)
                        if responses:
                            logger.info("update is found.")
                            break

        except Exception as e:
            logging.error(e, exc_info=True)

        logger.info(f"sleep for {sleep_sec} seconds")
        time.sleep(sleep_sec)


if __name__ == '__main__':
    t = threading.Thread(target=check)
    t.start()
    pocket.startServer()
