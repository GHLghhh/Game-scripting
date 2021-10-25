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

import game_scripting
import hearthstone.states

import signal
import sys

def signal_handler(sig, frame):
    send_email("Script Stopped Manually")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

def send_email(title='Game Script Failed', error=Exception("No error")):
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
        msgText = MIMEText("{}".format(error))
        msgAlternative.attach(msgText)
        if type(error) == pywintypes.error:
            msgText = MIMEText('Err: {}'.format(error), 'html')
            # Likely not able to capture screenshot
        else:
            msgText = MIMEText('Err: {}<br>Current state screenshot<br><img src="cid:image1"><br>'.format(error), 'html')
            msgAlternative.attach(msgText)
            current_screen = gw.get_current_screenshot()
            current_screen.save("screenshot.jpg")
            with open('screenshot.jpg', 'rb') as fp:
                msgImage = MIMEImage(fp.read())
            msgImage.add_header('Content-ID', '<image1>')
            msgRoot.attach(msgImage)

        with open(log_filename, "rb") as f:
            log = MIMEApplication(f.read(), Name=log_filename)
        log['Content-Disposition'] = 'attachment; filename="{}"'.format(log_filename)
        msgRoot.attach(log)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msgRoot)
        server.close()

if __name__ == "__main__":
    app_name = "炉石传说"
    log_filename = "{}_{}.log".format(app_name, datetime.now().strftime("%m_%d_%Y_%H:%M"))
    logging.basicConfig(filename=log_filename, encoding='utf-8', level=logging.INFO)

    try:
        gw = game_scripting.GameWindow(app_name)
        current_state = hearthstone.states.initialize_states(gw)

        if current_state.is_current_state():
            while current_state is not None:
                try:
                    current_state.act()
                    logging.info("Completed action at '{}'".format(type(current_state).__name__))
                    current_state = current_state.next_state()
                except Exception as err:
                    # Try to reintialize states
                    if "No matching state view is found" in str(err):
                        current_state = hearthstone.states.initialize_states(gw)
                    else:
                        raise err
            raise Exception("End of loop")
        else:
            raise Exception("State matching failed")
    except Exception as err:
        send_email(error=err)
        raise err

        

