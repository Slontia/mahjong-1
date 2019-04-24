
# coding: utf-8

# In[7]:


from naiveAI import AgentNaive, NMnaive
import tensorflow as tf
import numpy as np
from copy import deepcopy
from buffer import PrioritizedReplayBuffer


# In[8]:


sess = tf.InteractiveSession()


# In[12]:


class EnvMahjong:
    """
    An example mahjong environment for agent to interact with.
    """
    def __init__(self):
        pass
    
    def reset(self):
        self.turn = 0
        init_state = np.random.randint(low=0, high=2, size=[1, 34, 4, 1]).astype(np.float32)
        return init_state
        
        
    def step(self, action):
        """
        param: action is an action generated by the agent (agent.select()), 
            action=None means there is no available action, just go to next state
        """
        
        next_state = np.random.randint(low=0, high=2, size=[1, 34, 4, 1]).astype(np.float32)
        score = 0.  # if next_state 胡了, score = 胡的分数, else score = 0
        
        if self.turn >= 100:
            done = 1 # done=1 means this game terminates
        else:
            done = 0
            
        info = {'turn': self.turn} # other information not included in state
        
        self.turn += 1
        
        return next_state, score, done, info
    
    def get_aval_actions(self):
        N = np.random.randint(low=1, high=13)
        if N == 0:  # no available actions
            next_aval_states = None
        else:
            next_aval_states = np.random.randint(low=0, high=2, size=[N, 34, 4, 1]).astype(np.float32)
                
        return next_aval_states
    

'''
Agony:
游戏本身涉及到4个玩家。不建议在游戏中做状态获取和步进。

推荐将main处的训练代码用以下类代替。

在游戏过程中交替调用receive_selection和receive_state

并且在游戏结束时调用terminate(未在代码中体现)来结束一局的训练

agent是独立于该类的。训练开始时，创建1个（4个for all players）Agent对象，
之后每次游戏开始时会创建1个MahjongLearner对象（4个for all players）用于和
C++游戏之间进行交互。
'''

class MahjongLearner:
    def __init__(self, agent):
        self.agent = agent
        self.action = None
        self.policy = None
        self.next_aval_states = None
        self.this_state = None        

    def receive_hand_and_select(self, hand):
        return self.get_selection(hand)

    def get_selection(self, hand):
        #from hand generate next_aval_states
        assert(hand == 14)
        self.next_aval_states = np.zeros([14, 34, 4])
        for i in range(14):
            for j in range(14):
                if i == j:
                    continue
                for k in range(4):
                    if self.next_aval_states[i, hand[j], k] == 0:
                        self.next_aval_states[i, hand[j], k] = 1
                        break

        action, policy = agent.select(next_aval_states)
        self.action = action
        self.policy = policy
        return action

    def receive_hand_only(self, hand):
        agent.remember(this_state = self.this_state, 
                       next_state = hand, 
                       score = 0,  
                       done = -1,                        
                       next_aval_states = self.next_aval_states, 
                       policy = self.policy)
        agent.learn()
        self.this_state = next_state


if __name__ == 'main':

    nn = NMnaive(sess)
    env = EnvMahjong()

    # before the train start, create 4 agents.
    memory = PrioritizedReplayBuffer(state_dim=34*4, action_dim=34)
    agent = AgentNaive(nn, memory)


    # In[14]:


    n_games = 2

    for n in range(n_games):
        done = 0
        this_state = env.reset()

        step = 0

        while not done and step < 10000:

            next_aval_states = env.get_aval_actions()
            action, policy = agent.select(next_aval_states)

            next_state, score, done, info = env.step(action)

            agent.remember(this_state, action, next_state, score, done, next_aval_states, policy)
            agent.learn()

            this_state = deepcopy(next_state)
            step += 1

            print("Game {}, step {}".format(n, step))
            print(info)




# In[ ]:





# In[ ]:




