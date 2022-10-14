from template import Agent
import random
from Splendor.splendor_model import SplendorGameRule
from copy import deepcopy
import heapq
import time
from Splendor.splendor_model import *
from Splendor.splendor_utils import *
import collections

time_allow = 0.90
num_of_agent = 2


def Cost(state, action, agent_id):
    cost = 0
    noble_cost = 0
    game_state = deepcopy(state)
    agent_state = game_state.agents[agent_id]
    board_state = game_state.board
    strategy = Card_Strategy(board_state)

    current_card_costs = []
    gem_type = ['black', 'red', 'green', 'blue', 'white']
    for temp_card in board_state.dealt_list():
        temp_card_name = temp_card.__repr__()
        cost_list = [0, 0, 0, 0, 0]
        for i in list(CARDS[temp_card_name][1].keys()):
            cost_list[gem_type.index(i)] = CARDS[temp_card_name][1][i]
        current_card_costs.append(cost_list)

    current_gems = list(agent_state.gems.values())
    current_gems.pop(2)
    current_yellow_gems = list(agent_state.gems.values())[2]

    current_resources = []
    temp_keys_list = list(agent_state.gems.keys())
    temp_keys_list.pop(2)
    for i in list(temp_keys_list):
        current_resources.append(len(list(agent_state.cards[i])))

    if 'buy_available' in action['type']:
        card_name = action['card'].__repr__()
        card_point = CARDS[card_name][-1]
        card_id = CARDS[card_name][2]
        card_cost = list(action['returned_gems'].values())
        if sum(card_cost) == 0:
            if card_id == 1:
                cost = -9
            elif card_id == 2:
                cost = -99
            elif card_id == 3:
                cost = -999
        else:
            weight = (1 + card_point) / sum(card_cost)
            cost = 5 * weight * (1 / sum(card_cost) + card_point**2 / sum(card_cost) - sum(card_cost))

            if CARDS[card_name][0] in strategy:
                index_reward = [1.4, 1.3, 1.2, 1.1]
                index_val = strategy.index(CARDS[card_name][0])
                cost = cost * index_reward[index_val]

            if (agent_state.score + card_point) >= 15:
                cost = -99999

        if action['noble'] != 'None':
            noble_cost = -999

    elif 'buy_reserve' in action['type']:
        card_name = action['card'].__repr__()
        card_point = CARDS[card_name][-1]
        card_id = CARDS[card_name][2]
        card_cost = list(action['returned_gems'].values())
        if sum(card_cost) == 0:
            if card_id == 1:
                cost = -9
            elif card_id == 2:
                cost = -99
            elif card_id == 3:
                cost = -999
        else:
            weight = (1 + card_point) / sum(card_cost)
            cost = 10 * weight * (1 / sum(card_cost) + card_point ** 2 / sum(card_cost) - sum(card_cost))
            if (agent_state.score + card_point) >= 15:
                cost = -99999

        if action['noble'] != 'None':
            noble_cost = -999

    else:
        temp_cost = []
        returned_gems = [0, 0, 0, 0, 0]
        if 'returned_gems' in action.keys():
            for i in list(action['returned_gems'].keys()):
                if i != 'yellow':
                    returned_gems[gem_type.index(i)] = - (action['returned_gems'][i])
        if 'reserve' in action['type']:
            temp_list = [current_gems, current_resources, returned_gems]
            card_name = action['card'].__repr__()
            cost_list = [0, 0, 0, 0, 0]
            temp_cost_list = CARDS[card_name][1]
            for i in list(temp_cost_list.keys()):
                cost_list[gem_type.index(i)] = CARDS[card_name][1][i]
            current_agent_resources = [sum(x) for x in zip(*temp_list)]
            current_cost = [m - n for m, n in zip(current_agent_resources, cost_list)]
            for j in current_cost:
                if j > 0:
                    current_cost[current_cost.index(j)] = 0
                elif j < 0:
                    current_cost[current_cost.index(j)] = -j
            temp_cost.append(sum(current_cost) - 1 - current_yellow_gems + sum(returned_gems))
            cost = min(temp_cost)

            if agent_id == 0:
                opponent_id = 1
            else:
                opponent_id = 0

            if game_state.agents[opponent_id].score + CARDS[card_name][-1] >= 15:
                cost = -999

        else:
            collected_gems = [0, 0, 0, 0, 0]
            if 'collected_gems' in action.keys():
                for i in list(action['collected_gems'].keys()):
                    collected_gems[gem_type.index(i)] = action['collected_gems'][i]
            temp_list = [current_gems, current_resources, collected_gems, returned_gems]
            for current_card_cost in current_card_costs:
                current_agent_resources = [sum(x) for x in zip(*temp_list)]
                current_cost = [m - n for m, n in zip(current_agent_resources, current_card_cost)]
                for j in current_cost:
                    if j > 0:
                        current_cost[current_cost.index(j)] = 0
                    elif j < 0:
                        current_cost[current_cost.index(j)] = -j
                temp_cost.append(sum(current_cost) - current_yellow_gems + sum(returned_gems))
            cost = min(temp_cost)

    sum_cost = cost + noble_cost
    return sum_cost

