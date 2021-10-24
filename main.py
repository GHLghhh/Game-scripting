import sys
import os
import pathlib
import cv2
import time
import pywintypes
import win32api
import os

import game_scripting
import hearthstone.states

if __name__ == "__main__":
    try:
        gw = game_scripting.GameWindow("炉石传说")
        current_state = hearthstone.states.initialize_states(gw)

        print(current_state.is_current_state())
        if current_state.is_current_state():
            while current_state is not None:
                try:
                    current_state.act()
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
        print(err)
        import smtplib
        from email import encoders
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email.mime.image import MIMEImage

        gmail_user = os.environ['GMAIL_USER']
        gmail_password = os.environ['GMAIL_PASSWORD']

        # Set email content https://stackoverflow.com/a/60174103
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = 'Game Script Failed'
        msgRoot['From'] = gmail_user
        msgRoot['To'] = gmail_user
        msgRoot.preamble = 'Multi-part message in MIME format.'
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        msgText = MIMEText("{}".format(err))
        msgAlternative.attach(msgText)
        if type(err) == pywintypes.error:
            msgText = MIMEText('Err: {}'.format(err), 'html')
            # Likely not able to capture screenshot
        else:
            msgText = MIMEText('Err: {}<br>Current state screenshot<br><img src="cid:image1"><br>'.format(err), 'html')
            msgAlternative.attach(msgText)
            current_screen = gw.get_current_screenshot()
            current_screen.save("screenshot.jpg")
            with open('screenshot.jpg', 'rb') as fp:
                msgImage = MIMEImage(fp.read())
            msgImage.add_header('Content-ID', '<image1>')
            msgRoot.attach(msgImage)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.send_message(msgRoot)
        server.close()
        raise err

        

