import cv2
import game_scripting
import time


class SelectScreen(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/battle_icon.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/select_icon.jpg'))
        self.next_states_.append(self)

    def act(self):
        _, res = self.get_current_state_view()
        # Get mid point of the match
        lo = res[0][0]
        hi = res[0][1]
        point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
        off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
        self.game_window_.click(point, point_offset_range=off_range)


class Battle(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(cv2.imread('hearthstone/assets/idle_icon.jpg'))
        self.state_view_.append(cv2.imread('hearthstone/assets/act_left.jpg'))
        self.state_view_.append(cv2.imread('hearthstone/assets/ready_icon.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/prepare_icon.jpg'))
        self.act_view_ = [
            cv2.imread('hearthstone/assets/act_left.jpg'),
            cv2.imread('hearthstone/assets/act_right.jpg')
        ]
        self.next_states_.append(self)

    def act(self):
        i, res = self.get_current_state_view()
        if i > 1:
            # Get mid point of the match
            lo = res[0][0]
            hi = res[0][1]
            point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
            off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
            self.game_window_.click(point, point_offset_range=off_range)
        elif i == 0:
            # idle
            # Get bottom-left point of the match
            self.game_window_.click((res[0][0][0], res[0][1][1]))
        else:
            l_list = self.game_window_.find_matches(self.act_view_[0])
            if len(l_list) == 0:
                raise Exception("Expected at least 1 match for the icon")
            r_list = self.game_window_.find_matches(self.act_view_[1])
            if len(r_list) == 0:
                raise Exception("Expected at least 1 match for the icon")
            # Define bounding box for the actions
            lo = (l_list[0][1][0], l_list[0][0][1])
            hi = (r_list[0][0][0], r_list[0][1][1])
            # Define points for three actions
            y = int((hi[1] + lo[1]) / 2)
            x_off = int((hi[0] - lo[0]) / 3)
            x = lo[0] + int(x_off / 2)
            action_points = [(x, y), (x + x_off, y), (x + 2 * x_off, y)]
            # FIXME only select the first action for now
            self.game_window_.click(action_points[0])


class BattleSkipAction(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/select_enemy_2.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/select_enemy.jpg'))
        # This is part of the joint action, not included as state view
        self.ready_template_ = cv2.imread('hearthstone/assets/ready_icon_2.jpg')

    def act(self):
        _, res = self.get_current_state_view()
        # Get mid point of the match
        lo = res[0][0]
        hi = res[0][1]
        point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
        off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
        # Right click if at selecting enemy
        self.game_window_.click(point,
                                right_click=True,
                                point_offset_range=off_range)

        # Wait for animation
        time.sleep(2)
        res = self.game_window_.find_matches(self.ready_template_)
        if len(res) == 0:
            raise Exception("No matching state view is found")
        # Get mid point of the match
        lo = res[0][0]
        hi = res[0][1]
        point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
        off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
        self.game_window_.click(point, point_offset_range=off_range)


class BattleEnd(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/click_prompt.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/click_prompt_2.jpg'))
        self.next_states_.append(self)

    def act(self):
        _, res = self.get_current_state_view()
        # Get mid point of the match
        lo = res[0][0]
        hi = res[0][1]
        point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
        off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
        self.game_window_.click(point, point_offset_range=off_range)


class Treasure(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/treasure_top.jpg'))
        self.unselected_view_ = [
            cv2.imread('hearthstone/assets/treasure_top.jpg'),
            cv2.imread('hearthstone/assets/treasure_bottom.jpg')
        ]
        self.selected_view_ = cv2.imread(
            'hearthstone/assets/treasure_selected.jpg')
        self.next_states_.append(self)

    def act(self):
        # Check which substate the current state is at
        res = self.game_window_.find_matches(self.selected_view_)
        if len(res) > 0:
            # Get mid point of the match
            lo = res[0][0]
            hi = res[0][1]
            point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
            off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
            self.game_window_.click(point, point_offset_range=off_range)
        else:
            tres = self.game_window_.find_matches(self.unselected_view_[0])
            if len(tres) == 0:
                raise Exception("Expected at least 1 match for the icon")
            bres = self.game_window_.find_matches(self.unselected_view_[1])
            if len(bres) == 0:
                raise Exception("Expected at least 1 match for the icon")
            # Define point for the action
            y = int((tres[0][1][1] + bres[0][0][1]) / 2)
            x = int((bres[0][0][0] + bres[0][1][0]) / 2)
            self.game_window_.click((x, y))


class Retire(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        # Order implies priority
        self.state_view_.append(cv2.imread('hearthstone/assets/rewards.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/confirm_retire.jpg'))
        self.state_view_.append(cv2.imread('hearthstone/assets/retire.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/check_team_status.jpg'))
        self.next_states_.append(self)

    def act(self):
        # Check which substate the current state is at
        _, res = self.get_current_state_view()
        # Click the mid point of the match, same for all views
        lo = res[0][0]
        hi = res[0][1]
        point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
        off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
        self.game_window_.click(point, point_offset_range=off_range)


def initialize_states(game_window):
    start_state = SelectScreen(game_window)
    battle = Battle(game_window)
    battle_skip_action = BattleSkipAction(game_window)
    battle_end = BattleEnd(game_window)
    treasure = Treasure(game_window)
    retire = Retire(game_window)

    # Simple loop
    start_state.add_next_state(battle)
    battle.add_next_state(battle_end)
    battle.add_next_state(battle_skip_action, True)
    battle_skip_action.add_next_state(battle)
    battle_skip_action.add_next_state(battle_end)
    battle_end.add_next_state(treasure)
    treasure.add_next_state(retire)
    retire.add_next_state(start_state)

    # Match current state
    if start_state.is_current_state():
        return start_state
    elif battle.is_current_state():
        return battle
    elif battle_end.is_current_state():
        return battle_end
    elif treasure.is_current_state():
        return treasure
    elif retire.is_current_state():
        return retire
    return None
