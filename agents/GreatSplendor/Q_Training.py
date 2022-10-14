from template import Agent
import time
import numpy as np
from Splendor.splendor_model import *
# python3 splendor_runner.py -r agents.GreatSplendor.Q -c agents.GreatSplendor.myTeam -p
# python splendor_runner.py --replay=replays/replay.replay
# Group GreatSplendor
time_allow = 0.99
num_of_agent = 2

gem_types = ['red', 'green', 'blue', 'black', 'white', 'yellow']

E = 0.1
GAMMA = 0.9
ALPHA = 0.0005

def get_agent_state(game_state, agent_id):
    agent_state = game_state.agents[agent_id]
    agent_gems = []
    agent_resources = []
    agent_reserves = []
    for gem_type in gem_types:
        try:
            agent_gems.append(agent_state.gems[gem_type] + len(agent_state.cards[gem_type]))
            agent_resources.append(len(agent_state.cards[gem_type]))
        except:
            agent_gems.append(agent_state.gems[gem_type])
            agent_resources.append(0)

    for reserve_card in agent_state.cards['yellow']:
        temp_reserves = [reserve_card.points, reserve_card.colour]
        for gem_type in gem_types:
            try:
                temp_reserves.append(reserve_card.cost[gem_type])
            except:
                temp_reserves.append(0)
        agent_reserves.append(temp_reserves)

    return np.array(agent_gems), np.array(agent_resources), np.array(agent_reserves)

def get_board_state(game_state):
    board_state = game_state.board
    board_cards = []
    board_nobles = []
    for i in range(3):
        for j in range(4):
            if board_state.dealt[i][j] is not None:
                temp_board_cards = [board_state.dealt[i][j].points, board_state.dealt[i][j].colour]
                for k in gem_types:
                    try:
                        temp_board_cards.append(board_state.dealt[i][j].cost[k])
                    except:
                        temp_board_cards.append(0)
                board_cards.append(temp_board_cards)

    for noble in board_state.nobles:
        temp_board_nobles = [3, 'None']
        for gem_type in gem_types:
            try:
                temp_board_nobles.append(noble[1][gem_type])
            except:
                temp_board_nobles.append(0)
        board_nobles.append(temp_board_nobles)

    return np.array(board_cards), np.array(board_nobles)

def get_action(action):
    gems_cost = []
    resources_reward = [0, 0, 0, 0, 0]

    if 'collect_diff' in action['type'] or 'collect_same' in action['type']:
        gems_cost = [0]
        for gem_type in gem_types:
            try:
                temp_gem = action['collected_gems'][gem_type]
            except:
                temp_gem = 0

            try:
                current_gem = temp_gem - action['returned_gems'][gem_type]
            except:
                current_gem = temp_gem

            gems_cost.append(current_gem)

    elif 'buy_available' in action['type'] or 'buy_reserve' in action['type']:
        gems_cost.append(action['card'].points)
        for gem_type in gem_types:
            try:
                gems_cost.append(- action['returned_gems'][gem_type])
            except:
                gems_cost.append(0)

        resources_reward[gem_types.index(action['card'].colour)] = 1

    elif 'reserve' in action['type']:
        gems_cost = [0, 0, 0, 0, 0, 0, 1]

    if action['noble'] is not None:
        gems_cost[0] = gems_cost[0] + 3

    return np.array(gems_cost), np.array(resources_reward)

def Find_Distance(cards, current_gems, current_resources):
    distances = []
    for card in cards:
        card_cost = card[2:].astype(np.int)
        assets = [current_gems, current_resources]
        sum_assets = [sum(x) for x in zip(*assets)]
        distance = [m - n for m, n in zip(card_cost, sum_assets)]
        for i in distance:
            if i > 0:
                distance[distance.index(i)] = i
            elif i < 0:
                distance[distance.index(i)] = 0

        distances.append(distance)

    return distances

