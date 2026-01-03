# simpleAgents.py
# 简单的自动agent示例

from game import Agent
from game import Directions
import random

class RandomAgent(Agent):
    """随机移动的agent"""
    
    def getAction(self, state):
        legal = state.getLegalActions(self.index)
        if not legal:
            return Directions.STOP
        return random.choice(legal)


class GreedyAgent(Agent):
    """贪心agent：总是朝着最近的食物移动"""
    
    def getAction(self, state):
        legal = state.getLegalActions(self.index)
        if not legal:
            return Directions.STOP
        
        # 获取当前位置
        pacman_pos = state.getPacmanPosition()
        food = state.getFood()
        
        # 找到最近的食物
        min_distance = float('inf')
        best_action = random.choice(legal)
        
        for action in legal:
            successor = state.generatePacmanSuccessor(action)
            if successor is None:
                continue
            
            new_pos = successor.getPacmanPosition()
            # 计算到最近食物的距离
            food_list = food.asList()
            if food_list:
                distances = [abs(new_pos[0] - f[0]) + abs(new_pos[1] - f[1]) 
                           for f in food_list]
                min_dist = min(distances) if distances else float('inf')
                if min_dist < min_distance:
                    min_distance = min_dist
                    best_action = action
        
        return best_action

