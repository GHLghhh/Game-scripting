from PIL import ImageGrab
import win32gui, win32con, win32api
import pywintypes
import time

import cv2
import numpy as np
import abc
import random
import logging


def pil_to_cv_image(pil_image):
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


class GameWindow:

    def __init__(self, window_title):
        toplist, winlist = [], []

        def enum_cb(hwnd, results):
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

        win32gui.EnumWindows(enum_cb, toplist)
        matched_list = [
            hwnd for hwnd, title in winlist if window_title == title
        ]
        if len(matched_list) != 1:
            raise Exception("Expected only 1 match for the window title")
        self.hwnd_ = matched_list[0]

    def click(self,
              point,
              is_absolute_position=False,
              right_click=False,
              point_offset_range=None):
        # Introduce variation on point click
        if point_offset_range is not None:
            x_offset = random.randrange(point_offset_range[0]) * random.randint(
                -1, 1)
            y_offset = random.randrange(point_offset_range[1]) * random.randint(
                -1, 1)
            point = (point[0] + x_offset, point[1] + y_offset)
        if not is_absolute_position:
            bbox = self.get_window_coordinate()
            mouse_pos = (bbox[0] + point[0], bbox[1] + point[1])
        else:
            mouse_pos = (point[0], point[1])
        # FIXME PostMessage on mouse event is not responsive
        self.mouse_move(mouse_pos, True)
        if right_click:
            win32api.mouse_event(
                win32con.MOUSEEVENTF_RIGHTDOWN | win32con.MOUSEEVENTF_RIGHTUP |
                win32con.MOUSEEVENTF_ABSOLUTE, mouse_pos[0], mouse_pos[1], 0, 0)
        else:
            win32api.mouse_event(
                win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP |
                win32con.MOUSEEVENTF_ABSOLUTE, mouse_pos[0], mouse_pos[1], 0, 0)

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

    def keyboard(self, key):
        if key == "esc":
            time.sleep(1)
            win32gui.PostMessage(self.hwnd_, win32con.WM_KEYDOWN,
                                 win32con.VK_ESCAPE, 0)
            # win32gui.PostMessage(self.hwnd_, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)
        else:
            raise Exception("Unknown key press requested")

    def get_window_coordinate(self):
        bbox = win32gui.GetWindowRect(self.hwnd_)
        for pos in bbox:
            if pos < 0:
                raise Exception(
                    "Unexpected negative position for window bounding box")
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


class StateMachine(abc.ABC):

    def __init__(self, game_window) -> None:
        self.game_window_ = game_window
        self.current_state_ = None
        self.states_ = []
        self.stale_limit_ = 60
        self.previous_state_ = [0, None]

    def initialize_states(self):
        self.current_state_ = None
        self.previous_state_ = [0, None]
        for state in self.states_:
            if state.is_current_state():
                self.current_state_ = state
                break
        if self.current_state_ is None:
            state_list = ""
            for state in self.states_:
                state_list += (type(state).__name__ + "; ")
            raise Exception(
                "No match for current state, availble states: {}".format(
                    state_list))

    @abc.abstractmethod
    def update_loop_status(self, next_state):
        pass

    @abc.abstractmethod
    def loop_status_string(self):
        return ["No status"]

    def proceed(self):
        if self.current_state_ == self.previous_state_[1]:
            self.previous_state_[0] += 1
            if self.previous_state_[0] >= self.stale_limit_:
                raise Exception(
                    "State '{}' was repeated more than {} times".format(
                        type(self.previous_state_[1]).__name__,
                        self.previous_state_[0]))
        else:
            self.previous_state_ = [0, self.current_state_]
        try:
            self.current_state_.act()
            logging.info("Completed action at '{}'".format(
                type(self.current_state_).__name__))
            next_state = self.current_state_.next_state()
            self.update_loop_status(next_state)
            self.current_state_ = next_state
        except State.StateException as err:
            # Try to reintialize states if state error happens
            self.initialize_states()


class State(abc.ABC):

    class StateException(Exception):

        def __init__(self, *args: object) -> None:
            super().__init__(*args)

    def __init__(self, game_window):
        self.game_window_ = game_window
        # The views that the state correspones to if matches,
        # order implies priority if multiple view are matched
        self.state_view_ = []
        self.next_states_ = []
        self.wait_time_ = 1

    def is_current_state(self):
        try:
            self.get_current_state_view()
            return True
        except State.StateException as err:
            if "No matching state view is found" in str(err):
                return False
            else:
                raise err

    def get_current_state_view(self):
        for i in range(len(self.state_view_)):
            res = self.game_window_.find_matches(self.state_view_[i])
            if len(res) > 0:
                return i, res
        raise State.StateException("No matching state view is found")

    @abc.abstractmethod
    def act(self):
        # some action to take at this state
        pass

    def add_next_state(self, state, prioritized=False):
        if prioritized:
            self.next_states_.insert(0, state)
        else:
            self.next_states_.append(state)

    def next_state(self, wait_time=None):
        retry_count = 60
        for i in range(retry_count):
            time.sleep(wait_time if wait_time is not None else self.wait_time_)
            self.game_window_.mouse_move((0, 0))
            for next_state in self.next_states_:
                if next_state.is_current_state():
                    logging.info("Transit from '{}' to '{}'".format(
                        type(self).__name__,
                        type(next_state).__name__))
                    return next_state
        logging.info("Failed to find next state for '{}'".format(
            type(self).__name__))
        raise State.StateException("Failed to find next state for '{}'".format(
            type(self).__name__))


class MatchAndClickState(State):

    def __init__(self, game_window):
        super().__init__(game_window)

    def act(self):
        _, res = self.get_current_state_view()
        # Get mid point of the match
        lo = res[0][0]
        hi = res[0][1]
        point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
        off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
        self.game_window_.click(point, point_offset_range=off_range)
