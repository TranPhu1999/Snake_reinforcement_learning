# modified snake game to implement AI
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.SysFont('arial',24)

# reset
# reward
# play(action) -> direction
# game_iteration
# is_collision

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point',['x','y'])

#rgb color
WHITE = (255,255,255)
RED = (200,0,0)
BLUE1 = (0,0,255)
BLUE2 = (0,100,255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 30

class SnakeGame:
    def __init__(self, w = 640, h = 480):
        self.w = w
        self.h = h

        #init display
        self.display = pygame.display.set_mode((self.w,self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

        #init game state
    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,Point(self.head.x - BLOCK_SIZE, self.head.y),Point(self.head.x - 2*BLOCK_SIZE, self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.game_iteration = 0

    def play_step(self, action):
        self.game_iteration += 1
        #1.collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_a:
            #        self.direction = Direction.LEFT
            #     elif event.key == pygame.K_d:
            #        self.direction = Direction.RIGHT
            #     elif event.key == pygame.K_w:
            #        self.direction = Direction.UP 
            #     elif event.key == pygame.K_s:
            #        self.direction = Direction.DOWN  
        #2.move
        self._move(action)
        self.snake.insert(0,self.head)

        #3.check if game over
        game_over = False
        reward = 0
        if self.is_collision() or self.game_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        #4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        #5.update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        #6.return game over and score

        return reward, game_over,self.score
    
    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE)//BLOCK_SIZE) *BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE)//BLOCK_SIZE) *BLOCK_SIZE
        self.food = Point(x,y)
        if self.food in self.snake:
            self._place_food()

    def is_collision(self, point = None):
        #hit boundary
        if point == None:
            point = self.head
        if point.x > self.w - BLOCK_SIZE or point.x < 0 or point.y < 0 or point.y > self.h - BLOCK_SIZE:
            return True
        #hit it self
        if point in self.snake[1:]:
            return True
        return False

    def _move(self,action):
        # [straight, right, left]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action,[1,0,0]):
            new_direction = clock_wise[idx] # no change
        elif np.array_equal(action,[0,1,0]):
            next_idx = (idx + 1) % 4
            new_direction = clock_wise[next_idx] # turn right with the current direction
        if np.array_equal(action,[0,0,1]):
            next_idx = (idx - 1) % 4
            new_direction = clock_wise[next_idx] # turn left with the current direction

        self.direction = new_direction
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        if self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        if self.direction == Direction.UP:
            y -= BLOCK_SIZE
        if self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        
        self.head = Point(x,y)

    def _update_ui(self):
        self.display.fill(BLACK)
        for point in self.snake:
            pygame.draw.rect(self.display,BLUE1, pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE))
        
        pygame.draw.rect(self.display,RED, pygame.Rect(self.head.x+10, self.head.y+2, 5, 5))
        pygame.draw.rect(self.display,RED, pygame.Rect(self.head.x+10, self.head.y+12, 5, 5))
        pygame.draw.rect(self.display,RED, pygame.Rect(self.food.x,self.food.y,BLOCK_SIZE,BLOCK_SIZE))
        text = font.render("Score: " + str(self.score),True,WHITE)
        self.display.blit(text,[0,0])
        pygame.display.flip()


# if __name__ == '__main__':
#     game = SnakeGame()

#     #gameloop
#     while True:
#         game_over, score = game.play_step()

#         #break if game over
#         if game_over:
#             break

#     print('Final score',score)

#     pygame.quit()