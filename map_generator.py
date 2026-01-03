# map_generator.py
# 自动生成Pac-Man地图
# 使用递归回溯算法生成连通迷宫

import random
from typing import List, Tuple, Set

class MapGenerator:
    """自动生成Pac-Man地图的类"""
    
    def __init__(self, width: int = 21, height: int = 21, 
                 food_density: float = 0.7, capsule_count: int = 4):
        """
        初始化地图生成器
        
        Args:
            width: 地图宽度（必须是奇数，如果是偶数会自动+1）
            height: 地图高度（必须是奇数，如果是偶数会自动+1）
            food_density: 食物密度（0-1之间）
            capsule_count: 能量豆数量
        """
        # 确保宽度和高度是奇数（迷宫生成算法要求）
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.food_density = food_density
        self.capsule_count = capsule_count
        
        # 迷宫网格（True表示墙，False表示通道）
        self.maze = [[True for _ in range(self.width)] for _ in range(self.height)]
        
    def generate(self) -> List[str]:
        """
        生成地图并返回字符串列表
        
        Returns:
            地图字符串列表，每行一个字符串
        """
        # 1. 初始化：所有位置都是墙
        self.maze = [[True for _ in range(self.width)] for _ in range(self.height)]
        
        # 2. 生成连通迷宫（使用递归回溯算法）
        self._generate_maze()
        
        # 3. 增加连通性：添加额外路径
        self._add_extra_paths()
        
        # 4. 随机移除一些内部墙以增加连通性
        self._remove_random_walls()
        
        # 5. 确保最外圈是墙壁
        self._add_outer_walls()
        
        # 6. 放置传送门（Q）- 必须在最外层墙上
        portal_positions = self._place_portals()
        
        # 5. 放置Pac-Man起始位置（P）
        pacman_pos = self._place_pacman()
        
        # 6. 放置Ghost起始位置（G）
        ghost_pos = self._place_ghost(pacman_pos)
        
        # 7. 在可通行区域放置食物和能量豆
        self._place_food_and_capsules(pacman_pos, ghost_pos, portal_positions)
        
        # 8. 转换为字符串格式
        return self._to_string()
    
    def _generate_maze(self):
        """使用递归回溯算法生成迷宫"""
        # 从(1,1)开始（确保是奇数坐标）
        start_x, start_y = 1, 1
        stack = [(start_x, start_y)]
        visited = {(start_x, start_y)}
        
        # 方向：上、下、左、右
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        
        while stack:
            current_x, current_y = stack[-1]
            
            # 获取未访问的邻居
            neighbors = []
            for dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                if (1 <= nx < self.width - 1 and 
                    1 <= ny < self.height - 1 and 
                    (nx, ny) not in visited):
                    neighbors.append((nx, ny, current_x + dx // 2, current_y + dy // 2))
            
            if neighbors:
                # 随机选择一个邻居
                next_x, next_y, wall_x, wall_y = random.choice(neighbors)
                
                # 打通墙壁
                self.maze[next_y][next_x] = False
                self.maze[wall_y][wall_x] = False
                self.maze[current_y][current_x] = False
                
                # 标记为已访问
                visited.add((next_x, next_y))
                stack.append((next_x, next_y))
            else:
                # 回溯
                stack.pop()
        
        # 确保起始位置是通道
        self.maze[1][1] = False
    
    def _add_extra_paths(self):
        """增加额外路径以提高连通性"""
        # 在迷宫生成后，添加一些额外的连接路径
        # 随机选择一些墙位置，如果它们连接两个不同的区域，就打通它们
        
        # 尝试多次添加路径
        num_extra_paths = (self.width * self.height) // 50  # 根据地图大小决定路径数量
        
        for _ in range(num_extra_paths):
            # 随机选择一个内部墙位置（奇数坐标）
            x = random.randrange(1, self.width - 1, 2)
            y = random.randrange(1, self.height - 1, 2)
            
            # 检查这个位置是否是墙
            if self.maze[y][x]:
                # 检查相邻位置是否有通道
                neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                channel_count = sum(1 for nx, ny in neighbors 
                                  if 0 <= nx < self.width and 0 <= ny < self.height 
                                  and not self.maze[ny][nx])
                
                # 如果相邻有通道，有30%概率打通这面墙
                if channel_count > 0 and random.random() < 0.3:
                    self.maze[y][x] = False
    
    def _remove_random_walls(self):
        """随机移除一些内部墙以增加连通性"""
        # 计算内部墙的数量
        internal_walls = []
        for y in range(2, self.height - 2):
            for x in range(2, self.width - 2):
                if self.maze[y][x]:  # 是墙
                    # 检查是否被通道包围（至少两个方向有通道）
                    neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                    channel_count = sum(1 for nx, ny in neighbors 
                                      if 0 <= nx < self.width and 0 <= ny < self.height 
                                      and not self.maze[ny][nx])
                    if channel_count >= 2:  # 至少两个方向有通道
                        internal_walls.append((x, y))
        
        # 随机移除20-30%的内部墙
        if internal_walls:
            num_to_remove = int(len(internal_walls) * random.uniform(0.2, 0.3))
            walls_to_remove = random.sample(internal_walls, min(num_to_remove, len(internal_walls)))
            for x, y in walls_to_remove:
                self.maze[y][x] = False
    
    def _add_outer_walls(self):
        """确保最外圈是墙壁"""
        for y in range(self.height):
            self.maze[y][0] = True
            self.maze[y][self.width - 1] = True
        for x in range(self.width):
            self.maze[0][x] = True
            self.maze[self.height - 1][x] = True
    
    def _place_portals(self) -> List[Tuple[int, int]]:
        """
        放置两个传送门（Q），必须镶嵌在最外层的墙上
        传送门应该放在边界墙上（x=0, x=width-1, y=0, y=height-1），并且相邻位置应该是通道
        """
        portals = []
        
        # 收集所有边界墙位置，这些位置必须：
        # 1. 在最外层（x=0, x=width-1, y=0, y=height-1）
        # 2. 相邻位置至少有一个是通道（这样Pac-Man才能到达）
        boundary_walls = []
        
        # 顶部边界（y=0）
        for x in range(1, self.width - 1):
            if self.maze[0][x]:  # 是墙
                # 检查下方是否有通道
                if not self.maze[1][x]:
                    boundary_walls.append((x, 0))
        
        # 底部边界（y=height-1）
        for x in range(1, self.width - 1):
            if self.maze[self.height - 1][x]:  # 是墙
                # 检查上方是否有通道
                if not self.maze[self.height - 2][x]:
                    boundary_walls.append((x, self.height - 1))
        
        # 左侧边界（x=0）
        for y in range(1, self.height - 1):
            if self.maze[y][0]:  # 是墙
                # 检查右侧是否有通道
                if not self.maze[y][1]:
                    boundary_walls.append((0, y))
        
        # 右侧边界（x=width-1）
        for y in range(1, self.height - 1):
            if self.maze[y][self.width - 1]:  # 是墙
                # 检查左侧是否有通道
                if not self.maze[y][self.width - 2]:
                    boundary_walls.append((self.width - 1, y))
        
        # 如果边界墙位置不够，尝试在角落位置
        if len(boundary_walls) < 2:
            corners = [(1, 0), (self.width - 2, 0), (1, self.height - 1), (self.width - 2, self.height - 1)]
            for x, y in corners:
                if (x, y) not in boundary_walls:
                    boundary_walls.append((x, y))
        
        # 选择两个位置，尽量选择相对的位置（如顶部和底部，或左侧和右侧）
        if len(boundary_walls) >= 2:
            # 尝试选择一个在顶部/左侧，一个在底部/右侧
            top_left = [pos for pos in boundary_walls if pos[1] == 0 or pos[0] == 0]
            bottom_right = [pos for pos in boundary_walls if pos[1] == self.height - 1 or pos[0] == self.width - 1]
            
            if top_left and bottom_right:
                portals = [random.choice(top_left), random.choice(bottom_right)]
            else:
                # 如果无法分别选择，随机选择两个距离较远的位置
                if len(boundary_walls) >= 2:
                    # 选择距离最远的两个位置
                    max_dist = 0
                    best_pair = None
                    for i, pos1 in enumerate(boundary_walls):
                        for j, pos2 in enumerate(boundary_walls[i+1:], i+1):
                            dist = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
                            if dist > max_dist:
                                max_dist = dist
                                best_pair = (pos1, pos2)
                    if best_pair:
                        portals = list(best_pair)
                    else:
                        portals = random.sample(boundary_walls, 2)
                else:
                    portals = boundary_walls[:2]
        else:
            # 如果位置不够，使用默认位置（确保在最外层）
            portals = [(1, 0), (self.width - 2, self.height - 1)]
        
        return portals
    
    def _place_pacman(self) -> Tuple[int, int]:
        """放置Pac-Man起始位置（P）"""
        # 找到所有通道位置
        open_positions = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if not self.maze[y][x]:
                    open_positions.append((x, y))
        
        if open_positions:
            # 选择靠近中心的位置
            center_x, center_y = self.width // 2, self.height // 2
            open_positions.sort(key=lambda pos: 
                               abs(pos[0] - center_x) + abs(pos[1] - center_y))
            return open_positions[0]
        else:
            return (1, 1)
    
    def _place_ghost(self, pacman_pos: Tuple[int, int]) -> Tuple[int, int]:
        """放置Ghost起始位置（G），确保与Pac-Man有一定距离"""
        # 找到所有通道位置
        open_positions = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if not self.maze[y][x]:
                    # 确保与Pac-Man有一定距离（至少5格）
                    dist = abs(x - pacman_pos[0]) + abs(y - pacman_pos[1])
                    if dist >= 5:
                        open_positions.append((x, y))
        
        if open_positions:
            return random.choice(open_positions)
        else:
            # 如果找不到合适位置，使用默认位置
            return (self.width - 2, self.height - 2)
    
    def _place_food_and_capsules(self, pacman_pos: Tuple[int, int], 
                                 ghost_pos: Tuple[int, int],
                                 portal_positions: List[Tuple[int, int]]):
        """在可通行区域放置食物和能量豆"""
        # 找到所有可放置食物的位置（排除特殊位置）
        special_positions = {pacman_pos, ghost_pos}
        special_positions.update(portal_positions)
        
        available_positions = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if not self.maze[y][x] and (x, y) not in special_positions:
                    available_positions.append((x, y))
        
        # 先放置能量豆（需要分散放置）
        capsule_positions = self._place_capsules_dispersed(
            available_positions, special_positions)
        
        # 从可用位置中移除能量豆位置
        available_positions = [pos for pos in available_positions 
                              if pos not in capsule_positions]
        
        # 放置食物（必须空一格，不能连着）
        food_positions = self._place_food_spaced(
            available_positions, special_positions, capsule_positions)
        
        # 存储食物和能量豆位置
        self.food_positions = set(food_positions)
        self.capsule_positions = set(capsule_positions)
        self.pacman_pos = pacman_pos
        self.ghost_pos = ghost_pos
        self.portal_positions = portal_positions
    
    def _place_capsules_dispersed(self, available_positions: List[Tuple[int, int]],
                                   special_positions: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        分散放置能量豆，使它们彼此之间距离尽可能远
        使用贪心算法：每次选择与已选位置距离最远的位置
        """
        if len(available_positions) < self.capsule_count:
            # 如果位置不够，随机选择
            return random.sample(available_positions, min(self.capsule_count, len(available_positions)))
        
        capsule_positions = []
        remaining_positions = available_positions.copy()
        
        # 第一步：选择距离地图中心最远的位置（或随机选择第一个）
        if remaining_positions:
            # 计算地图中心
            center_x, center_y = self.width // 2, self.height // 2
            # 选择距离中心最远的位置作为第一个能量豆
            first_capsule = max(remaining_positions,
                              key=lambda pos: abs(pos[0] - center_x) + abs(pos[1] - center_y))
            capsule_positions.append(first_capsule)
            remaining_positions.remove(first_capsule)
        
        # 后续步骤：每次选择与已选位置距离最远的位置
        for _ in range(self.capsule_count - 1):
            if not remaining_positions:
                break
            
            # 对于每个剩余位置，计算它到所有已选位置的最小距离
            best_pos = None
            max_min_dist = -1
            
            for pos in remaining_positions:
                # 计算到所有已选位置的最小距离
                min_dist = min(abs(pos[0] - cp[0]) + abs(pos[1] - cp[1]) 
                             for cp in capsule_positions)
                if min_dist > max_min_dist:
                    max_min_dist = min_dist
                    best_pos = pos
            
            if best_pos:
                capsule_positions.append(best_pos)
                remaining_positions.remove(best_pos)
        
        return capsule_positions
    
    def _place_food_spaced(self, available_positions: List[Tuple[int, int]],
                          special_positions: Set[Tuple[int, int]],
                          capsule_positions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        放置食物，确保食物之间至少空一格（不能连着）
        相邻位置定义为：上下左右四个方向
        """
        # 计算需要放置的食物数量
        num_food = int(len(available_positions) * self.food_density)
        
        # 随机打乱位置列表
        shuffled_positions = available_positions.copy()
        random.shuffle(shuffled_positions)
        
        food_positions = []
        # 已放置的位置集合（包括特殊位置、能量豆和已放置的食物）
        placed_positions = set(special_positions)
        placed_positions.update(capsule_positions)
        
        for pos in shuffled_positions:
            if len(food_positions) >= num_food:
                break
            
            # 检查相邻位置（上下左右）是否已经有食物
            x, y = pos
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            
            # 检查相邻位置是否有已放置的食物（不包括能量豆和特殊位置，因为它们不影响食物间距）
            has_neighbor_food = any(neighbor in food_positions for neighbor in neighbors)
            
            # 如果相邻位置没有食物，则可以放置
            if not has_neighbor_food:
                food_positions.append(pos)
                placed_positions.add(pos)
        
        # 如果因为间距要求导致食物数量不足，尝试在更宽松的条件下继续放置
        # 但优先保持间距要求
        if len(food_positions) < num_food:
            remaining = [pos for pos in shuffled_positions if pos not in placed_positions]
            needed = num_food - len(food_positions)
            
            # 尝试放置剩余的食物，但跳过与已放置食物相邻的位置
            for pos in remaining:
                if len(food_positions) >= num_food:
                    break
                x, y = pos
                neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                has_neighbor_food = any(neighbor in food_positions for neighbor in neighbors)
                if not has_neighbor_food:
                    food_positions.append(pos)
                    placed_positions.add(pos)
        
        return food_positions
    
    def _to_string(self) -> List[str]:
        """将地图转换为字符串格式"""
        lines = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                pos = (x, y)
                
                # 优先检查特殊位置
                if pos in self.portal_positions:
                    line.append('Q')
                elif pos == self.pacman_pos:
                    line.append('P')
                elif pos == self.ghost_pos:
                    line.append('G')
                elif pos in self.capsule_positions:
                    line.append('o')
                elif pos in self.food_positions:
                    line.append('.')
                elif self.maze[y][x]:
                    line.append('%')
                else:
                    line.append(' ')
            
            lines.append(''.join(line))
        
        return lines


def generate_map(width: int = 21, height: int = 21, 
                 food_density: float = 0.7, capsule_count: int = 4,
                 output_file: str = None) -> List[str]:
    """
    生成地图的便捷函数
    
    Args:
        width: 地图宽度
        height: 地图高度
        food_density: 食物密度（0-1）
        capsule_count: 能量豆数量
        output_file: 输出文件路径（可选）
    
    Returns:
        地图字符串列表
    """
    generator = MapGenerator(width, height, food_density, capsule_count)
    map_lines = generator.generate()
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(map_lines))
        print(f"地图已保存到: {output_file}")
    
    return map_lines


if __name__ == "__main__":
    # 示例：生成一个地图
    import sys
    
    # 默认参数
    width = 21
    height = 21
    food_density = 0.7
    capsule_count = 4
    output_file = "layouts/auto_generated.lay"
    
    # 从命令行参数读取（如果提供）
    if len(sys.argv) > 1:
        width = int(sys.argv[1])
    if len(sys.argv) > 2:
        height = int(sys.argv[2])
    if len(sys.argv) > 3:
        food_density = float(sys.argv[3])
    if len(sys.argv) > 4:
        capsule_count = int(sys.argv[4])
    if len(sys.argv) > 5:
        output_file = sys.argv[5]
    
    print(f"生成地图: {width}x{height}, 食物密度: {food_density}, 能量豆: {capsule_count}")
    map_lines = generate_map(width, height, food_density, capsule_count, output_file)
    
    # 打印地图预览
    print("\n地图预览:")
    print('\n'.join(map_lines[:min(10, len(map_lines))]))
    if len(map_lines) > 10:
        print("...")

