# pacman.py
# ---------
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


"""
Pacman.py holds the logic for the classic pacman game along with the main
code to run a game.  This file is divided into three sections:

  (i)  Your interface to the pacman world:
          Pacman is a complex environment.  You probably don't want to
          read through all of the code we wrote to make the game runs
          correctly.  This section contains the parts of the code
          that you will need to understand in order to complete the
          project.  There is also some code in game.py that you should
          understand.

  (ii)  The hidden secrets of pacman:
          This section contains all of the logic code that the pacman
          environment uses to decide who can move where, who dies when
          things collide, etc.  You shouldn't need to read this section
          of code, but you can if you want.

  (iii) Framework to start a game:
          The final section contains the code for reading the command
          you use to set up the game, then starting up a new game, along with
          linking in all the external parts (agent functions, graphics).
          Check this section out to see all the options available to you.

To play your first game, type 'python pacman.py' from the command line.
The keys are 'a', 's', 'd', and 'w' to move (or arrow keys).  Have fun!
"""
from game import GameStateData
from game import Game
from game import Directions
from game import Actions
from game import Configuration
from util import nearestPoint
from util import manhattanDistance
import util, layout
import sys, types, time, random, os

###################################################
# YOUR INTERFACE TO THE PACMAN WORLD: A GameState #
###################################################

class GameState:
    """
    A GameState specifies the full game state, including the food, capsules,
    agent configurations and score changes.

    GameStates are used by the Game object to capture the actual state of the game and
    can be used by agents to reason about the game.

    Much of the information in a GameState is stored in a GameStateData object.  We
    strongly suggest that you access that data via the accessor methods below rather
    than referring to the GameStateData object directly.

    Note that in classic Pacman, Pacman is always agent 0.
    """

    ####################################################
    # Accessor methods: use these to access state data #
    ####################################################

    # static variable keeps track of which states have had getLegalActions called
    explored = set()
    def getAndResetExplored():
        tmp = GameState.explored.copy()
        GameState.explored = set()
        return tmp
    getAndResetExplored = staticmethod(getAndResetExplored)

    def getLegalActions( self, agentIndex=0 ):
        """
        Returns the legal actions for the agent specified.
        """
