# Splendor

<p align="center"> 
    <img src="img/splendor.jpg" alt="logo project 2" width="505">
 </p>

# Greedy Best First Search

## Governing Strategy Tree  

### Motivation  
The Greedy Best First Search is an efficient search algorithm which guarantees the local optimal because of the time limitation. In the Splendor board game, it is essential to perform an easy construct and less time-consuming algorithm and the Greedy Best First Search satisfies those requirements. Moreover, GBFS would support the understanding of Splendor operation procedure before we implement in-depth upgrading of algorithms.

### Application  
In the GBFS algorithm, the cost function involves each distance calculation between current total assets and cards cost; the price-to-price ratio of buying cards. In addition, we performed a cost function with a Reduced-Action(RA) function which helps to resolve the high branch factor problems. The RA function throws away the low-performance actions such as collect one gem and reserve Tier 1 cards etc. The game strategy includes picking the 4 most frequent resources in the board by traversing and the methods of three different actions:

| Methods | Details |
|-----------------|:-------------|
| Collect |Without collect one or two gems if the type of board gems is less than or equal to 2 |
| Reserve | Only reserve Tier 3 card with cost less than 14 and score bigger than 3 when scoring below 3; Only reserve Tier 3 card with cost less than 14  when scoring below 8 and bigger than or equal to 3; Only reserve Tier 3 card when scoring beyond 8  |
| Buy | Ensure the Tier 1 card of each resource is less than or equal to 4 |

In the following, at the Select-Action function, we constructed a priority queue to ensure the lowest cost. Furthermore, we designed a goal recognition strategy against the opponent to ensure that when we fall behind and the opponent can buy a card that directly wins in the next round, we would choose to reserve that card. 

### Trade-offs  
#### *Advantages*  
* Medium Win rate
* Guarantee local optimal
* Low time complexity
* Easy to construct

#### *Disadvantages*
* Unstable performance in a game with relatively even resources 
* Sometimes extra actions are chosen because of losing board information(eg. The opponent bought or reserved cards)

### Future improvements  
In the future, it is appreciated that we can make a better strategy to consider more about the collection of gems that benefits the agent and weaken the opponent. What's more, reserving a particular card which is important to the opponent.


# Reinforcement Learning with Approximate Q-Learning

## Governing Strategy Tree  

### Motivation  
Approximate Q-learning is a type of model-free reinforcement learning method that can interact with the game environment base on the states, which upgrades the transition by the following: Learning rate * (reward + discount factor * (current value - previous value)). This formula guarantees an optimal policy by repeating game episodes. In this game, there are various combinations of board states and actions which provides a resourceful environment and Q-learning can potentially accumulate experience from it. This would help the agent to make rational decisions to proceed to the goal.


### Application  
#### Feature selection-
In this approach, we calculate feature values for each action: collect, reserve and buy regarding different cases.

Collect: Find distances from agent and opponent to card and reserve card, and scale them into a ratio of distance after obtaining the gem against the distance; a penalty applied of picking fewer gems or return gems.

Reserve: Find the specific card resource and check whether the agent needs it; yellow gems requirements; check whether opponent could buy that card; check whether the resources in noble's cost; a penalty of returning gems or none yellow gems.

Buy: Score reward; gem costs; yellow gem costs; check noble in this action or not; check the demand of that card(which means the resource of that card is essential to other cards and reserve cards or not); check the opponent's demands with that card; compare that cards' resource with respect to noble's cost; consider the price-to-price ratio; the penalty of a number of resources exceed 4.

#### Training phase-
With the predefined learning rate and discount factor, we then employ the approximate Q-function to continuously update the feature and weight values by running the game over and over again until it can achieve a relatively high winning rate. 


### Trade-offs  
#### *Advantages*  
* Interact with the game environment
* Possible to construct global optimal
* Simplicity of implementation by policy and feature selections

#### *Disadvantages*
* Take too long to train
* Might overestimate reward
* High space complexity with expansion nodes

### Future improvements  
In order to reduce the uncertainties, a significant amount of learning processes is required in training. Moreover, minimizing the features might be a good choice to accurate the weights. Furthermore, deep reinforcement learning is an upgrading approach to strengthen the performance of reinforcement learning.


# Envrioment Setup




