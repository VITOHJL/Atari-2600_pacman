# ghostAgents.py
# --------------
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
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util
import search

class GhostAgent( Agent ):
    def __init__( self, index ):
        self.index = index

    def getAction( self, state ):
        dist = self.getDistribution(state)
        if len(dist) == 0:
            return Directions.STOP
        else:
            return util.chooseFromDistribution( dist )

    def getDistribution(self, state):
        "Returns a Counter encoding a distribution over actions from the provided state."
        util.raiseNotDefined()

class RandomGhost( GhostAgent ):
    "A ghost that chooses a legal action uniformly at random."
    def getDistribution( self, state ):
        dist = util.Counter()
        for a in state.getLegalActions( self.index ): dist[a] = 1.0
        dist.normalize()
        return dist

class GhostPositionSearchProblem:
    """
    A search problem for Ghost to find path to Pac-Man position.
    Uses A* algorithm to find optimal path.
    """
    def __init__(self, gameState, ghostIndex, goal):
        self.walls = gameState.getWalls()
        self.startState = gameState.getGhostPosition(ghostIndex)
        self.goal = goal
        self.ghostIndex = ghostIndex
        self.gameState = gameState
        # 保存初始状态以便在getSuccessors中使用
        self.initialGameState = gameState

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        return state == self.goal

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.
        Note: We need to respect Ghost's movement rules (no reverse, no stop).
        """
        successors = []
        # 从当前位置计算所有可能的方向
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                successors.append((nextState, action, 1))
        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions.
        """
        if actions == None:
            return 999999
        x, y = self.getStartState()
        cost = 0
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost


class DirectionalGhost( GhostAgent ):
    "A ghost that uses A* algorithm to rush Pacman, or flee when scared."
    def __init__( self, index, prob_attack=0.8, prob_scaredFlee=0.8 ):
        self.index = index
        self.prob_attack = prob_attack
        self.prob_scaredFlee = prob_scaredFlee

    def getDistribution( self, state ):
        # Read variables from state
        ghostState = state.getGhostState( self.index )
        legalActions = state.getLegalActions( self.index )
        pos = state.getGhostPosition( self.index )
        isScared = ghostState.scaredTimer > 0
        pacmanPosition = state.getPacmanPosition()

        # 使用A*算法找到最短路径（正常状态）或最长路径（害怕状态）
        bestActions = []
        try:
            if isScared:
                # 害怕状态：使用距离计算找最远的位置（更简单可靠）
                bestActions = self._fallbackToDistance(legalActions, pos, pacmanPosition, isScared)
            else:
                # 正常状态：使用A*算法找到最短路径
                problem = GhostPositionSearchProblem(state, self.index, pacmanPosition)
                # 使用A*算法搜索路径（使用曼哈顿距离作为启发式）
                path = search.aStarSearch(problem, manhattanDistance)
                
                if path and len(path) > 0:
                    # 路径的第一步就是最佳行动
                    bestAction = path[0]
                    # 检查这个行动是否在当前合法行动中（考虑不能掉头的规则）
                    if bestAction in legalActions:
                        bestActions = [bestAction]
                    else:
                        # 如果A*返回的行动不在合法行动中（可能因为不能掉头），回退到距离计算
                        bestActions = self._fallbackToDistance(legalActions, pos, pacmanPosition, isScared)
                else:
                    # A*找不到路径，回退到距离计算
                    bestActions = self._fallbackToDistance(legalActions, pos, pacmanPosition, isScared)
        except Exception as e:
            # 如果A*失败，回退到距离计算
            # print(f"A* search failed: {e}")  # 调试用
            bestActions = self._fallbackToDistance(legalActions, pos, pacmanPosition, isScared)

        # 如果没有找到最佳行动，使用所有合法行动
        if not bestActions:
            bestActions = legalActions

        # Construct distribution
        dist = util.Counter()
        if isScared:
            bestProb = self.prob_scaredFlee
        else:
            bestProb = self.prob_attack
        
        for a in bestActions: 
            dist[a] = bestProb / len(bestActions)
        for a in legalActions: 
            dist[a] += ( 1-bestProb ) / len(legalActions)
        dist.normalize()
        return dist

    def _fallbackToDistance(self, legalActions, pos, pacmanPosition, isScared):
        """回退方法：使用曼哈顿距离计算最佳行动"""
        actionVectors = [Actions.directionToVector( a, 1.0 ) for a in legalActions]
        newPositions = [( pos[0]+a[0], pos[1]+a[1] ) for a in actionVectors]
        distancesToPacman = [manhattanDistance( pos, pacmanPosition ) for pos in newPositions]
        if isScared:
            bestScore = max( distancesToPacman )
        else:
            bestScore = min( distancesToPacman )
        return [action for action, distance in zip( legalActions, distancesToPacman ) if distance == bestScore]