#        GameState.explored.add(self)
        if self.isWin() or self.isLose(): return []

        if agentIndex == 0:  # Pacman is moving
            return PacmanRules.getLegalActions( self )
        else:
            return GhostRules.getLegalActions( self, agentIndex )

    def generateSuccessor( self, agentIndex, action):
        """
        Returns the successor state after the specified agent takes the action.
        """
        # Check that successors exist
        if self.isWin() or self.isLose(): raise Exception('Can\'t generate a successor of a terminal state.')

        # Copy current state
        state = GameState(self)

        # Let agent's logic deal with its action's effects on the board
        if agentIndex == 0:  # Pacman is moving
            state.data._eaten = [False for i in range(state.getNumAgents())]
            PacmanRules.applyAction( state, action )
        else:                # A ghost is moving
            GhostRules.applyAction( state, action, agentIndex )

        # Time passes
        if agentIndex == 0:
            # 走路不消耗分数（移除TIME_PENALTY）
            # state.data.scoreChange += -TIME_PENALTY # Penalty for waiting around
            pass
        else:
            GhostRules.decrementTimer( state.data.agentStates[agentIndex] )

        # Resolve multi-agent effects
        GhostRules.checkDeath( state, agentIndex )

        # Book keeping
        state.data._agentMoved = agentIndex
        state.data.score += state.data.scoreChange
        GameState.explored.add(self)
        GameState.explored.add(state)
        return state

    def getLegalPacmanActions( self ):
        return self.getLegalActions( 0 )

    def generatePacmanSuccessor( self, action ):
        """
        Generates the successor state after the specified pacman move
        """
        return self.generateSuccessor( 0, action )

    def getPacmanState( self ):
        """
        Returns an AgentState object for pacman (in game.py)

        state.pos gives the current position
        state.direction gives the travel vector
        """
        return self.data.agentStates[0].copy()

    def getPacmanPosition( self ):
        return self.data.agentStates[0].getPosition()

    def getGhostStates( self ):
        return self.data.agentStates[1:]

    def getGhostState( self, agentIndex ):
        if agentIndex == 0 or agentIndex >= self.getNumAgents():
            raise Exception("Invalid index passed to getGhostState")
        return self.data.agentStates[agentIndex]

    def getGhostPosition( self, agentIndex ):
        if agentIndex == 0:
            raise Exception("Pacman's index passed to getGhostPosition")
        return self.data.agentStates[agentIndex].getPosition()

    def getGhostPositions(self):
        return [s.getPosition() for s in self.getGhostStates()]

    def getNumAgents( self ):
        return len( self.data.agentStates )

    def getScore( self ):
        return float(self.data.score)

    def getCapsules(self):
        """
        Returns a list of positions (x,y) of the remaining capsules.
        """
        return self.data.capsules

    def getNumFood( self ):
        return self.data.food.count()

    def getFood(self):
        """
        Returns a Grid of boolean food indicator variables.

        Grids can be accessed via list notation, so to check
        if there is food at (x,y), just call

        currentFood = state.getFood()
        if currentFood[x][y] == True: ...
        """
        return self.data.food

    def getWalls(self):
        """
        Returns a Grid of boolean wall indicator variables.

        Grids can be accessed via list notation, so to check
        if there is a wall at (x,y), just call

        walls = state.getWalls()
        if walls[x][y] == True: ...
        """
        return self.data.layout.walls

    def hasFood(self, x, y):
        return self.data.food[x][y]

    def hasWall(self, x, y):
        return self.data.layout.walls[x][y]

    def isLose( self ):
        return self.data._lose

    def isWin( self ):
        return self.data._win

    #############################################
    #             Helper methods:               #
    # You shouldn't need to call these directly #
    #############################################

    def __init__( self, prevState = None ):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState != None: # Initial state
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy( self ):
        state = GameState( self )
        state.data = self.data.deepCopy()
        return state

    def __eq__( self, other ):
        """
        Allows two states to be compared.
        """
        return hasattr(other, 'data') and self.data == other.data

    def __hash__( self ):
        """
        Allows states to be keys of dictionaries.
        """
        return hash( self.data )

    def __str__( self ):

        return str(self.data)

    def initialize( self, layout, numGhostAgents=1000 ):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.data.initialize(layout, numGhostAgents)

############################################################################
#                     THE HIDDEN SECRETS OF PACMAN                         #
#                                                                          #
# You shouldn't need to look through the code in this section of the file. #
############################################################################

SCARED_TIME = 40    # Moves ghosts are scared
COLLISION_TOLERANCE = 0.7 # How close ghosts must be to Pacman to kill
TIME_PENALTY = 1 # Number of points lost each round

