from PIL import ImageGrab
import win32gui, win32con, win32api
import pywintypes
import time

import cv2
import numpy as np
import abc

def pil_to_cv_image(pil_image):
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

class GameWindow:
    def __init__(self, window_title):
        toplist, winlist = [], []
        def enum_cb(hwnd, results):
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
        win32gui.EnumWindows(enum_cb, toplist)
        matched_list = [hwnd for hwnd, title in winlist if window_title == title]
        if len(matched_list) != 1:
            raise Exception("Expected only 1 match for the window title")
        self.hwnd_ = matched_list[0]

    def click(self, point, is_absolute_position=False):
        if not is_absolute_position:
            bbox = self.get_window_coordinate()
            mouse_pos = (bbox[0] + point[0], bbox[1] + point[1])
        else:
            mouse_pos = (point[0], point[1])
        # FIXME PostMessage on mouse event is not responsive
        self.mouse_move(mouse_pos, True)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_ABSOLUTE, mouse_pos[0], mouse_pos[1],0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_ABSOLUTE, mouse_pos[0], mouse_pos[1],0,0)

    def mouse_move(self, point, is_absolute_position=False):
        if not is_absolute_position:
            bbox = self.get_window_coordinate()
            mouse_pos = (bbox[0] + point[0], bbox[1] + point[1])
        else:
            mouse_pos = (point[0], point[1])
        
        # FIXME sometimes there is unexpected Windows API error
        try:
            win32api.SetCursorPos(mouse_pos)
        except pywintypes.error as err:
            retry_count = 3
            for i in range(retry_count):
                time.sleep(5)
                try:
                    win32api.SetCursorPos(mouse_pos)
                except pywintypes.error as err:
                    continue

    def _keyboard(self, point, absolute_position=False):
        if absolute_position:
            bbox = self.get_window_coordinate()
            mouse_pos = win32api.MAKELONG(bbox[0] + point[0], bbox[1] + point[1])
        else:
            mouse_pos = win32api.MAKELONG(point[0], point[1])
        win32gui.PostMessage(self.hwnd_, win32con.WM_KEYDOWN, 0x4A, 0)
        time.sleep(1)
        win32gui.PostMessage(self.hwnd_, win32con.WM_KEYUP, 0x4A, 0)

    def get_window_coordinate(self):
        bbox = win32gui.GetWindowRect(self.hwnd_)
        for pos in bbox:
            if pos < 0:
                raise Exception("Unexpected negative position for window bounding box")
        return bbox

    def get_current_screenshot(self):
        # FIXME resolution setting will affect bbox axis on some appllications
        # which will result in partially capture
        # FIXME multiple calls to SetForegroundWindow() returns unexpected
        # error, now check foreground to avoid multiple calls
        if (win32gui.GetForegroundWindow() != self.hwnd_):
            win32gui.SetForegroundWindow(self.hwnd_)
        bbox = win32gui.GetWindowRect(self.hwnd_)
        return ImageGrab.grab(bbox, all_screens=True)

    # Return a list of point pairs that define the matching rectangles in the
    # current screenshot
    # FIXME template is no scalable for now
    def find_matches(self, template, to_gray_scale=True):
        # https://stackoverflow.com/a/35378944
        img_rgb = pil_to_cv_image(self.get_current_screenshot())
        if to_gray_scale:
            img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            w, h = template.shape
        else:
            w, h = template.shape[:-1]

        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        threshold = .8
        loc = np.where(res >= threshold)
        res_list = []
        for pt in zip(*loc[::-1]):  # Switch collumns and rows
            res_list.append((pt, (pt[0] + h, pt[1] + w)))
        return res_list


class State(abc.ABC):
    def __init__(self, game_window):
        self.game_window_ = game_window
        # The views that the state correspones to if matches,
        # order implies priority if multiple view are matched
        self.state_view_ = []
        self.next_states_ = []

    def is_current_state(self):
        try:
            _, res = self.get_current_state_view()
            return True
        except Exception as err:
            return False

    def get_current_state_view(self):
        retry_count = 3
        for k in range(retry_count):
            for i in range(len(self.state_view_)):
                res = self.game_window_.find_matches(self.state_view_[i])
                if len(res) > 0:
                    return i, res
            time.sleep(1)
        raise Exception("No matching state view is found")

    @abc.abstractmethod
    def act(self):
        # some action to take at this state
        pass

    def add_next_state(self, state):
        self.next_states_.append(state)

    def next_state(self, wait_time=1):
        retry_count = 10
        for i in range(retry_count):
            time.sleep(wait_time)
            self.game_window_.mouse_move((0,0))
            for next_state in self.next_states_:
                if next_state.is_current_state():
                    return next_state
        return None