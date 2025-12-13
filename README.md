# Pac-Man 游戏项目

一个用于训练视觉模型的 Pac-Man 游戏实现，支持回合制和实时两种模式，并提供完整的截图和游戏状态导出功能。

## 📁 项目结构

### 核心代码文件

#### 1. **test_turn_based.py** - 主入口文件
- **功能**: 回合制游戏的主程序入口
- **作用**: 
  - 加载地图和配置游戏参数
  - 创建 Pac-Man 和 Ghost 智能体
  - 初始化回合制接口（导出截图和状态）
  - 启动游戏循环
- **运行方式**: `python test_turn_based.py`
- **特点**: 
  - 回合制规则：Ghost 先移动，Pac-Man 后移动
  - 每回合自动导出截图（PNG）和游戏状态（PKL/JSON）
  - 支持键盘控制（WASD 或方向键）

#### 2. **game.py** - 游戏核心逻辑
- **功能**: 定义游戏的基础框架和运行机制
- **主要内容**:
  - `Agent` 基类：所有智能体的基类
  - `Game` 类：游戏主循环，管理回合、状态更新、胜负判定
  - `Directions` 和 `Actions`：方向定义和动作处理
  - `GameStateData`：游戏状态数据容器
- **关键方法**:
  - `Game.run()`: 执行游戏主循环
  - `Game.generateSuccessor()`: 生成下一状态
- **修改点**: 
  - 移除了 Agent 超时机制
  - 集成了 `TurnBasedInterface` 用于数据导出

#### 3. **pacman.py** - Pac-Man 游戏规则
- **功能**: 实现 Pac-Man 的具体游戏规则和状态管理
- **主要内容**:
  - `GameState`: 游戏状态类，包含所有游戏信息
  - `ClassicGameRules`: 经典游戏规则
  - `PacmanRules`: Pac-Man 移动和吃豆规则
  - `GhostRules`: Ghost 移动和碰撞规则
- **游戏规则实现**:
  - **生命系统**: 初始 4 条生命，失去生命后继续游戏，只有生命 ≤ 0 时游戏结束
  - **分数系统**:
    - 糖豆（food pellet）: 1 分
    - 能量丸（power pellet）: 5 分
    - 吃鬼分数递增: 10 × 2^n（n 为连续吃鬼次数）
    - 走路不扣分（已移除时间惩罚）
  - **状态管理**: 跟踪生命数、连续吃鬼次数、得分等

#### 4. **layout.py** - 地图加载
- **功能**: 从 `.lay` 文件加载游戏地图
- **地图格式**:
  - `%`: 墙壁
  - `.`: 糖豆
  - `o`: 能量丸（Power Pellet）
  - `P`: Pac-Man 起始位置
  - `G`: Ghost 起始位置
- **方法**:
  - `getLayout(name)`: 加载指定名称的地图文件
  - 自动从 `layouts/` 目录查找地图文件

#### 5. **graphicsDisplay.py** - 图形显示
- **功能**: 使用 Tkinter 渲染游戏画面
- **主要内容**:
  - `PacmanGraphics`: 主图形显示类
  - `InfoPane`: 信息面板（显示分数、生命数）
  - 实时更新游戏画面
- **特点**: 
  - 支持自定义缩放（zoom 参数）
  - 显示分数和生命数
  - 使用 Canvas 进行图形渲染

#### 6. **graphicsUtils.py** - 图形工具
- **功能**: 提供底层图形绘制函数
- **作用**: 
  - 封装 Tkinter Canvas 操作
  - 提供绘制圆形、矩形、文本等基础图形函数
  - 管理全局 Canvas 和窗口对象

#### 7. **keyboardAgents.py** - 键盘控制
- **功能**: 实现键盘控制的 Pac-Man Agent
- **控制方式**:
  - `W` / `↑`: 向上移动
  - `S` / `↓`: 向下移动
  - `A` / `←`: 向左移动
  - `D` / `→`: 向右移动
  - `空格`: 停止不动
  - `Q`: 退出游戏
- **类**: `KeyboardAgent` - 继承自 `Agent` 基类

