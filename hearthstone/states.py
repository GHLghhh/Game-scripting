import cv2
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
        battle_skip_action = BattleSkipAction(self.game_window_)
        battle_end = BattleEnd(self.game_window_)
        treasure = Treasure(self.game_window_)
        retire = Retire(self.game_window_)

        # Simple loop
        start_state.add_next_state(battle)
        battle.add_next_state(battle_end)
        battle.add_next_state(battle_skip_action, True)
        battle_skip_action.add_next_state(battle)
        battle_skip_action.add_next_state(battle_end)
        battle_end.add_next_state(treasure)
        treasure.add_next_state(retire)
        retire.add_next_state(start_state)

        self.states_ = [
            start_state, battle, battle_skip_action, battle_end, treasure,
            retire
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
        battle_skip_action = BattleSkipAction(self.game_window_)
        battle_end = BattleEnd(self.game_window_)
        treasure = Treasure(self.game_window_)
        select_battle = SelectBattle(self.game_window_)
        rewards = ChestRewards(self.game_window_)
        loop_end = ChestRewardsEnd(self.game_window_)

        # Simple loop
        start_state.add_next_state(battle)
        battle.add_next_state(battle_end)
        battle.add_next_state(battle_skip_action, True)
        battle_skip_action.add_next_state(battle)
        battle_skip_action.add_next_state(battle_end)
        battle_end.add_next_state(treasure)

        # WIP
        battle_end.add_next_state(rewards, True)
        rewards.add_next_state(loop_end)
        treasure.add_next_state(select_battle)
        select_battle.add_next_state(start_state, True)
        loop_end.add_next_state(start_state)

        self.states_ = [
            start_state, battle, battle_skip_action, battle_end, treasure,
            select_battle, rewards, loop_end
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
        self.next_states_.append(self)

    def act(self):
        # Hard code ratio of the reward location
        off_ratio = (40 / 870, 35 / 701)
        point_ratio = [(450 / 870, 190 / 701), (186 / 870, 300 / 701),
                       (676 / 870, 330 / 701), (250 / 870, 600 / 701),
                       (610 / 870, 623 / 701)]
        _, res = self.get_current_state_view()
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
            cv2.imread('hearthstone/assets/special_event.jpg'))
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

class SelectBattle(game_scripting.State):

    def __init__(self, game_window):
        super().__init__(game_window)
        # FIXME use file path
        self.state_view_.append(
            cv2.imread('hearthstone/assets/guardian.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/mage.jpg'))
        self.state_view_.append(
            cv2.imread('hearthstone/assets/fighter.jpg'))
        self.next_states_.append(self)
        # Easy for matching in full color
        self.gray_scale_matching_ = False

    def act(self):
        offset = -1
        while offset < len(self.state_view_):
            # There can be inactionable match, check if the action brings it
            # to the next state
            offset, res = self.get_current_state_view(offset+1)
            for (lo, hi) in res:
                # Get lower of the matching point
                point = (int((lo[0] + hi[0]) / 2), int(hi[1] + (hi[1] - lo[1])))
                off_range = (int((hi[0] - lo[0]) / 4), int((hi[1] - lo[1]) / 4))
                self.game_window_.click(point, point_offset_range=off_range)
                if self.next_state() != self:
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
        self.act_view_ = [
            [cv2.imread('hearthstone/assets/act_left.jpg')],
            [cv2.imread('hearthstone/assets/act_right.jpg'),
            cv2.imread('hearthstone/assets/act_right_2.jpg')
            ]
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
            print("here")
            l_list = []
            r_list = []
            for act_view in self.act_view_[0]:
                l_list = self.game_window_.find_matches(act_view)
                if len(l_list) != 0:
                    break
            if len(l_list) == 0:
                print("left")
                raise Exception("Expected at least 1 match for the icon")
            for act_view in self.act_view_[1]:
                r_list = self.game_window_.find_matches(act_view)
                if len(r_list) != 0:
                    break
            if len(r_list) == 0:
                print("right")
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
