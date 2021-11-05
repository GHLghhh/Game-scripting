import cv2
from numpy import character
import game_scripting
import time
import random


class ShortArenaLoop(game_scripting.StateMachine):

    def __init__(self, game_window) -> None:
        super().__init__(game_window)
        self.rewared_received_ = 0
        self.start_time_ = time.time()

        start_state = SelectScreen(self.game_window_)
        searching_opponent = SearchingOpponent(self.game_window_)
        forfeit = Forfeit(self.game_window_, 0.3)
        battle_end = BattleEnd(self.game_window_)
        battle_defeated = BattleDefeated(self.game_window_)
        rewards = ChestRewards(self.game_window_)
        loop_end = ChestRewardsEnd(self.game_window_)

        # FIXME Simple loop is not right, now rewards state
        # must be reached by all states
        start_state.add_next_state(searching_opponent)
        start_state.add_next_state(rewards, True)
        searching_opponent.add_next_state(forfeit)
        forfeit.add_next_state(rewards, True)
        forfeit.add_next_state(battle_end, True)
        forfeit.add_next_state(battle_defeated, True)
        battle_end.add_next_state(start_state)
        battle_end.add_next_state(rewards)
        battle_defeated.add_next_state(start_state)
        battle_defeated.add_next_state(rewards)
        rewards.add_next_state(loop_end)
        loop_end.add_next_state(start_state)

        self.states_ = [
            start_state, searching_opponent, forfeit, battle_end,
            battle_defeated, rewards, loop_end
        ]
        self.initialize_states()

    def update_loop_status(self, next_state):
        retiring = (type(self.current_state_) == ChestRewardsEnd)
        # State changed (reward received)
        if retiring and (type(next_state) != ChestRewardsEnd):
            self.rewared_received_ += 1

    def loop_status_string(self):
        script_duration = int(time.time() - self.start_time_)
        return [
            'Completed runs: {}'.format(self.rewared_received_),
            'Script duration: {} seconds'.format(script_duration)
        ]

    def proceed(self):
        previous_state = self.current_state_
        super().proceed()
        if (type(previous_state) == Forfeit):
            if type(self.current_state_) == BattleDefeated:
                previous_state.adjust_wait_time(increase=True)
            elif type(self.current_state_) == BattleEnd:
                previous_state.adjust_wait_time(reset=True)


class ShortCampaignLoop(game_scripting.StateMachine):

    def __init__(self, game_window) -> None:
        super().__init__(game_window)
        self.rewared_received_ = 0
        self.start_time_ = time.time()

        start_state = SelectScreen(self.game_window_)
        battle = Battle(self.game_window_)
        character_selected = CharacterSelected(self.game_window_)
        battle_skip_action = BattleSkipAction(self.game_window_)
        battle_end = BattleEnd(self.game_window_)
        treasure = Treasure(self.game_window_)
        select_event = SelectEvent(self.game_window_)
        event_selected = EventSelected(self.game_window_)
        retire = Retire(self.game_window_)

        # Simple loop
        start_state.add_next_state(battle)
        battle.add_next_state(battle_end)
        battle.add_next_state(character_selected, True)
        battle.add_next_state(battle_skip_action, True)
        character_selected.add_next_state(battle)
        battle_skip_action.add_next_state(battle)
        battle_skip_action.add_next_state(battle_end)
        battle_end.add_next_state(treasure)
        treasure.add_next_state(retire, True)
        treasure.add_next_state(select_event, True)
        select_event.add_next_state(retire)
        select_event.add_next_state(event_selected, True)
        event_selected.add_next_state(select_event)
        retire.add_next_state(start_state)

        self.states_ = [
            start_state, battle, character_selected, battle_skip_action, battle_end, treasure,
            select_event, event_selected, retire
        ]
        self.initialize_states()

    def update_loop_status(self, next_state):
        retiring = (type(self.current_state_) == Retire)
        # State changed (reward received)
        if retiring and (type(next_state) != Retire):
            self.rewared_received_ += 1

    def loop_status_string(self):
        script_duration = int(time.time() - self.start_time_)
        return [
            'Completed runs: {}'.format(self.rewared_received_),
            'Script duration: {} seconds'.format(script_duration)
        ]