#### 8. **ghostAgents.py** - Ghost AI
- **功能**: 实现 Ghost 的智能体行为
- **Ghost 类型**:
  - `RandomGhost`: 随机移动的 Ghost（已弃用）
  - `DirectionalGhost`: 智能 Ghost（默认使用）
    - **正常状态**: 使用 A* 算法追踪 Pac-Man
    - **恐惧状态**: 使用距离计算逃离 Pac-Man
    - 使用 `GhostPositionSearchProblem` 定义搜索问题
- **搜索算法**: 
  - 使用 `search.aStarSearch()` 和 `manhattanDistance` 启发式函数
  - 如果 A* 失败，回退到基于距离的简单策略

#### 9. **turnBasedInterface.py** - 回合制接口
- **功能**: 提供截图和游戏状态导出功能
- **主要功能**:
  - `export_screenshot(turn)`: 导出当前回合的截图（PNG 格式）
    - 使用 `mss` 库捕获 Canvas 区域
    - 自动缓存 Canvas 尺寸，确保截图一致性
  - `export_state(game_state, turn, format)`: 导出游戏状态
    - `format='pkl'`: 使用 pickle 保存完整 GameState 对象（默认）
    - `format='json'`: 保存关键信息的 JSON 格式
  - `export_turn(game_state, turn)`: 同时导出截图和状态
  - `finalize_game(final_score)`: 游戏结束时重命名输出目录
- **输出目录结构**:
  ```
  turn_based_output/
    score_{得分}_{随机数}/
      screenshots/
        turn_000001.png
        turn_000002.png
        ...
      states/
        state_000001.pkl
        state_000002.pkl
        ...
  ```
- **特点**:
  - 每局游戏自动创建唯一目录
  - 游戏结束时根据最终得分重命名目录
  - 支持临时目录（游戏进行中）和最终目录（游戏结束后）

#### 10. **util.py** - 工具函数
- **功能**: 提供通用工具函数
- **主要内容**:
  - `manhattanDistance()`: 曼哈顿距离计算
  - `Counter`: 计数器类（用于概率分布）
  - `chooseFromDistribution()`: 根据概率分布选择动作
  - `nearestPoint()`: 找到最近的点
  - 其他辅助函数

#### 11. **search.py** - 搜索算法
- **功能**: 实现通用搜索算法
- **算法**:
  - `aStarSearch()`: A* 搜索算法（用于 Ghost 路径规划）
  - 其他搜索算法（BFS, DFS, UCS 等）
- **用途**: 被 `ghostAgents.py` 中的 `DirectionalGhost` 使用

### 目录结构

#### **layouts/** - 地图文件目录
- 存放 `.lay` 格式的地图文件
- 当前地图: `merged_mask_frame_0_small.lay`
- 地图文件格式说明见下方

#### **turn_based_output/** - 输出目录
- 自动生成的游戏数据输出目录
- 每局游戏创建一个子目录
- 目录命名规则: `score_{最终得分}_{随机数}`

### 配置文件

#### **requirements.txt** - 依赖包
```
numpy>=1.20.0
Pillow>=8.0.0
pygame>=2.0.0
mss>=6.0.0  # 用于截图（需要单独安装）
```

**安装依赖**:
```bash
pip install -r requirements.txt
pip install mss  # 截图功能需要
```

### 文档文件

#### **pacman2600规则.md** - 游戏规则说明
- 详细说明 Atari 2600 版本的 Pac-Man 游戏规则
- 包含生命系统、能量丸、维生素等规则说明
- 分数表参考

