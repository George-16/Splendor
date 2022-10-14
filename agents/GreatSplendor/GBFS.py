from template import Agent
import heapq
import time
import collections
from copy import deepcopy
from Splendor.splendor_model import *
from Splendor.splendor_utils import *
# python3 splendor_runner.py -r agents.GreatSplendor.myTeam -p
# python splendor_runner.py --replay=replays/replay.replay
# Group GreatSplendor
time_allow = 0.99
num_of_agent = 2

def Cost(state, action, agent_id):
    cost = 0
    noble_cost = 0
    game_state = deepcopy(state)
    agent_state = game_state.agents[agent_id]
    board_state = game_state.board
    strategy, maximum_resource = Card_Strategy(board_state)

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

    card_cost = list(action['returned_gems'].values())

    if 'buy_available' in action['type']:
        card_name = action['card'].__repr__()
        card_point = CARDS[card_name][-1]
        card_id = CARDS[card_name][2]
        if sum(card_cost) == 0:
            if card_id == 1:
                index_reward = [1.425, 1.275, 1.15, 1.05]
                if CARDS[card_name][0] in strategy:
                    index_val = strategy.index(CARDS[card_name][0])
                    cost = -9 * index_reward[index_val]
                    if card_point == 1:
                        cost = -9.9 * index_reward[index_val]
                else:
                    cost = -9
            elif card_id == 2:
                cost = -99
            elif card_id == 3:
                cost = -999
        else:
            weight = card_point / sum(card_cost)
            if card_id == 1:
                if weight == 0:
                    cost = -9 + sum(card_cost)
                else:
                    cost = -9 + weight * card_point

                if CARDS[card_name][0] in strategy:
                    index_reward = [1.425, 1.275, 1.15, 1.05]
                    index_val = strategy.index(CARDS[card_name][0])
                    cost = cost * index_reward[index_val]
            elif card_id == 2:
                cost = -99 + weight * card_point
            elif card_id == 3:
                cost = -999 + weight * card_point

            if agent_state.gems[CARDS[card_name][0]] \
                    + len(agent_state.cards[CARDS[card_name][0]]) + 1 > maximum_resource[CARDS[card_name][0]]:
                cost = 999

            if (agent_state.score + card_point) >= 15:
                cost = -99999

        if action['noble'] != 'None':
            noble_cost = -999
            if (agent_state.score + card_point + 3) >= 15:
                noble_cost = -99999

    elif 'buy_reserve' in action['type']:
        card_name = action['card'].__repr__()
        card_point = CARDS[card_name][-1]
        cost = -999

        if action['noble'] != 'None':
            noble_cost = -999
            if (agent_state.score + card_point + 3) >= 15:
                noble_cost = -99999

    else:
        temp_cost = []
        returned_gems = [0, 0, 0, 0, 0]
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

            opponent, opponent_id, opponent_name = Opponent_Strategy(game_state, agent_id)
            if agent_state.score < game_state.agents[opponent_id].score:
                if card_name == opponent_name:
                    if opponent:
                        cost = -9999

        else:
            collected_gems = [0, 0, 0, 0, 0]
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

            flag = True
            for k in list(action['collected_gems'].keys()):
                if agent_state.gems[k] + len(agent_state.cards[k]) + action['collected_gems'][k] > maximum_resource[k]:
                    flag = False

            if not flag:
                cost = 999
            else:
                cost = min(temp_cost)

    sum_cost = cost + noble_cost

    return sum_cost

def Card_Strategy(board_state):
    board_information = deepcopy(board_state)
    card_dealt_lists = board_information.dealt_list()
    card_total_frequency_list = []
    card_list = {'black': 0, 'red': 0, 'green': 0, 'blue': 0, 'white': 0}
    maximum_resource = {'black': 0, 'red': 0, 'green': 0, 'blue': 0, 'white': 0}

    for card_dealt_list in card_dealt_lists:
        card_name = card_dealt_list.__repr__()
        for i in list(CARDS[card_name][1].keys()):
            card_list[i] = 1
        card_total_frequency_list.append(collections.Counter(card_list))

        for j in list(CARDS[card_name][1].keys()):
            if CARDS[card_name][1][j] > maximum_resource[j]:
                maximum_resource[j] = CARDS[card_name][1][j]

    card_strategy_list = dict(sum(card_total_frequency_list, collections.Counter()))

    min_key = min(card_strategy_list.keys(), key=lambda k: card_strategy_list[k])
    del card_strategy_list[min_key]
    card_strategy = list(card_strategy_list.keys())

    return card_strategy, maximum_resource