def Card_Strategy(board_state):
    board_information = deepcopy(board_state)
    card_dealt_lists = board_information.dealt_list()
    card_total_frequency_list = []

    for card_dealt_list in card_dealt_lists:
        card_name = card_dealt_list.__repr__()
        card_frequency_list = {'black': 0, 'red': 0, 'green': 0, 'blue': 0, 'white': 0}
        for i in list(CARDS[card_name][1].keys()):
            card_frequency_list[i] = 1
        card_total_frequency_list.append(collections.Counter(card_frequency_list))

    card_strategy_list = dict(sum(card_total_frequency_list, collections.Counter()))

    min_key = min(card_strategy_list.keys(), key=lambda k: card_strategy_list[k])
    del card_strategy_list[min_key]
    card_strategy = list(card_strategy_list.keys())
    return card_strategy

# Reduce low cost performance actions
def ReducedAction(actions, agent_state, board_state):
    temp_actions = deepcopy(actions)
    agent_information = deepcopy(agent_state)
    board_information = deepcopy(board_state)
    strategy = Card_Strategy(board_information)
    legal_actions = []

    if agent_information.score <= 3:
        for temp_action in temp_actions:
            if 'collect_diff' in temp_action['type']:
                current_board_gem = list(board_information.gems.values())
                current_board_gem.pop(2)
                current_board_gem = [i for i in current_board_gem if i != 0]
                if sum(temp_action['collected_gems'].values()) == 1:
                    if len(current_board_gem) <= 1:
                        legal_actions.append(temp_action)
                elif sum(temp_action['collected_gems'].values()) == 2:
                    if len(current_board_gem) <= 2:
                        legal_actions.append(temp_action)
                else:
                    legal_actions.append(temp_action)

            elif 'reserve' in temp_action['type']:
                card_name = temp_action['card'].__repr__()
                card_id = CARDS[card_name][2]
                if card_id == 3:
                    if CARDS[card_name][-1] > 3:
                        if sum(list(CARDS[card_name][1].values())) < 14:
                            legal_actions.append(temp_action)

            elif 'buy_available' in temp_action['type']:
                card_name = temp_action['card'].__repr__()
                card_id = CARDS[card_name][2]
                if card_id == 1:
                    if CARDS[card_name][0] in strategy:
                        if len(list(agent_information.cards[CARDS[card_name][0]])) < 4:
                            legal_actions.append(temp_action)
                elif card_id == 2:
                    if sum(list(CARDS[card_name][1].values())) < 8:
                        legal_actions.append(temp_action)
                elif card_id == 3:
                    if CARDS[card_name][-1] > 3:
                        if sum(list(CARDS[card_name][1].values())) < 14:
                            legal_actions.append(temp_action)
            else:
                legal_actions.append(temp_action)

    elif agent_information.score > 3 & agent_information.score <= 8:
        for temp_action in temp_actions:
            if 'collect_diff' in temp_action['type']:
                current_board_gem = list(board_information.gems.values())
                current_board_gem.pop(2)
                current_board_gem = [i for i in current_board_gem if i != 0]
                if sum(temp_action['collected_gems'].values()) == 1:
                    if len(current_board_gem) <= 1:
                        legal_actions.append(temp_action)
                elif sum(temp_action['collected_gems'].values()) == 2:
                    if len(current_board_gem) <= 2:
                        legal_actions.append(temp_action)
                else:
                    legal_actions.append(temp_action)

            elif 'reserve' in temp_action['type']:
                card_name = temp_action['card'].__repr__()
                card_id = CARDS[card_name][2]
                if card_id == 3:
                    if sum(list(CARDS[card_name][1].values())) < 14:
                        legal_actions.append(temp_action)

            elif 'buy_available' in temp_action['type']:
                card_name = temp_action['card'].__repr__()
                card_id = CARDS[card_name][2]
                if card_id == 1:
                    if CARDS[card_name][0] in strategy:
                        if len(list(agent_information.cards[CARDS[card_name][0]])) < 5:
                            legal_actions.append(temp_action)
                elif card_id == 2:
                    legal_actions.append(temp_action)
                elif card_id == 3:
                    if sum(list(CARDS[card_name][1].values())) < 14:
                        legal_actions.append(temp_action)
            else:
                legal_actions.append(temp_action)

    else:
        for temp_action in temp_actions:
            if 'collect_diff' in temp_action['type']:
                current_board_gem = list(board_information.gems.values())
                current_board_gem.pop(2)
                current_board_gem = [i for i in current_board_gem if i != 0]
                if sum(temp_action['collected_gems'].values()) == 1:
                    if len(current_board_gem) <= 1:
                        legal_actions.append(temp_action)
                elif sum(temp_action['collected_gems'].values()) == 2:
                    if len(current_board_gem) <= 2:
                        legal_actions.append(temp_action)
                else:
                    legal_actions.append(temp_action)

            elif 'reserve' in temp_action['type']:
                card_name = temp_action['card'].__repr__()
                card_id = CARDS[card_name][2]
                if card_id == 3:
                    legal_actions.append(temp_action)

            elif 'buy_available' in temp_action['type']:
                card_name = temp_action['card'].__repr__()
                card_id = CARDS[card_name][2]
                if card_id == 1:
                    if CARDS[card_name][0] in strategy:
                        if len(list(agent_information.cards[CARDS[card_name][0]])) < 6:
                            legal_actions.append(temp_action)
                if card_id == 2:
                    legal_actions.append(temp_action)
                elif card_id == 3:
                    legal_actions.append(temp_action)
            else:
                legal_actions.append(temp_action)

    return legal_actions

