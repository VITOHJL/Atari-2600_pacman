# graphicsDisplay.py
# ------------------
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


from graphicsUtils import *
import math, time
from game import Directions
import tkinter
import graphicsUtils

###########################
#  GRAPHICS DISPLAY CODE  #
###########################

# Most code by Dan Klein and John Denero written or rewritten for cs188, UC Berkeley.
# Some code from a Pacman implementation by LiveWires, and used / modified with permission.

DEFAULT_GRID_SIZE = 30.0
DEFAULT_GRID_WIDTH = 30.0  # 网格宽度
DEFAULT_GRID_HEIGHT = 80.0  # 网格高度
INFO_PANE_HEIGHT = 35
BACKGROUND_COLOR = formatColor(20/255,65/255,202/255)  # 背景颜色，RGB值范围0-1，例如 formatColor(0.1,0.1,0.1) 为深灰色
WALL_COLOR = formatColor(231.0/255.0, 197.0/255.0, 82.0/255.0)  # 土黄色
PORTAL_COLOR = formatColor(1.0, 0.0, 0.0)  # 红色传送门墙
INFO_PANE_COLOR = formatColor(.4,.4,0)
SCORE_COLOR = formatColor(.9, .9, .9)
PACMAN_OUTLINE_WIDTH = 2
PACMAN_CAPTURE_OUTLINE_WIDTH = 4

GHOST_COLORS = []
GHOST_COLORS.append(formatColor(.9,0,0)) # Red
GHOST_COLORS.append(formatColor(.98,.41,.07)) # Orange
GHOST_COLORS.append(formatColor(.1,.75,.7)) # Green
GHOST_COLORS.append(formatColor(1.0,0.6,0.0)) # Yellow
GHOST_COLORS.append(formatColor(.4,0.13,0.91)) # Purple

TEAM_COLORS = GHOST_COLORS[:2]

GHOST_SHAPE = [
    ( 0,    0.3 ),
    ( 0.25, 0.75 ),
    ( 0.5,  0.3 ),
    ( 0.75, 0.75 ),
    ( 0.75, -0.5 ),
    ( 0.5,  -0.75 ),
    (-0.5,  -0.75 ),
    (-0.75, -0.5 ),
    (-0.75, 0.75 ),
    (-0.5,  0.3 ),
    (-0.25, 0.75 )
  ]
GHOST_SIZE = 0.65
SCARED_COLOR = formatColor(1,1,1)

GHOST_VEC_COLORS = [colorToVector(c) for c in GHOST_COLORS]

PACMAN_COLOR = formatColor(255.0/255.0,255.0/255.0,61.0/255)
PACMAN_SCALE = 0.5
#pacman_speed = 0.25

# Food
FOOD_COLOR = formatColor(231/255,197/255,82/255)  # 白色，可以修改为其他颜色，例如 formatColor(1,0,0) 为红色
FOOD_WIDTH_SCALE = 0.5  # 食物宽度相对于网格宽度的比例（0.0-1.0）
FOOD_HEIGHT_SCALE = 0.05  # 食物高度相对于网格高度的比例（0.0-1.0）
FOOD_SIZE = 0.1  # 保留用于向后兼容

# Laser
LASER_COLOR = formatColor(1,0,0)
LASER_SIZE = 0.02

# Capsule graphics
CAPSULE_COLOR = formatColor(243/255,149/255,221/255)  # 能量球颜色，RGB值范围0-1，例如 formatColor(1,0,0) 为红色
CAPSULE_WIDTH_SCALE = 0.25  # 能量球宽度相对于网格宽度的比例（0.0-1.0）
CAPSULE_HEIGHT_SCALE = 0.3  # 能量球高度相对于网格高度的比例（0.0-1.0）
CAPSULE_SIZE = 0.25  # 保留用于向后兼容

# Drawing walls
WALL_RADIUS = 0.15

