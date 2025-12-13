# keyboardAgents.py
# -----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from game import Agent
from game import Directions
import random

class KeyboardAgent(Agent):
    """
    An agent controlled by the keyboard.
    """
    # NOTE: Arrow keys also work.
    WEST_KEY  = 'a'
    EAST_KEY  = 'd'
    NORTH_KEY = 'w'
    SOUTH_KEY = 's'
    STOP_KEY = 'q'

    def __init__( self, index = 0 ):

        self.lastMove = Directions.STOP
        self.index = index
        self.keys = []
        self.pendingAction = None  # 回合制：存储待执行的动作

    def getAction( self, state):
        from graphicsUtils import keys_waiting
        from graphicsUtils import keys_pressed
        import time
        
        # 回合制模式：等待按键按下并释放才算一个完整动作
        # 1. 等待按键按下
        # 2. 等待按键释放
        # 3. 返回对应的动作
        
        # 初始化按键状态跟踪
        if not hasattr(self, '_key_pressed_state'):
            self._key_pressed_state = {}  # 记录哪些键被按下
        
        # 第一步：等待按键按下
        key_pressed = None
        while key_pressed is None:
            # 检查新按下的键
            waiting_keys = list(keys_waiting())
            current_pressed = set(keys_pressed())
            
            # 找出新按下的键（在current_pressed中但不在_key_pressed_state中）
            new_keys = current_pressed - set(self._key_pressed_state.keys())
            
            if new_keys:
                # 记录新按下的键
                key_pressed = list(new_keys)[0]
                self._key_pressed_state[key_pressed] = True
                break
            
            # 更新按键状态
            for key in list(self._key_pressed_state.keys()):
                if key not in current_pressed:
                    # 键已释放，从状态中移除
                    del self._key_pressed_state[key]
            
            time.sleep(0.05)
        
        # 第二步：等待按键释放
        while key_pressed in self._key_pressed_state:
            current_pressed = set(keys_pressed())
            if key_pressed not in current_pressed:
                # 按键已释放
                del self._key_pressed_state[key_pressed]
                break
            time.sleep(0.05)
        
        # 按键已按下并释放，记录按键
        self.keys = [key_pressed]
        
        legal = state.getLegalActions(self.index)
        move = self.getMove(legal)

        # 回合制：空格键表示不走（STOP）
        # 检查是否有空格键
        if 'space' in self.keys or ' ' in self.keys:
            if Directions.STOP in legal:
                move = Directions.STOP
                self.lastMove = move
                return move

        # 如果没有有效移动，且上次移动合法，继续上次方向
        if move == Directions.STOP:
            if self.lastMove in legal:
                move = self.lastMove
            else:
                # 如果上次移动不合法，必须选择一个合法动作
                if Directions.STOP in legal:
                    move = Directions.STOP
                else:
                    move = random.choice(legal)

        # STOP_KEY (q) 表示停止
        if (self.STOP_KEY in self.keys) and Directions.STOP in legal: 
            move = Directions.STOP

        # 确保移动合法
        if move not in legal:
            move = random.choice(legal)

        self.lastMove = move
        return move

    def getMove(self, legal):
        move = Directions.STOP
        if   (self.WEST_KEY in self.keys or 'Left' in self.keys) and Directions.WEST in legal:  move = Directions.WEST
        if   (self.EAST_KEY in self.keys or 'Right' in self.keys) and Directions.EAST in legal: move = Directions.EAST
        if   (self.NORTH_KEY in self.keys or 'Up' in self.keys) and Directions.NORTH in legal:   move = Directions.NORTH
        if   (self.SOUTH_KEY in self.keys or 'Down' in self.keys) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move

class KeyboardAgent2(KeyboardAgent):
    """
    A second agent controlled by the keyboard.
    """
    # NOTE: Arrow keys also work.
    WEST_KEY  = 'j'
    EAST_KEY  = "l"
    NORTH_KEY = 'i'
    SOUTH_KEY = 'k'
    STOP_KEY = 'u'

    def getMove(self, legal):
        move = Directions.STOP
        if   (self.WEST_KEY in self.keys) and Directions.WEST in legal:  move = Directions.WEST
        if   (self.EAST_KEY in self.keys) and Directions.EAST in legal: move = Directions.EAST
        if   (self.NORTH_KEY in self.keys) and Directions.NORTH in legal:   move = Directions.NORTH
        if   (self.SOUTH_KEY in self.keys) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