def Opponent_Strategy(state, agent_id):
    game_state = deepcopy(state)
    if agent_id == 0:
        opponent_id = 1
    else:
        opponent_id = 0
    opponent_state = game_state.agents[opponent_id]
    opponent_actions = SplendorGameRule(num_of_agent).getLegalActions(game_state, opponent_id)
    for opponent_action in opponent_actions:
        if 'buy_available' in opponent_action['type']:
            opponent_name = opponent_action['card'].__repr__()
            opponent_point = CARDS[opponent_name][-1]
            if CARDS[opponent_name][2] == 3:
                if opponent_point + opponent_state.score >= 15:
                    opponent = True
                    return opponent, opponent_id, opponent_name

    return False, opponent_id, None

# Reduce low cost performance actions
def ReducedAction(actions, state, agent_id):
    temp_actions = deepcopy(actions)
    game_state = deepcopy(state)
    agent_information = game_state.agents[agent_id]
    board_information = game_state.board
    legal_actions = []

    for temp_action in temp_actions:
        if 'collect_diff' in temp_action['type']:
            current_board_gem = list(board_information.gems.values())
            current_board_gem.pop(2)
            current_board_gem = [i for i in current_board_gem if i != 0]
            if sum(temp_action['collected_gems'].values()) == 1:
                if len(current_board_gem) <= 1:
                    legal_actions.append(temp_action)
            elif sum(temp_action['collected_gems'].values()) == 2:
                if len(current_board_gem) <= 3:
                    legal_actions.append(temp_action)
            else:
                legal_actions.append(temp_action)

        elif 'reserve' in temp_action['type']:
            card_name = temp_action['card'].__repr__()
            card_id = CARDS[card_name][2]
            if card_id == 3:
                if agent_information.score <= 3:
                    if CARDS[card_name][-1] > 3:
                        if sum(list(CARDS[card_name][1].values())) < 14:
                            legal_actions.append(temp_action)
                elif agent_information.score > 3 & agent_information.score <= 8:
                    if sum(list(CARDS[card_name][1].values())) < 14:
                        legal_actions.append(temp_action)
                else:
                    legal_actions.append(temp_action)

        elif 'buy_available' in temp_action['type']:
            card_name = temp_action['card'].__repr__()
            card_id = CARDS[card_name][2]
            if card_id == 1:
                if len(list(agent_information.cards[CARDS[card_name][0]])) < 4:
                    legal_actions.append(temp_action)
            else:
                legal_actions.append(temp_action)
        else:
            legal_actions.append(temp_action)

    return legal_actions

def LegalAction(game_rule, game_state, agent_id):
    temp_rule = deepcopy(game_rule)
    temp_state = deepcopy(game_state)
    temp_actions = temp_rule.getLegalActions(temp_state, agent_id)
    legal_actions = ReducedAction(temp_actions, temp_state, agent_id)
    return legal_actions

class myAgent(Agent):
    def __init__(self, _id):
        super().__init__(_id)

    def SelectAction(self, actions, game_states):
        agent_id = self.id
        start_time = time.time()
        frontier = PriorityQueue()
        frontier.push((deepcopy(game_states), []), 0)
        game_rule = SplendorGameRule(num_of_agent)
        cost = [99999]
        while not frontier.isEmpty() and time.time() - start_time < time_allow:
            state, action = frontier.pop()
            paths = LegalAction(game_rule, state, agent_id)
            if len(action) > 0:
                if Cost(state, action[0], agent_id) == min(cost):
                    return action[0]
            for path in paths:
                next_state = deepcopy(state)
                next_path = action + [path]
                next_cost = Cost(state, path, agent_id)
                if next_cost < float("inf"):
                    frontier.push((next_state, next_path), next_cost)
                    cost.append(next_cost)
        return frontier.pop()

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