class ClassicGameRules:
    """
    These game rules manage the control flow of a game, deciding when
    and how the game starts and ends.
    """
    def __init__(self, timeout=30):
        self.timeout = timeout

    def newGame( self, layout, pacmanAgent, ghostAgents, display, quiet = False, catchExceptions=False):
        agents = [pacmanAgent] + ghostAgents  # 使用所有提供的鬼，不受地图中鬼数量限制
        initState = GameState()
        initState.initialize( layout, len(ghostAgents) )  # 使用实际提供的鬼数量
        game = Game(agents, display, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return game

    def process(self, state, game):
        """
        Checks to see whether it is time to end the game.
        """
        # 检查是否完成一轮（所有食物被吃光）
        if hasattr(state.data, '_roundComplete') and state.data._roundComplete:
            self.startNewRound(state, game)
            state.data._roundComplete = False
        
        if state.isWin(): self.win(state, game)
        if state.isLose(): self.lose(state, game)

    def win( self, state, game ):
        if not self.quiet: print("Pacman emerges victorious! Score: %d" % state.data.score)
        game.gameOver = True

    def lose( self, state, game ):
        if not self.quiet: print("Pacman died! Score: %d" % state.data.score)
        game.gameOver = True

    def startNewRound(self, state, game):
        """
        开始新一轮：所有食物被吃光后触发
        - 糖豆人生命+1
        - 所有鬼回到重置位置
        - Pac-Man也回到初始位置
        - 食物、能量豆全部刷新
        - 积分继续累计
        - 之前吃过鬼的次数也继续累计
        """
        if not self.quiet: 
            print("Round Complete! Starting new round... Lives: %d -> %d" % (state.data.lives, state.data.lives + 1))
        
        # 生命+1
        state.data.lives += 1
        
        # 刷新食物和能量豆（从initialState复制，确保是初始状态）
        initialState = self.initialState
        state.data.food = initialState.data.food.deepCopy()
        state.data.capsules = initialState.data.capsules[:]
        
        # 重置所有agent位置到初始位置
        # 重置Pac-Man位置
        pacmanState = state.data.agentStates[0]
        pacmanState.configuration = pacmanState.start
        
        # 重置所有鬼的位置
        for index in range(1, len(state.data.agentStates)):
            ghostState = state.data.agentStates[index]
            # 创建新的Configuration对象，确保configuration和start是独立的
            from game import Configuration
            start_pos = ghostState.start.getPosition()
            start_dir = ghostState.start.getDirection()
            ghostState.configuration = Configuration(start_pos, start_dir)
            ghostState.scaredTimer = 0
            ghostState.respawnTimer = 0  # 重置复活状态
        
        # 清除可能阻止游戏继续的标志
        state.data._win = False
        state.data._lose = False
        
        # 积分和ghostsEatenInRow保持不变（继续累计）
        # 不需要做任何操作，因为它们已经在state.data中

    def getProgress(self, game):
        return float(game.state.getNumFood()) / self.initialState.getNumFood()

    def agentCrash(self, game, agentIndex):
        if agentIndex == 0:
            print("Pacman crashed")
        else:
            print("A ghost crashed")

    def getMaxTotalTime(self, agentIndex):
        return self.timeout

    def getMaxStartupTime(self, agentIndex):
        return self.timeout

    def getMoveWarningTime(self, agentIndex):
        return self.timeout

    def getMoveTimeout(self, agentIndex):
        return self.timeout

    def getMaxTimeWarnings(self, agentIndex):
        return 0

class PacmanRules:
    """
    These functions govern how pacman interacts with his environment under
    the classic game rules.
    """
    PACMAN_SPEED=1

    def getLegalActions( state ):
        """
        Returns a list of possible actions.
        For Pac-Man, portals (Q) are not considered walls, allowing movement through them.
        """
        # 创建 walls 的副本，将传送门位置标记为非墙（仅对 Pac-Man）
        walls = state.data.layout.walls.copy()
        portals = getattr(state.data.layout, 'portals', [])
        for portal_pos in portals:
            x, y = portal_pos
            walls[x][y] = False  # 传送门对 Pac-Man 来说不是墙
        
        return Actions.getPossibleActions( state.getPacmanState().configuration, walls )
    getLegalActions = staticmethod( getLegalActions )

    def applyAction( state, action ):
        """
        Edits the state to reflect the results of the action.
        """
        legal = PacmanRules.getLegalActions( state )
        if action not in legal:
            raise Exception("Illegal action " + str(action))

        pacmanState = state.data.agentStates[0]

        # Update Configuration
        vector = Actions.directionToVector( action, PacmanRules.PACMAN_SPEED )
        pacmanState.configuration = pacmanState.configuration.generateSuccessor( vector )

        # 检查传送门传送
        next = pacmanState.configuration.getPosition()
        nearest = nearestPoint( next )
        if manhattanDistance( nearest, next ) <= 0.5 :
            # 检查是否在传送门上
            portals = getattr(state.data.layout, 'portals', [])
            if nearest in portals and len(portals) == 2:
                # 找到另一个传送门
                other_portal = portals[0] if portals[1] == nearest else portals[1]
                target_x, target_y = other_portal
                layout = state.data.layout
                
                # 判断"内侧"方向：朝向地图中心的方向
                # 地图中心y坐标
                center_y = layout.height / 2.0
                
                # 如果传送门在中心上方（y值大），内侧是下方（y-1，朝向中心）
                # 如果传送门在中心下方（y值小），内侧是上方（y+1，朝向中心）
                if target_y > center_y:
                    # 传送门在上半部分，内侧是下方
                    inner_direction = (0, -1)  # 向下
                    outer_direction = (0, 1)   # 向上
                else:
                    # 传送门在下半部分，内侧是上方
                    inner_direction = (0, 1)   # 向上
                    outer_direction = (0, -1)   # 向下
                
                # 优先尝试内侧方向
                inner_x = target_x + inner_direction[0]
                inner_y = target_y + inner_direction[1]
                if (0 <= inner_x < layout.width and 0 <= inner_y < layout.height and 
                    not layout.walls[inner_x][inner_y]):
                    target_pos = (inner_x, inner_y)
                # 如果内侧不行，尝试外侧方向
                else:
                    outer_x = target_x + outer_direction[0]
                    outer_y = target_y + outer_direction[1]
                    if (0 <= outer_x < layout.width and 0 <= outer_y < layout.height and 
                        not layout.walls[outer_x][outer_y]):
                        target_pos = (outer_x, outer_y)
                    # 如果内外侧都不行，尝试左右
                    elif target_x > 0 and not layout.walls[target_x - 1][target_y]:
                        target_pos = (target_x - 1, target_y)
                    elif target_x < layout.width - 1 and not layout.walls[target_x + 1][target_y]:
                        target_pos = (target_x + 1, target_y)
                    else:
                        # 如果都不行，就传送到传送门本身的位置
                        target_pos = other_portal
                
                # 传送Pac-Man到目标位置
                # 保持当前方向
                current_dir = pacmanState.configuration.direction
                pacmanState.configuration = Configuration(target_pos, current_dir)
                # 更新位置用于后续的吃豆逻辑
                next = target_pos
                nearest = target_pos
            
            # Remove food
            PacmanRules.consume( nearest, state )
    applyAction = staticmethod( applyAction )

    def consume( position, state ):
        x,y = position
        # Eat food (糖豆：1分)
        if state.data.food[x][y]:
            state.data.scoreChange += 1
            state.data.food = state.data.food.copy()
            state.data.food[x][y] = False
            state.data._foodEaten = position
            # TODO: cache numFood?
            numFood = state.getNumFood()
            if numFood == 0 and not state.data._lose:
                state.data.scoreChange += 500
                # 不直接设置_win，而是设置一个标志，让游戏规则处理新一轮
                state.data._roundComplete = True
        # Eat capsule (能量丸)
        if( position in state.getCapsules() ):
            state.data.capsules.remove( position )
            state.data._capsuleEaten = position
            # 能量丸分数：5分
            state.data.scoreChange += 5
            # Reset all ghosts' scared timers
            # 白色鬼持续时间随着吃的鬼数量增多而减少
            # 基础时间40回合，每吃一个鬼减少2回合，最小为0回合
            # 第0个鬼被吃后：40回合
            # 第1个鬼被吃后：38回合
            # 第2个鬼被吃后：36回合
            # ...
            # 第20个及以后：0回合（不变成白色，不能被吃，但会躲避）
            scaredTime = max(0, SCARED_TIME - state.data.ghostsEatenInRow * 2)
            for index in range( 1, len( state.data.agentStates ) ):
                state.data.agentStates[index].scaredTimer = scaredTime
    consume = staticmethod( consume )

class GhostRules:
    """
    These functions dictate how ghosts interact with their environment.
    """
    GHOST_SPEED=1.0
    def getLegalActions( state, ghostIndex ):
        """
        Ghosts cannot stop, and cannot turn around unless they
        reach a dead end, but can turn 90 degrees at intersections.
        """
        ghostState = state.getGhostState( ghostIndex )
        # 如果鬼处于死亡状态（等待复活），不移动
        if ghostState.respawnTimer > 0:
            return []  # 返回空列表，鬼不移动
        
        conf = ghostState.configuration
        possibleActions = Actions.getPossibleActions( conf, state.data.layout.walls )
        reverse = Actions.reverseDirection( conf.direction )
        if Directions.STOP in possibleActions:
            possibleActions.remove( Directions.STOP )
        if reverse in possibleActions and len( possibleActions ) > 1:
            possibleActions.remove( reverse )
        return possibleActions
    getLegalActions = staticmethod( getLegalActions )

    def applyAction( state, action, ghostIndex):
        ghostState = state.data.agentStates[ghostIndex]
        # 如果鬼处于死亡状态，不移动
        if ghostState.respawnTimer > 0:
            return  # 不执行任何动作

        legal = GhostRules.getLegalActions( state, ghostIndex )
        if action not in legal:
            raise Exception("Illegal ghost action " + str(action))

        speed = GhostRules.GHOST_SPEED
        if ghostState.scaredTimer > 0: speed /= 2.0
        vector = Actions.directionToVector( action, speed )
        ghostState.configuration = ghostState.configuration.generateSuccessor( vector )
    applyAction = staticmethod( applyAction )

    def decrementTimer( ghostState):
        timer = ghostState.scaredTimer
        if timer == 1:
            ghostState.configuration.pos = nearestPoint( ghostState.configuration.pos )
        ghostState.scaredTimer = max( 0, timer - 1 )
    decrementTimer = staticmethod( decrementTimer )

    def checkDeath( state, agentIndex):
        pacmanPosition = state.getPacmanPosition()
        if agentIndex == 0: # Pacman just moved; Anyone can kill him
            for index in range( 1, len( state.data.agentStates ) ):
                ghostState = state.data.agentStates[index]
                # 跳过死亡状态的鬼（它们不应该与Pac-Man碰撞）
                if ghostState.respawnTimer > 0:
                    continue
                ghostPosition = ghostState.configuration.getPosition()
                if GhostRules.canKill( pacmanPosition, ghostPosition ):
                    GhostRules.collide( state, ghostState, index )
        else:
            ghostState = state.data.agentStates[agentIndex]
            # 跳过死亡状态的鬼（它们不应该与Pac-Man碰撞）
            if ghostState.respawnTimer > 0:
                return
            ghostPosition = ghostState.configuration.getPosition()
            if GhostRules.canKill( pacmanPosition, ghostPosition ):
                GhostRules.collide( state, ghostState, agentIndex )
    checkDeath = staticmethod( checkDeath )

    def collide( state, ghostState, agentIndex):
        if ghostState.scaredTimer > 0:
            # 吃鬼分数递增：10 × 2^n（n为连续吃掉的第n个鬼）
            # 第1个=20分，第2个=40分，第3个=80分，第4个=160分
            state.data.ghostsEatenInRow += 1
            points = 10 * (2 ** state.data.ghostsEatenInRow)
            state.data.scoreChange += points
            
            # 鬼被吃：设置复活倒计时
            # 复活时间固定为16回合
            ghostState.respawnTimer = 16
            
            # 将鬼移动到初始位置（但处于死亡状态，不立即复活）
            GhostRules.placeGhost(state, ghostState)
            ghostState.scaredTimer = 0
            # Added for first-person
            state.data._eaten[agentIndex] = True
        else:
            # Pac-Man被鬼吃：失去一条生命
            if not state.data._win:
                state.data.lives -= 1
                if state.data.lives <= 0:
                    # 没有生命了，游戏结束
                    state.data.scoreChange -= 500
                    state.data._lose = True
                else:
                    # 还有生命，重置位置（不结束游戏）
                    # 重置Pac-Man位置到起始位置
                    pacmanState = state.data.agentStates[0]
                    pacmanState.configuration = pacmanState.start
                    # 重置所有鬼的位置
                    for index in range(1, len(state.data.agentStates)):
                        ghostState = state.data.agentStates[index]
                        ghostState.configuration = ghostState.start
                        ghostState.scaredTimer = 0
                        # 重置复活状态（如果鬼处于死亡状态，保持死亡状态）
                        # 注意：这里不重置respawnTimer，让鬼继续等待复活
                    # 重置连续吃鬼计数
                    state.data.ghostsEatenInRow = 0
    collide = staticmethod( collide )

    def canKill( pacmanPosition, ghostPosition ):
        return manhattanDistance( ghostPosition, pacmanPosition ) <= COLLISION_TOLERANCE
    canKill = staticmethod( canKill )

    def placeGhost(state, ghostState):
        # 创建新的Configuration对象，而不是直接引用start
        # 这样可以确保configuration和start是独立的
        start_pos = ghostState.start.getPosition()
        start_dir = ghostState.start.getDirection()
        ghostState.configuration = Configuration(start_pos, start_dir)
    placeGhost = staticmethod( placeGhost )

#############################
# FRAMEWORK TO START A GAME #
#############################

def default(str):
    return str + ' [Default: %default]'

def parseAgentArgs(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key,val = p, 1
        opts[key] = val
    return opts

def readCommand( argv ):
    """
    Processes the command used to run pacman from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python pacman.py <options>
    EXAMPLES:   (1) python pacman.py
                    - starts an interactive game
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - starts an interactive game on a smaller board, zoomed in
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-l', '--layout', dest='layout',
                      help=default('the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='mediumClassic')
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default('the agent TYPE in the pacmanAgents module to use'),
                      metavar='TYPE', default='KeyboardAgent')
    parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='Generate minimal output and no graphics', default=False)
    parser.add_option('-g', '--ghosts', dest='ghost',
                      help=default('the ghost agent TYPE in the ghostAgents module to use'),
                      metavar = 'TYPE', default='RandomGhost')
    parser.add_option('-k', '--numghosts', type='int', dest='numGhosts',
                      help=default('The maximum number of ghosts to use'), default=4)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    parser.add_option('--replay', dest='gameToReplay',
                      help='A recorded game file (pickle) to replay', default=None)
    parser.add_option('-a','--agentArgs',dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    parser.add_option('--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)
    parser.add_option('-c', '--catchExceptions', action='store_true', dest='catchExceptions',
                      help='Turns on exception handling and timeouts during games', default=False)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum length of time an agent can spend computing in a single game'), default=30)

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed: random.seed('cs188')

    # Choose a layout
    args['layout'] = layout.getLayout( options.layout )
    if args['layout'] == None: raise Exception("The layout " + options.layout + " cannot be found")

    # Choose a Pacman agent
    noKeyboard = options.gameToReplay == None and (options.textGraphics or options.quietGraphics)
    pacmanType = loadAgent(options.pacman, noKeyboard)
    agentOpts = parseAgentArgs(options.agentArgs)
    if options.numTraining > 0:
        args['numTraining'] = options.numTraining
        if 'numTraining' not in agentOpts: agentOpts['numTraining'] = options.numTraining
    pacman = pacmanType(**agentOpts) # Instantiate Pacman with agentArgs
    args['pacman'] = pacman

    # Don't display training games
    if 'numTrain' in agentOpts:
        options.numQuiet = int(agentOpts['numTrain'])
        options.numIgnore = int(agentOpts['numTrain'])

    # Choose a ghost agent
    ghostType = loadAgent(options.ghost, noKeyboard)
    args['ghosts'] = [ghostType( i+1 ) for i in range( options.numGhosts )]

    # Choose a display format
    if options.quietGraphics:
        import textDisplay
        args['display'] = textDisplay.NullGraphics()
    elif options.textGraphics:
        import textDisplay
        textDisplay.SLEEP_TIME = options.frameTime
        args['display'] = textDisplay.PacmanGraphics()
    else:
        import graphicsDisplay
        args['display'] = graphicsDisplay.PacmanGraphics(options.zoom, frameTime = options.frameTime)
    args['numGames'] = options.numGames
    args['record'] = options.record
    args['catchExceptions'] = options.catchExceptions
    args['timeout'] = options.timeout

    # Special case: recorded games don't use the runGames method or args structure
    if options.gameToReplay != None:
        print('Replaying recorded game %s.' % options.gameToReplay)
        import pickle
        f = open(options.gameToReplay, 'rb')
        try: recorded = pickle.load(f)
        finally: f.close()
        recorded['display'] = args['display']
        replayGame(**recorded)
        sys.exit(0)

    return args

def loadAgent(pacman, nographics):
    # Looks through all pythonPath Directories for the right module,
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(';') == -1:
        pythonPathDirs = pythonPathStr.split(':')
    else:
        pythonPathDirs = pythonPathStr.split(';')
    pythonPathDirs.append('.')

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir): continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if pacman in dir(module):
                if nographics and modulename == 'keyboardAgents.py':
                    raise Exception('Using the keyboard requires graphics (not text display)')
                return getattr(module, pacman)
    raise Exception('The agent ' + pacman + ' is not specified in any *Agents.py.')

def replayGame( layout, actions, display ):
    import pacmanAgents, ghostAgents
    rules = ClassicGameRules()
    agents = [pacmanAgents.GreedyAgent()] + [ghostAgents.RandomGhost(i+1) for i in range(layout.getNumGhosts())]
    game = rules.newGame( layout, agents[0], agents[1:], display )
    state = game.state
    display.initialize(state.data)

    for action in actions:
            # Execute the action
        state = state.generateSuccessor( *action )
        # Change the display
        display.update( state.data )
        # Allow for game specific conditions (winning, losing, etc.)
        rules.process(state, game)

    display.finish()

def runGames( layout, pacman, ghosts, display, numGames, record, numTraining = 0, catchExceptions=False, timeout=30 ):
    import __main__
    __main__.__dict__['_display'] = display

    rules = ClassicGameRules(timeout)
    games = []

    for i in range( numGames ):
        beQuiet = i < numTraining
        if beQuiet:
                # Suppress output and graphics
            import textDisplay
            gameDisplay = textDisplay.NullGraphics()
            rules.quiet = True
        else:
            gameDisplay = display
            rules.quiet = False
        game = rules.newGame( layout, pacman, ghosts, gameDisplay, beQuiet, catchExceptions)
        game.run()
        if not beQuiet: games.append(game)

        if record:
            import time, pickle
            fname = ('recorded-game-%d' % (i + 1)) +  '-'.join([str(t) for t in time.localtime()[1:6]])
            f = open(fname, 'wb')
            components = {'layout': layout, 'actions': game.moveHistory}
            pickle.dump(components, f)
            f.close()

    if (numGames-numTraining) > 0:
        scores = [game.state.getScore() for game in games]
        wins = [game.state.isWin() for game in games]
        winRate = wins.count(True)/ float(len(wins))
        print('Average Score:', sum(scores) / float(len(scores)))
        print('Scores:       ', ', '.join([str(score) for score in scores]))
        print('Win Rate:      %d/%d (%.2f)' % (wins.count(True), len(wins), winRate))
        print('Record:       ', ', '.join([ ['Loss', 'Win'][int(w)] for w in wins]))

    return games

if __name__ == '__main__':
    """
    The main function called when pacman.py is run
    from the command line:

    > python pacman.py

    See the usage string for more details.

    > python pacman.py --help
    """
    args = readCommand( sys.argv[1:] ) # Get game components based on input
    runGames( **args )

    # import cProfile
    # cProfile.run("runGames( **args )")
    pass