## 🎮 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
pip install mss
```

### 2. 运行回合制游戏
```bash
python test_turn_based.py
```

### 3. 游戏控制
- **移动**: WASD 或方向键
- **停止**: 空格键
- **退出**: Q 键

### 4. 查看输出
游戏结束后，在 `turn_based_output/` 目录下会生成以得分命名的文件夹，包含：
- `screenshots/`: 每回合的截图（PNG）
- `states/`: 每回合的游戏状态（PKL 或 JSON）

## 🎯 游戏规则

### 生命系统
- 初始生命数: **4 条**
- 失去生命后: 继续游戏，Pac-Man 和 Ghost 重置到起始位置
- 游戏结束条件: 生命数 ≤ 0

### 分数系统
| 项目 | 分数 |
|------|------|
| 糖豆（Food Pellet） | 1 分 |
| 能量丸（Power Pellet） | 5 分 |
| 连续吃第 n 个鬼 | 10 × 2^n 分 |
| 走路 | 不扣分 |

### Ghost AI
- **默认**: `DirectionalGhost`（智能 Ghost）
- **正常状态**: 使用 A* 算法追踪 Pac-Man
- **恐惧状态**: 逃离 Pac-Man

## 📊 数据导出格式

### 截图格式
- **格式**: PNG
- **命名**: `turn_{回合数:06d}.png`
- **内容**: 完整的游戏画面（Canvas 区域）

### 状态格式

#### PKL 格式（默认）
- **格式**: Python Pickle
- **命名**: `state_{回合数:06d}.pkl`
- **内容**: 完整的 `GameState` 对象
- **用途**: 可以完全恢复游戏状态，用于训练和回放

#### JSON 格式（可选）
- **格式**: JSON
- **命名**: `state_{回合数:06d}.json`
- **内容**: 关键信息（分数、生命、位置、食物数量等）
- **用途**: 人类可读，用于快速分析

## 🔧 自定义配置

### 修改地图
1. 在 `layouts/` 目录下创建或修改 `.lay` 文件
2. 在 `test_turn_based.py` 中修改 `layout.getLayout('地图名称')`

### 修改窗口大小
在 `test_turn_based.py` 中修改:
```python
display = graphicsDisplay.PacmanGraphics(zoom=0.5)  # 0.5 = 一半大小
```

### 修改 Ghost AI
在 `test_turn_based.py` 中修改:
```python
from ghostAgents import RandomGhost, DirectionalGhost
ghosts = [DirectionalGhost(i+1) for i in range(layout_obj.getNumGhosts())]
```

### 修改导出格式
在 `turnBasedInterface.py` 的 `export_state()` 方法中修改 `format` 参数:
```python
export_interface.export_state(game_state, turn, format='json')  # 或 'pkl'
```

## 📝 地图文件格式

`.lay` 文件使用文本格式，字符含义：
- `%`: 墙壁（Wall）
- `.`: 糖豆（Food Pellet）
- `o`: 能量丸（Power Pellet）
- `P`: Pac-Man 起始位置
- `G`: Ghost 起始位置
- `空格`: 可通行区域

示例：
```
%%%%%%%%%%%%%%%%%%%
%......%...%......%
%.%%%.%.%.%.%%%.%.%
%o...%.%.%.%...o%
%.%%%.%.%.%.%%%.%.%
%......%...%......%
%%%%%%%%%%%%%%%%%%%
```

## 🐛 常见问题

### 1. 截图失败
- **问题**: `mss截图失败: 'float' object cannot be interpreted as an integer`
- **解决**: 已修复，确保坐标和尺寸为整数

### 2. 窗口大小变化
- **问题**: 第一回合后窗口自动变小
- **解决**: 已实现 Canvas 尺寸缓存机制

### 3. 文件锁定错误
- **问题**: `WinError 32: 另一个程序正在使用此文件`
- **解决**: 已改用 `mss` 库，避免文件锁定问题

### 4. 导入错误
- **问题**: `ModuleNotFoundError: No module named 'mss'`
- **解决**: 运行 `pip install mss`

## 📚 技术栈

- **Python 3.x**
- **Tkinter**: 图形界面
- **PIL/Pillow**: 图像处理
- **mss**: 屏幕截图
- **pickle**: 状态序列化
- **A* 算法**: Ghost 路径规划

## 🔄 开发历史

- ✅ 实现回合制游戏模式
- ✅ 实现截图和状态导出功能
- ✅ 实现生命系统（4 条生命）
- ✅ 实现分数系统（糖豆 1 分，能量丸 5 分，吃鬼递增）
- ✅ 移除走路扣分机制
- ✅ 移除 Agent 超时机制
- ✅ 实现智能 Ghost（A* 算法）
- ✅ 优化截图机制（使用 mss 库）
- ✅ 实现游戏目录自动命名（基于得分）
- ✅ 项目结构优化（文件整理到根目录）

## 📄 许可证

本项目基于 UC Berkeley 的 Pac-Man AI 项目修改，遵循原项目的许可证要求。

## 👥 贡献

本项目用于训练视觉模型，欢迎提出改进建议。

---

**最后更新**: 2025年12月14日