class CampaignLoop(game_scripting.StateMachine):

    def __init__(self, game_window) -> None:
        super().__init__(game_window)
        self.rewared_received_ = 0
        self.start_time_ = time.time()

        start_state = SelectScreen(self.game_window_)
        battle = Battle(self.game_window_)
        character_selected = CharacterSelected(self.game_window_)
        battle_skip_action = BattleSkipAction(self.game_window_)
        battle_end = BattleEnd(self.game_window_)
        treasure = Treasure(self.game_window_)
        select_battle = SelectBattle(self.game_window_)
        rewards = ChestRewards(self.game_window_)
        loop_end = ChestRewardsEnd(self.game_window_)
        select_event = SelectEvent(self.game_window_)
        event_selected = EventSelected(self.game_window_)

        # Simple loop
        start_state.add_next_state(battle)
        battle.add_next_state(battle_end)
        battle.add_next_state(character_selected, True)
        battle.add_next_state(battle_skip_action, True)
        character_selected.add_next_state(battle)
        battle_skip_action.add_next_state(battle)
        battle_skip_action.add_next_state(battle_end)
        battle_end.add_next_state(treasure)

        # WIP
        battle_end.add_next_state(rewards, True)
        rewards.add_next_state(loop_end)
        treasure.add_next_state(start_state)
        treasure.add_next_state(select_event)
        treasure.add_next_state(select_battle)
        select_event.add_next_state(select_battle)
        select_event.add_next_state(event_selected, True)
        event_selected.add_next_state(select_event)
        event_selected.add_next_state(select_battle)
        select_battle.add_next_state(start_state, True)
        loop_end.add_next_state(start_state)

        self.states_ = [
            start_state, battle, character_selected, battle_skip_action, battle_end, treasure,
            select_event, event_selected, select_battle, rewards, loop_end
        ]
        self.initialize_states()

    def update_loop_status(self, next_state):
        retiring = (type(self.current_state_) == ChestRewardsEnd)
        # State changed (reward received)
        if retiring and (type(next_state) != ChestRewardsEnd):
            self.rewared_received_ += 1

    def loop_status_string(self):
        script_duration = int(time.time() - self.start_time_)
        return [
            'Completed runs: {}'.format(self.rewared_received_),
            'Script duration: {} seconds'.format(script_duration)
        ]