def LegalAction(agent_id,game_rule, game_state):
    temp_rule = deepcopy(game_rule)
    temp_state = deepcopy(game_state)
    temp_actions = temp_rule.getLegalActions(temp_state, agent_id)
    agent_state = temp_state.agents[agent_id]
    board_state = temp_state.board
    legal_actions = ReducedAction(temp_actions, agent_state, board_state)
    return legal_actions

def minimax(actions, _id, game_state, depth):

        def change_id(_id):
            if _id == 1:
                return 0
            else:
                return 1

        def getMax(action, _id, depth, game_state):
            if depth == 0 or sp.gameEnds():
                # return evaluate(game_state, action, _id)
                # print(1)
                v = -Cost(game_state,action,change_id(_id))
                return v
            # print(game_state.board.gems)
            game_state = sp.generateSuccessor(game_state, action, change_id(_id))
            # print(game_state.board.gems)
            maximum = float('inf')
            self_actions = LegalAction(_id,sp,game_state)
            for self_action in self_actions:
                if self_action['type'] == 'collect_diff' or self_action['type'] == 'buy_available' or self_action['type'] == 'buy_reserve':
                    continue
                value = getMin(self_action, change_id(_id), depth, game_state)
                if value < maximum:
                    maximum = value
            return maximum

        def getMin(action, _id, depth, game_state):
            if depth == 0 or sp.gameEnds():
                return -Cost(game_state,action,change_id(_id))
            game_state = sp.generateSuccessor(game_state, action, change_id(_id))
            com_actions = LegalAction(_id,sp,game_state)
            minimum = float('inf')
            vs = -Cost(game_state,action,change_id(_id))
            for com_action in com_actions:
                va = vs - getMax(com_action, change_id(_id), depth-1, game_state)
                if va < minimum:
                    minimum = va
                if time.time() - start_time > time_allow:
                    return minimum
            return minimum

        sp = SplendorGameRule(2)
        best = -float('inf')
        move = None
        start_time = time.time()

        for action in actions:
            if (action['type'] == 'collect_diff' or action['type'] == 'collect_same') and action['returned_gems'] != {}:
                continue
            value = getMin(action, change_id(_id), depth,game_state)
            if value > best:
                best = value
                move = action
            if time.time() - start_time >time_allow:
                return action
        if move is None:
            move = actions[-1]
        return move



class myAgent(Agent):
    def __init__(self, _id):
        super().__init__(_id)

    def SelectAction(self, actions, game_states):
        agent_id = self.id
        # start_time = time.time()
        frontier = PriorityQueue()
        frontier.push((deepcopy(game_states), []), 0)
        ac = minimax(self.LegalAction(SplendorGameRule(2), game_states), agent_id, game_states, 1)
        return ac

    def LegalAction(self, game_rule, game_state):
        agent_id = self.id
        temp_rule = deepcopy(game_rule)
        temp_state = deepcopy(game_state)
        temp_actions = temp_rule.getLegalActions(temp_state, agent_id)
        agent_state = temp_state.agents[agent_id]
        board_state = temp_state.board
        legal_actions = ReducedAction(temp_actions, agent_state, board_state)
        return legal_actions

class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)