class InfoPane:
    def __init__(self, layout, gridWidth, gridHeight):
        self.gridWidth = gridWidth
        self.gridHeight = gridHeight
        self.width = (layout.width) * gridWidth
        self.base = (layout.height + 1) * gridHeight
        self.height = INFO_PANE_HEIGHT
        self.fontSize = 24
        self.textColor = PACMAN_COLOR
        self.drawPane()

    def toScreen(self, pos, y = None):
        """
          Translates a point relative from the bottom left of the info pane.
        """
        if y == None:
            x,y = pos
        else:
            x = pos

        x = self.gridWidth + x # Margin
        y = self.base + y
        return x,y

    def drawPane(self):
        self.scoreText = text( self.toScreen(0, 0  ), self.textColor, "SCORE:    0", "Times", self.fontSize, "bold")

    def initializeGhostDistances(self, distances):
        self.ghostDistanceText = []

        size = 20
        if self.width < 240:
            size = 12
        if self.width < 160:
            size = 10

        for i, d in enumerate(distances):
            t = text( self.toScreen(self.width//2 + self.width//8 * i, 0), GHOST_COLORS[i+1], d, "Times", size, "bold")
            self.ghostDistanceText.append(t)

    def updateScore(self, score, lives=None):
        if lives is not None:
            changeText(self.scoreText, "SCORE: % 4d  LIVES: %d" % (score, lives))
        else:
            changeText(self.scoreText, "SCORE: % 4d" % score)

    def setTeam(self, isBlue):
        text = "RED TEAM"
        if isBlue: text = "BLUE TEAM"
        self.teamText = text( self.toScreen(300, 0  ), self.textColor, text, "Times", self.fontSize, "bold")

    def updateGhostDistances(self, distances):
        if len(distances) == 0: return
        if 'ghostDistanceText' not in dir(self): self.initializeGhostDistances(distances)
        else:
            for i, d in enumerate(distances):
                changeText(self.ghostDistanceText[i], d)

    def drawGhost(self):
        pass

    def drawPacman(self):
        pass

    def drawWarning(self):
        pass

    def clearIcon(self):
        pass

    def updateMessage(self, message):
        pass

    def clearMessage(self):
        pass


class PacmanGraphics:
    def __init__(self, zoom=1.0, frameTime=0.0, capture=False, gridWidth=None, gridHeight=None):
        self.have_window = 0
        self.currentGhostImages = {}
        self.pacmanImage = None
        self.zoom = zoom
        # 如果未指定，使用默认值；如果只指定了一个，另一个使用相同的值
        if gridWidth is None and gridHeight is None:
            self.gridWidth = DEFAULT_GRID_WIDTH * zoom
            self.gridHeight = DEFAULT_GRID_HEIGHT * zoom
        elif gridWidth is None:
            self.gridHeight = gridHeight * zoom
            self.gridWidth = self.gridHeight  # 默认正方形
        elif gridHeight is None:
            self.gridWidth = gridWidth * zoom
            self.gridHeight = self.gridWidth  # 默认正方形
        else:
            self.gridWidth = gridWidth * zoom
            self.gridHeight = gridHeight * zoom
        # 为了向后兼容，保留 gridSize 作为平均大小
        self.gridSize = (self.gridWidth + self.gridHeight) / 2.0
        self.capture = capture
        self.frameTime = frameTime

    def checkNullDisplay(self):
        return False

    def initialize(self, state, isBlue = False):
        self.isBlue = isBlue
        self.startGraphics(state)

        # self.drawDistributions(state)
        self.distributionImages = None  # Initialized lazily
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)

        # Information
        self.previousState = state

    def startGraphics(self, state):
        self.layout = state.layout
        layout = self.layout
        self.width = layout.width
        self.height = layout.height
        self.make_window(self.width, self.height)
        self.infoPane = InfoPane(layout, self.gridWidth, self.gridHeight)
        self.currentState = layout

    def drawDistributions(self, state):
        walls = state.layout.walls
        dist = []
        for x in range(walls.width):
            distx = []
            dist.append(distx)
            for y in range(walls.height):
                ( screen_x, screen_y ) = self.to_screen( (x, y) )
                block = square( (screen_x, screen_y),
                                0.5 * min(self.gridWidth, self.gridHeight),
                                color = BACKGROUND_COLOR,
                                filled = 1, behind=2)
                distx.append(block)
        self.distributionImages = dist

    def drawStaticObjects(self, state):
        layout = self.layout
        self.drawWalls(layout.walls)
        self.food = self.drawFood(layout.food)
        self.capsules = self.drawCapsules(layout.capsules)
        refresh()

    def drawAgentObjects(self, state):
        self.agentImages = [] # (agentState, image)
        for index, agent in enumerate(state.agentStates):
            if agent.isPacman:
                image = self.drawPacman(agent, index)
                self.agentImages.append( (agent, image) )
            else:
                # 跳过死亡状态的鬼（不绘制）
                if hasattr(agent, 'respawnTimer') and agent.respawnTimer > 0:
                    continue
                image = self.drawGhost(agent, index)
                self.agentImages.append( (agent, image) )
        refresh()

    def swapImages(self, agentIndex, newState):
        """
          Changes an image from a ghost to a pacman or vis versa (for capture)
        """
        prevState, prevImage = self.agentImages[agentIndex]
        for item in prevImage: remove_from_screen(item)
        if newState.isPacman:
            image = self.drawPacman(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image )
        else:
            image = self.drawGhost(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image )
        refresh()

    def update(self, newState):
        # 首先检查所有鬼的状态，处理死亡和复活
        for index, agentState in enumerate(newState.agentStates):
            if agentState.isPacman:
                continue
            
            # 确保 agentImages 有足够的元素
            while index >= len(self.agentImages):
                self.agentImages.append((None, []))
            
            prevState, prevImage = self.agentImages[index]
            
            # 如果鬼处于死亡状态，移除其图像（不显示）
            if hasattr(agentState, 'respawnTimer') and agentState.respawnTimer > 0:
                if len(prevImage) > 0:
                    for item in prevImage:
                        remove_from_screen(item)
                    self.agentImages[index] = (agentState, [])
                continue
            
            # 如果鬼从死亡状态复活，需要重新绘制
            if prevState is not None and hasattr(prevState, 'respawnTimer') and prevState.respawnTimer > 0 and len(prevImage) == 0:
                image = self.drawGhost(agentState, index)
                self.agentImages[index] = (agentState, image)
                continue
        
        # 处理移动的agent（正常更新）
        agentIndex = newState._agentMoved
        agentState = newState.agentStates[agentIndex]
        
        # 如果这个agent是死亡状态的鬼，已经在上面的循环中处理了
        if not agentState.isPacman and hasattr(agentState, 'respawnTimer') and agentState.respawnTimer > 0:
            pass  # 已经在上面处理了
        else:
            if self.agentImages[agentIndex][0].isPacman != agentState.isPacman: 
                self.swapImages(agentIndex, agentState)
            prevState, prevImage = self.agentImages[agentIndex]
            if agentState.isPacman:
                self.animatePacman(agentState, prevState, prevImage)
            else:
                self.moveGhost(agentState, agentIndex, prevState, prevImage)
            self.agentImages[agentIndex] = (agentState, prevImage)

        if newState._foodEaten != None:
            self.removeFood(newState._foodEaten, self.food)
        if newState._capsuleEaten != None:
            self.removeCapsule(newState._capsuleEaten, self.capsules)
        # 显示得分和生命数
        lives = getattr(newState, 'lives', None)
        self.infoPane.updateScore(newState.score, lives)
        if 'ghostDistances' in dir(newState):
            self.infoPane.updateGhostDistances(newState.ghostDistances)

    def make_window(self, width, height):
        grid_width = (width-1) * self.gridWidth
        grid_height = (height-1) * self.gridHeight
        screen_width = 2*self.gridWidth + grid_width
        screen_height = 2*self.gridHeight + grid_height + INFO_PANE_HEIGHT

        begin_graphics(screen_width,
                       screen_height,
                       BACKGROUND_COLOR,
                       "CS188 Pacman")

    def drawPacman(self, pacman, index):
        position = self.getPosition(pacman)
        screen_point = self.to_screen(position)
        endpoints = self.getEndpoints(self.getDirection(pacman))

        width = PACMAN_OUTLINE_WIDTH
        outlineColor = PACMAN_COLOR
        fillColor = PACMAN_COLOR

        if self.capture:
            outlineColor = TEAM_COLORS[index % 2]
            fillColor = GHOST_COLORS[index]
            width = PACMAN_CAPTURE_OUTLINE_WIDTH

        # 使用 gridWidth 和 gridHeight 分别绘制椭圆，使其能够像鬼魂一样被拉伸
        radius_x = PACMAN_SCALE * self.gridWidth
        radius_y = PACMAN_SCALE * self.gridHeight
        x, y = screen_point
        x0, x1 = x - radius_x, x + radius_x
        y0, y1 = y - radius_y, y + radius_y
        
        # 处理 endpoints
        if endpoints == None:
            e = [0, 359]
        else:
            e = list(endpoints)
        while e[0] > e[1]: e[1] = e[1] + 360
        
        # 使用 create_arc 绘制椭圆扇形
        # 直接使用 graphicsUtils._canvas，因为它是全局变量
        # 注意：_canvas 在 begin_graphics 调用后才初始化
        from graphicsUtils import _canvas as canvas
        if canvas is None:
            raise RuntimeError("Canvas not initialized. begin_graphics must be called before drawPacman.")
        arc = canvas.create_arc(x0, y0, x1, y1, 
                                 outline=outlineColor, fill=fillColor or outlineColor,
                                 extent=e[1] - e[0], start=e[0], style='pieslice', width=width)
        return [arc]

    def getEndpoints(self, direction, position=(0,0)):
        x, y = position
        pos = x - int(x) + y - int(y)
        width = 30 + 80 * math.sin(math.pi* pos)

        delta = width / 2
        if (direction == 'West'):
            endpoints = (180+delta, 180-delta)
        elif (direction == 'North'):
            endpoints = (90+delta, 90-delta)
        elif (direction == 'South'):
            endpoints = (270+delta, 270-delta)
        else:
            endpoints = (0+delta, 0-delta)
        return endpoints

    def movePacman(self, position, direction, image):
        screenPosition = self.to_screen(position)
        endpoints = self.getEndpoints( direction, position )
        # 使用 gridWidth 和 gridHeight 分别计算椭圆半径，使其能够像鬼魂一样被拉伸
        radius_x = PACMAN_SCALE * self.gridWidth
        radius_y = PACMAN_SCALE * self.gridHeight
        x, y = screenPosition
        x0, x1 = x - radius_x, x + radius_x
        y0, y1 = y - radius_y, y + radius_y
        
        # 处理 endpoints
        if endpoints == None:
            e = [0, 359]
        else:
            e = list(endpoints)
        while e[0] > e[1]: e[1] = e[1] + 360
        
        # 直接更新椭圆的位置和大小
        # 直接使用 graphicsUtils._canvas，因为它是全局变量
        from graphicsUtils import _canvas as canvas
        if canvas is not None:
            canvas.coords(image[0], x0, y0, x1, y1)
            canvas.itemconfig(image[0], start=e[0], extent=e[1] - e[0])
        refresh()

    def animatePacman(self, pacman, prevPacman, image):
        if self.frameTime < 0:
            print('Press any key to step forward, "q" to play')
            keys = wait_for_keys()
            if 'q' in keys:
                self.frameTime = 0.1
        if self.frameTime > 0.01 or self.frameTime < 0:
            start = time.time()
            fx, fy = self.getPosition(prevPacman)
            px, py = self.getPosition(pacman)
            frames = 4.0
            for i in range(1,int(frames) + 1):
                pos = px*i/frames + fx*(frames-i)/frames, py*i/frames + fy*(frames-i)/frames
                self.movePacman(pos, self.getDirection(pacman), image)
                refresh()
                sleep(abs(self.frameTime) / frames)
        else:
            self.movePacman(self.getPosition(pacman), self.getDirection(pacman), image)
        refresh()

    def getGhostColor(self, ghost, ghostIndex):
        if ghost.scaredTimer > 0:
            return SCARED_COLOR
        else:
            return GHOST_COLORS[ghostIndex]

    def drawGhost(self, ghost, agentIndex):
        pos = self.getPosition(ghost)
        dir = self.getDirection(ghost)
        (screen_x, screen_y) = (self.to_screen(pos) )
        coords = []
        for (x, y) in GHOST_SHAPE:
            # 分别使用 gridWidth 和 gridHeight 来缩放 x 和 y 坐标
            coords.append((x*self.gridWidth*GHOST_SIZE + screen_x, y*self.gridHeight*GHOST_SIZE + screen_y))

        colour = self.getGhostColor(ghost, agentIndex)
        body = polygon(coords, colour, filled = 1)
        WHITE = formatColor(1.0, 1.0, 1.0)
        BLACK = formatColor(0.0, 0.0, 0.0)

        dx = 0
        dy = 0
        if dir == 'North':
            dy = -0.2
        if dir == 'South':
            dy = 0.2
        if dir == 'East':
            dx = 0.2
        if dir == 'West':
            dx = -0.2
        # 使用平均尺寸计算眼睛大小
        eye_radius = min(self.gridWidth, self.gridHeight) * GHOST_SIZE * 0.2
        pupil_radius = min(self.gridWidth, self.gridHeight) * GHOST_SIZE * 0.08
        leftEye = circle((screen_x+self.gridWidth*GHOST_SIZE*(-0.3+dx/1.5), screen_y-self.gridHeight*GHOST_SIZE*(0.3-dy/1.5)), eye_radius, WHITE, WHITE)
        rightEye = circle((screen_x+self.gridWidth*GHOST_SIZE*(0.3+dx/1.5), screen_y-self.gridHeight*GHOST_SIZE*(0.3-dy/1.5)), eye_radius, WHITE, WHITE)
        leftPupil = circle((screen_x+self.gridWidth*GHOST_SIZE*(-0.3+dx), screen_y-self.gridHeight*GHOST_SIZE*(0.3-dy)), pupil_radius, BLACK, BLACK)
        rightPupil = circle((screen_x+self.gridWidth*GHOST_SIZE*(0.3+dx), screen_y-self.gridHeight*GHOST_SIZE*(0.3-dy)), pupil_radius, BLACK, BLACK)
        ghostImageParts = []
        ghostImageParts.append(body)
        ghostImageParts.append(leftEye)
        ghostImageParts.append(rightEye)
        ghostImageParts.append(leftPupil)
        ghostImageParts.append(rightPupil)

        return ghostImageParts

    def moveEyes(self, pos, dir, eyes):
        (screen_x, screen_y) = (self.to_screen(pos) )
        dx = 0
        dy = 0
        if dir == 'North':
            dy = -0.2
        if dir == 'South':
            dy = 0.2
        if dir == 'East':
            dx = 0.2
        if dir == 'West':
            dx = -0.2
        # 使用平均尺寸计算眼睛大小
        eye_radius = min(self.gridWidth, self.gridHeight) * GHOST_SIZE * 0.2
        pupil_radius = min(self.gridWidth, self.gridHeight) * GHOST_SIZE * 0.08
        moveCircle(eyes[0],(screen_x+self.gridWidth*GHOST_SIZE*(-0.3+dx/1.5), screen_y-self.gridHeight*GHOST_SIZE*(0.3-dy/1.5)), eye_radius)
        moveCircle(eyes[1],(screen_x+self.gridWidth*GHOST_SIZE*(0.3+dx/1.5), screen_y-self.gridHeight*GHOST_SIZE*(0.3-dy/1.5)), eye_radius)
        moveCircle(eyes[2],(screen_x+self.gridWidth*GHOST_SIZE*(-0.3+dx), screen_y-self.gridHeight*GHOST_SIZE*(0.3-dy)), pupil_radius)
        moveCircle(eyes[3],(screen_x+self.gridWidth*GHOST_SIZE*(0.3+dx), screen_y-self.gridHeight*GHOST_SIZE*(0.3-dy)), pupil_radius)

    def moveGhost(self, ghost, ghostIndex, prevGhost, ghostImageParts):
        old_x, old_y = self.to_screen(self.getPosition(prevGhost))
        new_x, new_y = self.to_screen(self.getPosition(ghost))
        delta = new_x - old_x, new_y - old_y

        for ghostImagePart in ghostImageParts:
            move_by(ghostImagePart, delta)
        refresh()

        if ghost.scaredTimer > 0:
            color = SCARED_COLOR
        else:
            color = GHOST_COLORS[ghostIndex]
        edit(ghostImageParts[0], ('fill', color), ('outline', color))
        self.moveEyes(self.getPosition(ghost), self.getDirection(ghost), ghostImageParts[-4:])
        refresh()

    def getPosition(self, agentState):
        if agentState.configuration == None: return (-1000, -1000)
        return agentState.getPosition()

    def getDirection(self, agentState):
        if agentState.configuration == None: return Directions.STOP
        return agentState.configuration.getDirection()

    def finish(self):
        end_graphics()

    def to_screen(self, point):
        ( x, y ) = point
        # 使用 gridWidth 和 gridHeight 分别计算
        x = (x + 1) * self.gridWidth
        y = (self.height - y) * self.gridHeight
        return ( x, y )

    # Fixes some TK issue with off-center circles
    def to_screen2(self, point):
        ( x, y ) = point
        # 使用 gridWidth 和 gridHeight 分别计算
        x = (x + 1) * self.gridWidth
        y = (self.height - y) * self.gridHeight
        return ( x, y )

    def drawWalls(self, wallMatrix):
        wallColor = WALL_COLOR
        # 获取传送门位置列表
        portals = getattr(self.layout, 'portals', [])
        for xNum, x in enumerate(wallMatrix):
            if self.capture and (xNum * 2) < wallMatrix.width: wallColor = TEAM_COLORS[0]
            if self.capture and (xNum * 2) >= wallMatrix.width: wallColor = TEAM_COLORS[1]

            for yNum, cell in enumerate(x):
                if cell: # There's a wall here
                    pos = (xNum, yNum)
                    # 如果是传送门位置，跳过绘制（透明）
                    if pos in portals:
                        continue
                    
                    screen = self.to_screen(pos)
                    # 绘制矩形墙壁，宽度和高度分别使用 gridWidth 和 gridHeight，确保墙壁填满整个网格单元
                    half_width = 0.5 * self.gridWidth
                    half_height = 0.5 * self.gridHeight
                    coords = [
                        (screen[0] - half_width, screen[1] - half_height),
                        (screen[0] + half_width, screen[1] - half_height),
                        (screen[0] + half_width, screen[1] + half_height),
                        (screen[0] - half_width, screen[1] + half_height)
                    ]
                    polygon(coords, wallColor, wallColor, filled=1, smoothed=0)

    def isWall(self, x, y, walls):
        if x < 0 or y < 0:
            return False
        if x >= walls.width or y >= walls.height:
            return False
        return walls[x][y]

    def drawFood(self, foodMatrix ):
        foodImages = []
        color = FOOD_COLOR
        for xNum, x in enumerate(foodMatrix):
            if self.capture and (xNum * 2) <= foodMatrix.width: color = TEAM_COLORS[0]
            if self.capture and (xNum * 2) > foodMatrix.width: color = TEAM_COLORS[1]
            imageRow = []
            foodImages.append(imageRow)
            for yNum, cell in enumerate(x):
                if cell: # There's food here
                    screen = self.to_screen((xNum, yNum ))
                    # 绘制矩形，使用 FOOD_WIDTH_SCALE 和 FOOD_HEIGHT_SCALE 控制大小
                    half_width = FOOD_WIDTH_SCALE * self.gridWidth
                    half_height = FOOD_HEIGHT_SCALE * self.gridHeight
                    coords = [
                        (screen[0] - half_width, screen[1] - half_height),
                        (screen[0] + half_width, screen[1] - half_height),
                        (screen[0] + half_width, screen[1] + half_height),
                        (screen[0] - half_width, screen[1] + half_height)
                    ]
                    bar = polygon(coords, color, color, filled=1, smoothed=0)
                    imageRow.append(bar)
                else:
                    imageRow.append(None)
        return foodImages

    def drawCapsules(self, capsules ):
        capsuleImages = {}
        for capsule in capsules:
            ( screen_x, screen_y ) = self.to_screen(capsule)
            # 绘制矩形，使用 CAPSULE_WIDTH_SCALE 和 CAPSULE_HEIGHT_SCALE 控制大小
            half_width = CAPSULE_WIDTH_SCALE * self.gridWidth
            half_height = CAPSULE_HEIGHT_SCALE * self.gridHeight
            coords = [
                (screen_x - half_width, screen_y - half_height),
                (screen_x + half_width, screen_y - half_height),
                (screen_x + half_width, screen_y + half_height),
                (screen_x - half_width, screen_y + half_height)
            ]
            bar = polygon(coords, CAPSULE_COLOR, CAPSULE_COLOR, filled=1, smoothed=0)
            capsuleImages[capsule] = bar
        return capsuleImages

    def removeFood(self, cell, foodImages ):
        x, y = cell
        remove_from_screen(foodImages[x][y])

    def removeCapsule(self, cell, capsuleImages ):
        x, y = cell
        remove_from_screen(capsuleImages[(x, y)])

    def drawExpandedCells(self, cells):
        """
        Draws an overlay of expanded grid positions for search agents
        """
        n = float(len(cells))
        baseColor = [1.0, 0.0, 0.0]
        self.clearExpandedCells()
        self.expandedCells = []
        for k, cell in enumerate(cells):
            screenPos = self.to_screen( cell)
            cellColor = formatColor(*[(n-k) * c * .5 / n + .25 for c in baseColor])
            block = square(screenPos,
                     0.5 * min(self.gridWidth, self.gridHeight),
                     color = cellColor,
                     filled = 1, behind=2)
            self.expandedCells.append(block)
            if self.frameTime < 0:
                refresh()

    def clearExpandedCells(self):
        if 'expandedCells' in dir(self) and len(self.expandedCells) > 0:
            for cell in self.expandedCells:
                remove_from_screen(cell)


    def updateDistributions(self, distributions):
        "Draws an agent's belief distributions"
        # copy all distributions so we don't change their state
        distributions = map(lambda x: x.copy(), distributions)
        if self.distributionImages == None:
            self.drawDistributions(self.previousState)
        for x in range(len(self.distributionImages)):
            for y in range(len(self.distributionImages[0])):
                image = self.distributionImages[x][y]
                weights = [dist[ (x,y) ] for dist in distributions]

                if sum(weights) != 0:
                    pass
                # Fog of war
                color = [0.0,0.0,0.0]
                colors = GHOST_VEC_COLORS[1:] # With Pacman
                if self.capture: colors = GHOST_VEC_COLORS
                for weight, gcolor in zip(weights, colors):
                    color = [min(1.0, c + 0.95 * g * weight ** .3) for c,g in zip(color, gcolor)]
                changeColor(image, formatColor(*color))
        refresh()

class FirstPersonPacmanGraphics(PacmanGraphics):
    def __init__(self, zoom = 1.0, showGhosts = True, capture = False, frameTime=0):
        PacmanGraphics.__init__(self, zoom, frameTime=frameTime)
        self.showGhosts = showGhosts
        self.capture = capture

    def initialize(self, state, isBlue = False):

        self.isBlue = isBlue
        PacmanGraphics.startGraphics(self, state)
        # Initialize distribution images
        walls = state.layout.walls
        dist = []
        self.layout = state.layout

        # Draw the rest
        self.distributionImages = None  # initialize lazily
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)

        # Information
        self.previousState = state

    def lookAhead(self, config, state):
        if config.getDirection() == 'Stop':
            return
        else:
            pass
            # Draw relevant ghosts
            allGhosts = state.getGhostStates()
            visibleGhosts = state.getVisibleGhosts()
            for i, ghost in enumerate(allGhosts):
                if ghost in visibleGhosts:
                    self.drawGhost(ghost, i)
                else:
                    self.currentGhostImages[i] = None

    def getGhostColor(self, ghost, ghostIndex):
        return GHOST_COLORS[ghostIndex]

    def getPosition(self, ghostState):
        if not self.showGhosts and not ghostState.isPacman and ghostState.getPosition()[1] > 1:
            return (-1000, -1000)
        else:
            return PacmanGraphics.getPosition(self, ghostState)

def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


# Saving graphical output
# -----------------------
# Note: to make an animated gif from this postscript output, try the command:
# convert -delay 7 -loop 1 -compress lzw -layers optimize frame* out.gif
# convert is part of imagemagick (freeware)

SAVE_POSTSCRIPT = False
POSTSCRIPT_OUTPUT_DIR = 'frames'
FRAME_NUMBER = 0
import os

def saveFrame():
    "Saves the current graphical output as a postscript file"
    global SAVE_POSTSCRIPT, FRAME_NUMBER, POSTSCRIPT_OUTPUT_DIR
    if not SAVE_POSTSCRIPT: return
    if not os.path.exists(POSTSCRIPT_OUTPUT_DIR): os.mkdir(POSTSCRIPT_OUTPUT_DIR)
    name = os.path.join(POSTSCRIPT_OUTPUT_DIR, 'frame_%08d.ps' % FRAME_NUMBER)
    FRAME_NUMBER += 1
    writePostscript(name) # writes the current canvas
