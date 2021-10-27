import sys
import os
import pathlib
import cv2
import time
import pywintypes
import win32api
import os
import logging
from datetime import datetime

from win32gui import RedrawWindow

import game_scripting
import hearthstone.states

import signal
import sys

LOOP_OBJECT = None


def signal_handler(sig, frame):
    send_email("Script Stopped Manually")
    exit(0)


signal.signal(signal.SIGINT, signal_handler)


def send_email(title='Game Script Failed', error=Exception("No error")):
    if LOOP_OBJECT is not None:
        for status_string in LOOP_OBJECT.loop_status_string():
            print(status_string)
    print('Err: {}'.format(error))

    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    if (gmail_user is not None) and (gmail_password is not None):
        import smtplib
        from email import encoders
        from email.mime.multipart import MIMEMultipart
        from email.mime.application import MIMEApplication
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email.mime.image import MIMEImage

        # Set email content https://stackoverflow.com/a/60174103
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = title
        msgRoot['From'] = gmail_user
        msgRoot['To'] = gmail_user
        msgRoot.preamble = 'Multi-part message in MIME format.'
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        content = ""
        if LOOP_OBJECT is not None:
            for status_string in LOOP_OBJECT.loop_status_string():
                content += "{}<br>".format(status_string)
        content += "Err: {}<br>".format(error)
        if type(error) != pywintypes.error:
            content += '<br>Current state screenshot<br><img src="cid:image1"><br>'
            current_screen = gw.get_current_screenshot()
            current_screen.save("screenshot.jpg")
            with open('screenshot.jpg', 'rb') as fp:
                msgImage = MIMEImage(fp.read())
            msgImage.add_header('Content-ID', '<image1>')
            msgRoot.attach(msgImage)
        msgText = MIMEText(content, 'html')
        msgAlternative.attach(msgText)

        with open(log_filename, "rb") as f:
            log = MIMEApplication(f.read(), Name=log_filename)
        log['Content-Disposition'] = 'attachment; filename="{}"'.format(
            log_filename)
        msgRoot.attach(log)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msgRoot)
        server.close()


if __name__ == "__main__":
    app_name = "炉石传说"
    log_filename = "{}_{}.log".format(app_name,
                                      datetime.now().strftime("%m_%d_%Y_%H_%M"))
    logging.basicConfig(filename=log_filename,
                        encoding='utf-8',
                        level=logging.INFO)

    try:
        gw = game_scripting.GameWindow(app_name)
        # LOOP_OBJECT = hearthstone.states.ShortCampaignLoop(gw)
        LOOP_OBJECT = hearthstone.states.ShortArenaLoop(gw)

        while True:
            LOOP_OBJECT.proceed()
    except Exception as err:
        send_email(error=err)
        raise err
