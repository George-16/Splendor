# Splendor

<p align="center"> 
    <img src="img/splendor.jpg" alt="logo project 2" width="505">
 </p>

# Greedy Best First Search - Computational Approach

# Table of Contents
- [Governing Strategy Tree](#governing-strategy-tree)
  * [Motivation](#motivation)
  * [Application](#application)
  * [Trade-offs](#trade-offs)     
     - [Advantages](#advantages)
     - [Disadvantages](#disadvantages)
  * [Future improvements](#future-improvements)

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

[Back to top](#table-of-contents)