class myAgent(Agent):
    def __init__(self, _id):
        super().__init__(_id)
        self.id = _id

    def Collect_Features(self, action, gems, resources, reserves, dealt_cards, opp_gems,
                                    opp_resources, opp_reserves):
        features = []

        dis_to_dealt = Find_Distance(dealt_cards, gems, resources)
        dis_to_reserve = Find_Distance(reserves, gems, resources)
        opp_dis_to_dealt = Find_Distance(dealt_cards, opp_gems, opp_resources)
        opp_dis_to_reserve = Find_Distance(opp_reserves, opp_gems, opp_resources)

        def ratio(card_distances):
            ratio = 0
            for card_distance in card_distances:
                for colour, gems in action['collected_gems'].items():
                    index = gem_types.index(colour)
                    gem_distance = max(card_distance[index] - gems, 0)
                    if gem_distance != 0:
                        ratio += gem_distance / card_distance[index]
            return ratio

        # feature 1,2,3,4 : distances with increasing rate
        for distances in [dis_to_dealt, dis_to_reserve, opp_dis_to_dealt, opp_dis_to_reserve]:
            features.append(ratio(distances))

        # feature 5: penalty with less pick
        if action['type'] == 'collect_diff' and len(action['collected_gems']) < 3 or action['returned_gems']:
            features.append(1)
        else:
            features.append(0)

        return features

    def Reserve_Features(self, action, gems, resources, reserves, dealt_cards, nobles, opp_gems,
                                    opp_resources, opp_reserves):
        features = []

        dis_to_dealt = Find_Distance(dealt_cards, gems, resources)
        dis_to_reserve = Find_Distance(reserves, gems, resources)
        opp_dis_to_dealt = Find_Distance(dealt_cards, opp_gems, opp_resources)
        opp_dis_to_reserve = Find_Distance(opp_reserves, opp_gems, opp_resources)

        def target(cards, current_gems):
            gem_index = gem_types.index(action['card'].colour)
            if len(cards) == 0:
                return 0
            cnt = 0
            for card in cards:
                if int(card[gem_index + 2]) - current_gems[gem_index] > 0:
                    cnt += 1

            return cnt

        # feature 1: card
        features.append(target(dealt_cards, resources) + target(reserves, resources))

        # feature 2: yellow gem
        cnt = 0
        for dis_yellow in dis_to_dealt + dis_to_reserve:
            if sum(dis_yellow) == 1:
                cnt += 1
        features.append(cnt)

        # feature 3: opponent can buy it
        cnt = 0
        for dis_opp in opp_dis_to_dealt + opp_dis_to_reserve:
            if sum(dis_opp) == 0:
                cnt += 1
        features.append(cnt)

        # feature 4: nobel check
        features.append(target(nobles, resources))

        # feature 5: penalty of gems
        if not action["collected_gems"] or action['returned_gems']:
            features.append(1)
        else:
            features.append(0)

        return features

    def Buy_Features(self, action, resources, reserves, dealt_cards, nobles, opp_resources, opp_reserves):
        gem_index = gem_types.index(action['card'].colour)
        gems_cost, _ = get_action(action)

        def target(cards, current_gems):
            if len(cards) == 0:
                return 0
            cnt = 0
            for card in cards:
                if int(card[gem_index + 2]) - current_gems[gem_index] > 0:
                    cnt += 1

            return cnt

        # feature 1: score got after buying
        # feature 2: gem rewards or costs
        # feature 3: yellow gem consumed
        features = [gems_cost[0], sum(gems_cost[1:]), gems_cost[-1]]

        # feature 4: noble visited
        if action['noble'] is not None:
            features.append(1)
        else:
            features.append(0)

        # feature 5,6,7: check if buy cards needed
        features.append(target(dealt_cards, resources) + target(reserves, resources))
        features.append(target(dealt_cards, opp_resources) + target(opp_reserves, opp_resources))
        features.append(target(nobles, resources))

        # feature 8: price–performance ratio in cards
        if sum(gems_cost[1:]) > 0:
            features.append(gems_cost[0]/sum(gems_cost[1:]))
        else:
            features.append(1)

        # feature 9: penalty of resources
        if resources[gem_index] > 4:
            features.append(1)
        else:
            features.append(0)

        return features

    def Q_function(self, feature, weight):
        q_value = 0
        for i in range(len(weight)):
            q_value += np.multiply(feature[i], weight[i])
        return q_value

    def opponent_id(self, agent_id):
        if agent_id == 1:
            return 0
        else:
            return 1

    def calculate_feature(self, action, gems, resources, reserves, dealt_cards, nobles, opp_gems,
                                opp_resources, opp_reserves):
        if action is None:
            pass
        elif action["type"] == "collect_diff" or action["type"] == "collect_same":
            return self.Collect_Features(action, gems, resources, reserves, dealt_cards, opp_gems,
                                              opp_resources, opp_reserves)
        elif action["type"] == "reserve":
            return self.Reserve_Features(action, gems, resources, reserves, dealt_cards, nobles, opp_gems,
                                              opp_resources, opp_reserves)
        elif action["type"] == "buy_available" or action["type"] == "buy_reserve":
            return self.Buy_Features(action, resources, reserves, dealt_cards, nobles, opp_resources, opp_reserves)

    def SelectAction(self, actions, game_state):
        agent_id = self.id
        opp_id = self.opponent_id(agent_id)

        gems, resources, reserves = get_agent_state(game_state, agent_id)
        opp_gems, opp_resources, opp_reserves = get_agent_state(game_state, opp_id)
        dealt_cards, nobles = get_board_state(game_state)
        best_value = 0
        move = actions[0]
        current_score = game_state.agents[self.id].score
        weight_dict = {'collect': [], 'reserve': [], 'buy': []}

        with open("weight.txt", "r") as f:
            for i in range(5):
                a = f.readline()
                weight_dict['collect'].append(float(a))

            for i in range(5):
                a = f.readline()
                weight_dict['reserve'].append(float(a))

            for i in range(9):
                a = f.readline()
                weight_dict['buy'].append(float(a))

        start_time = time.time()
        if time.time() - start_time < time_allow:
            for action in actions:
                feature = self.calculate_feature(action, gems, resources, reserves, dealt_cards, nobles, opp_gems,
                                                 opp_resources, opp_reserves)
                weight_index = 'collect' if action['type'] in ['collect_diff', 'collect_same'] \
                    else 'buy' if action['type'] in ['buy_available', 'buy_reserve'] else 'reserve'
                value = self.Q_function(feature, weight_dict[weight_index])

                if value > best_value:
                    best_value = value
                    move = action

        else:
            return move

        with open("feature.txt", "r") as f:
            actionType = f.readline()

            if actionType[0] != "n":
                last_feature = float(f.readline())
                last_score = float(f.readline())
                reward = (current_score - last_score) * 999

                if game_state.agents[agent_id].score >= 15:
                    reward += 9999

                product = ALPHA * (reward + GAMMA * best_value - last_feature)

                if actionType[0] == 'c':
                    for i in range(5):
                        last_feature = float(f.readline())
                        weight_dict['collect'][i] += last_feature * product

                elif actionType[0] == 'r':
                    for i in range(5):
                        last_feature = float(f.readline())
                        weight_dict['reserve'][i] += last_feature * product

                elif actionType[0] == 'b':
                    for i in range(9):
                        last_feature = float(f.readline())
                        weight_dict['buy'][i] += last_feature * product

                with open("weight.txt", "w") as fw:
                    for item in weight_dict['collect'] + weight_dict['reserve'] + weight_dict['buy']:
                        fw.write(str(item) + '\n')

        if random.random() <= E:
            move = random.choice(actions)

        with open("feature.txt", "w") as f:

            if move['type'] == "collect_diff" or move['type'] == "collect_same":
                feature = self.Collect_Features(move, gems, resources, reserves, dealt_cards, opp_gems,
                                                     opp_resources, opp_reserves)
                f.write("c\n")
                f.write(str(best_value) + '\n')
                f.write(str(current_score) + '\n')
                for item in feature:
                    f.write(str(item) + '\n')
            elif move['type'] == "reserve":
                feature = self.Reserve_Features(move, gems, resources, reserves, dealt_cards, nobles, opp_gems,
                                                     opp_resources, opp_reserves)
                f.write("r\n")
                f.write(str(best_value) + '\n')
                f.write(str(current_score) + '\n')
                for item in feature:
                    f.write(str(item) + '\n')
            elif move["type"] == "buy_reserve" or move["type"] == "buy_available":
                feature = self.Buy_Features(move, gems, reserves, dealt_cards, nobles, opp_gems, opp_reserves)
                f.write("b\n")
                f.write(str(best_value) + '\n')
                f.write(str(current_score) + '\n')
                for item in feature:
                    f.write(str(item) + '\n')

        return move