class ChestRewards(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/arena_rewards.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/rewards_3.jpg'))
        self.next_states_.append(self)

    def act(self):
        i, res = self.get_current_state_view()
        # Hard code ratio of the reward location
        if i == 0:
            template_x = 870
            template_y = 701
            off_ratio = (40 / template_x, 35 / template_y)
            point_ratio = [(450 / template_x, 190 / template_y), (186 / template_x, 300 / template_y),
                            (676 / template_x, 330 / template_y), (250 / template_x, 600 / template_y),
                            (610 / template_x, 623 / template_y)]
        elif i == 1:
            template_x = 782
            template_y = 589
            off_ratio = (50 / 782, 35 / 589)
            point_ratio = [(395 / template_x, 125 / template_y), (175 / template_x, 470 / template_y),
                            (630 / template_x, 480 / template_y)]

        lo = res[0][0]
        hi = res[0][1]
        full_x = hi[0] - lo[0]
        full_y = hi[1] - lo[1]

        off_range = (int(off_ratio[0] * full_x), int(off_ratio[1] * full_y))
        points = [(int(pr[0] * full_x + lo[0]), int(pr[1] * full_y + lo[1]))
                  for pr in point_ratio]
        random.shuffle(points)
        print(points)
        print(lo)
        print(hi)
        for point in points:
            time.sleep(1)
            self.game_window_.click(point, point_offset_range=off_range)


class ChestRewardsEnd(game_scripting.MatchAndClickState):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(cv2.imread('hearthstone/assets/confirm.jpg'))
        self.state_view_.append(cv2.imread('hearthstone/assets/confirm_2.jpg'))
        self.state_view_.append(cv2.imread('hearthstone/assets/confirm_3.jpg'))
        self.state_view_.append(cv2.imread('hearthstone/assets/confirm_4.jpg'))
        self.next_states_.append(self)


class SearchingOpponent(game_scripting.MatchAndClickState):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/searching_opponent.jpg'))
        self.next_states_.append(self)


class Forfeit(game_scripting.MatchAndClickState):

    def __init__(self, game_window, default_wait_time=0.5):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(cv2.imread('hearthstone/assets/forfeit.jpg'))
        self.state_view_.append(cv2.imread('hearthstone/assets/options.jpg'))
        self.next_states_.append(self)
        self.wait_time_ = default_wait_time
        self.default_wait_time_ = default_wait_time

    def adjust_wait_time(self, increase=False, reset=False):
        if increase:
            self.wait_time_ += self.default_wait_time_
        if reset:
            self.wait_time_ = self.default_wait_time_


class SelectScreen(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/battle_icon.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/arena_battle.jpg'))
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

class EventSelected(game_scripting.State):
    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/revive_prompt.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/power_up_prompt.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/stranger_top.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/special_event_prompt.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/special_event_prompt_2.jpg'))
        self.view_ = [
            cv2.imread('hearthstone/assets/stranger_top.jpg'),
            cv2.imread('hearthstone/assets/stranger_bottom.jpg')
        ]
        self.next_states_.append(self)

    def act(self):
        i, res = self.get_current_state_view()
        print(i)
        if i != 2:
            # Get mid point of the match
            lo = res[0][0]
            hi = res[0][1]
            point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
            off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
            # Right click if at selecting enemy
            self.game_window_.click(point, point_offset_range=off_range)

            # Wait for animation and click again to normalize
            time.sleep(1)
            self.game_window_.click(point, point_offset_range=off_range)
            time.sleep(4 if i == 0 else 2)
        else:
            off = 0
            tres = self.game_window_.find_matches(self.view_[off])
            if len(tres) == 0:
                raise Exception("Expected at least 1 match for the icon")
            bres = self.game_window_.find_matches(self.view_[1 + off])
            if len(bres) == 0:
                raise Exception("Expected at least 1 match for the icon")
            # Define point for the action
            y = int((tres[0][1][1] + bres[0][0][1]) / 2)
            x = int((bres[0][0][0] + bres[0][1][0]) / 2)
            self.game_window_.click((x, y))

            # Get mid point of the match
            time.sleep(1)
            lo = bres[0][0]
            hi = bres[0][1]
            point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
            off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
            self.game_window_.click(point, point_offset_range=off_range)
            time.sleep(1)
            self.game_window_.click(point, point_offset_range=off_range)
            time.sleep(3)


class SelectEvent(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/special_event.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/power_up.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/revive.jpg'))
        self.next_states_.append(self)

    def act(self):
        offset = -1
        while offset < len(self.state_view_):
            # There can be inactionable match, check if the action brings it
            # to the next state
            try:
                offset, res = self.get_current_state_view(offset+1)
            except game_scripting.State.StateException as ex:
                if "No matching state view is found" in str(ex):
                    return
            last_point = None
            for (lo, hi) in res:
                # Get mid point of the match
                point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
                off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
                # Check if the point refers to the same spot
                if last_point is not None:
                    in_x = ((point[0] > last_point[0][0]) and (point[0] < last_point[1][0]))
                    in_y = ((point[1] > last_point[0][1]) and (point[1] < last_point[1][1]))
                    if in_x and in_y:
                        continue
                last_lo = (point[0] - off_range[0], point[1] - off_range[1])
                last_hi = (point[0] + off_range[0], point[1] + off_range[1])
                last_point = (last_lo, last_hi)
                self.game_window_.click(point, point_offset_range=off_range)
                if super().next_state(wait_time=0.3) != self:
                    return

    def next_state(self, wait_time=None, ignore_self=True):
        return super().next_state(wait_time=wait_time, ignore_self=True)

class SelectBattle(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/fighter.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/guardian.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/mage.jpg'))
        self.next_states_.append(self)
        # Easy for matching in full color
        self.gray_scale_matching_ = False

    def act(self):
        offset = -1
        while offset < len(self.state_view_):
            # There can be inactionable match, check if the action brings it
            # to the next state
            try:
                offset, res = self.get_current_state_view(offset+1)
            except game_scripting.State.StateException as ex:
                if "No matching state view is found" in str(ex):
                    return
            last_point = None
            for (lo, hi) in res:
                # Get lower of the matching point
                point = (int((lo[0] + hi[0]) / 2), int(hi[1] + (hi[1] - lo[1])))
                off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
                # Check if the point refers to the same spot
                if last_point is not None:
                    in_x = ((point[0] > last_point[0][0]) and (point[0] < last_point[1][0]))
                    in_y = ((point[1] > last_point[0][1]) and (point[1] < last_point[1][1]))
                    if in_x and in_y:
                        continue
                last_lo = (point[0] - off_range[0], point[1] - off_range[1])
                last_hi = (point[0] + off_range[0], point[1] + off_range[1])
                last_point = (last_lo, last_hi)
                self.game_window_.click(point, point_offset_range=off_range)
                if super().next_state(wait_time=0.3) != self:
                    return


class Battle(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(cv2.imread('hearthstone/assets/idle_icon.jpg'))
        self.state_view_.append(cv2.imread('hearthstone/assets/act_left.jpg'))
        self.state_view_.append(cv2.imread('hearthstone/assets/ready_icon.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/prepare_icon.jpg'))
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
            # Do nothing, should transition to the other state
            pass

class CharacterSelected(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(cv2.imread('hearthstone/assets/act_left.jpg'))
        self.characters_ = [
            (cv2.imread('hearthstone/assets/char_rag.jpg'), [(cv2.imread('hearthstone/assets/char_rag_skill_2.jpg'), self.simple_click)]),
            (cv2.imread('hearthstone/assets/char_house.jpg'), [(cv2.imread('hearthstone/assets/char_house_skill_1.jpg'), self.simple_click)]),
            (cv2.imread('hearthstone/assets/char_wal.jpg'), [(cv2.imread('hearthstone/assets/char_wal_skill_1.jpg'), self.simple_click)]),
            (cv2.imread('hearthstone/assets/char_tregx.jpg'), [(cv2.imread('hearthstone/assets/char_tregx_skill_1.jpg'), self.simple_click)]),
        ]
        self.next_states_.append(self)

    # Additional logic to define how to cast the skill
    def simple_click(self, res):
        # Click the mid point of the match
        lo = res[0][0]
        hi = res[0][1]
        point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
        off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
        self.game_window_.click(point, point_offset_range=off_range)

    def act(self):
        current_screenshot = self.game_window_.get_current_screenshot()
        for char, skills in self.characters_:
            res = self.game_window_.find_matches(char, img_rgb=current_screenshot)
            if len(res) != 0:
                for skill, action in skills:
                    res = self.game_window_.find_matches(skill, img_rgb=current_screenshot)
                    if len(res) != 0:
                        action(res)
                        return
        raise game_scripting.State.StateException("Failed to find proper action for selected charactor")


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


class BattleEnd(game_scripting.MatchAndClickState):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/click_prompt.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/click_prompt_2.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/victory.jpg'))
        self.next_states_.append(self)


class BattleDefeated(game_scripting.MatchAndClickState):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(cv2.imread('hearthstone/assets/defeated.jpg'))
        self.next_states_.append(self)


class Treasure(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/treasure_top.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/treasure_top_2.jpg'))
        self.view_ = [
            cv2.imread('hearthstone/assets/treasure_top.jpg'),
            cv2.imread('hearthstone/assets/treasure_bottom.jpg'),
            cv2.imread('hearthstone/assets/treasure_top_2.jpg'),
            cv2.imread('hearthstone/assets/treasure_bottom_2.jpg'),
        ]
        self.next_states_.append(self)

    def act(self):
        # Check which substate the current state is at
        i, _ = self.get_current_state_view()
        off = int(2 * i)
        tres = self.game_window_.find_matches(self.view_[off])
        if len(tres) == 0:
            raise Exception("Expected at least 1 match for the icon")
        bres = self.game_window_.find_matches(self.view_[1 + off])
        if len(bres) == 0:
            raise Exception("Expected at least 1 match for the icon")
        # Define point for the action
        y = int((tres[0][1][1] + bres[0][0][1]) / 2)
        x = int((bres[0][0][0] + bres[0][1][0]) / 2)
        self.game_window_.click((x, y))

        # Get mid point of the match
        time.sleep(1)
        lo = bres[0][0]
        hi = bres[0][1]
        point = (int((lo[0] + hi[0]) / 2), int((lo[1] + hi[1]) / 2))
        off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
        self.game_window_.click(point, point_offset_range=off_range)
        time.sleep(2)


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
