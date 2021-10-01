from typing_extensions import final
import torch
import random
import numpy as np
from snake_game_AI import Direction, Point, SnakeGame
from collections import deque
from model import Linear_Qnet, Qtrainer
from helper import plot

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001 #Learning rate

class Agent:
    def __init__(self):
        self.n_game = 0
        self.epsilon = 0 #randomness
        self.gamma = 0.9 #discount rate
        self.memory = deque(maxlen= MAX_MEMORY) #popleft() if reach MAX_MEMORY

        self.model = Linear_Qnet(11,512,3)
        self.trainer = Qtrainer(self.model, lr = LR, gamma= self.gamma)

    def get_state(self,game):
        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y-20)
        point_d = Point(head.x, head.y+20)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            #Danger straight 
            (dir_r and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),

            #Danger right 
            (dir_r and game.is_collision(point_d)) or
            (dir_l and game.is_collision(point_u)) or
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)),

            #Danger left 
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)) or
            (dir_u and game.is_collision(point_l)) or
            (dir_d and game.is_collision(point_r)),

            #Direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            #Food location
            game.food.x < game.head.x, #food on the left of the snake head
            game.food.x > game.head.x, #right
            game.food.y < game.head.y, #up
            game.food.y > game.head.y #down
        ]
        return np.array(state, dtype= int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else: 
            mini_sample = self.memory
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        # for state, action, reward, next_state, done in mini_sample:
        #     self.trainer.train_step(state, action, reward, next_state, done)
    
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self,state):
        # random moves: trades off exploration / exploitation
        self.epsilon = 80 - self.n_game
        final_move = [0,0,0]
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype= torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        
        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    highest_record = 0
    agent = Agent()
    game = SnakeGame()
    while True:
        #get old state
        state_0 = agent.get_state(game)

        #get move
        final_move = agent.get_action(state_0)

        #perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_1 = agent.get_state(game)

        #train short memory
        agent.train_short_memory(state_0, final_move,reward,state_1, done)

        #remember
        agent.remember(state_0, final_move,reward,state_1, done)

        if done:
            #train long memory, plot result
            game.reset()
            agent.n_game += 1
            agent.train_long_memory()

            if score > highest_record: 
                highest_record = score
                agent.model.save()
            
            print('Game: ', agent.n_game, 'Score: ',score,'Highest record: ', highest_record)

            #plot
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_game
            plot_mean_scores.append(mean_score)
            plot(plot_scores,plot_mean_scores)


if __name__ == '__main__':
    train()