"""
回合制游戏接口
提供导出截图和二进制状态的功能
"""
import pickle
import os
import graphicsUtils
import time
import random
import shutil
from datetime import datetime

class TurnBasedInterface:
    """回合制游戏接口，用于导出截图和状态"""
    
    def __init__(self, output_dir="turn_based_output", game_id=None):
        """
        初始化接口
        Args:
            output_dir: 基础输出目录
            game_id: 游戏ID，如果为None则使用临时ID（游戏结束时根据得分重命名）
        """
        self.base_output_dir = output_dir
        
        # 生成临时游戏ID（如果未提供）
        if game_id is None:
            # 使用时间戳生成临时ID：格式为 temp_YYYYMMDD_HHMMSS
            self.temp_game_id = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.game_id = self.temp_game_id
            self.is_temp = True
        else:
            self.temp_game_id = None
            self.game_id = game_id
            self.is_temp = False
        
        self.output_dir = os.path.join(output_dir, self.game_id)
        self.turn_count = 0
        self.screenshot_dir = os.path.join(self.output_dir, "screenshots")
        self.state_dir = os.path.join(self.output_dir, "states")
        
        # 创建输出目录
        os.makedirs(self.screenshot_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)
        
        # 缓存Canvas尺寸，避免窗口大小变化导致截图尺寸不一致
        self.cached_canvas_width = None
        self.cached_canvas_height = None
        
        print(f"游戏ID: {self.game_id}")
        print(f"输出目录: {self.output_dir}")
    
    def finalize_game(self, score):
        """
        游戏结束时，根据得分重命名目录
        Args:
            score: 游戏结束时的得分
        Returns:
            最终的游戏ID
        """
        if not self.is_temp:
            # 如果已经指定了游戏ID，不重命名
            return self.game_id
        
        # 生成最终的游戏ID：score_随机数
        random_suffix = random.randint(1000, 9999)
        final_game_id = f"score_{score}_{random_suffix}"
        final_output_dir = os.path.join(self.base_output_dir, final_game_id)
        
        # 重命名目录
        try:
            if os.path.exists(self.output_dir):
                if os.path.exists(final_output_dir):
                    # 如果目标目录已存在，添加更多随机数
                    random_suffix = random.randint(10000, 99999)
                    final_game_id = f"score_{score}_{random_suffix}"
                    final_output_dir = os.path.join(self.base_output_dir, final_game_id)
                
                shutil.move(self.output_dir, final_output_dir)
                self.game_id = final_game_id
                self.output_dir = final_output_dir
                self.screenshot_dir = os.path.join(self.output_dir, "screenshots")
                self.state_dir = os.path.join(self.output_dir, "states")
                self.is_temp = False
                print(f"游戏结束！目录已重命名为: {final_game_id} (得分: {score})")
                return final_game_id
            else:
                print(f"警告: 原目录不存在: {self.output_dir}")
                return self.game_id
        except Exception as e:
            print(f"重命名目录失败: {e}")
            return self.game_id
    
    def export_screenshot(self, turn=None):
        """
        导出当前游戏画面的截图
        使用mss库截图，不依赖窗口位置
        Args:
            turn: 回合数，如果为None则使用内部计数器
        Returns:
            截图文件路径
        """
        if turn is None:
            turn = self.turn_count
        
        filename = os.path.join(self.screenshot_dir, f"turn_{turn:06d}.png")
        
        try:
            # 获取canvas和root_window
            _canvas = getattr(graphicsUtils, '_canvas', None)
            _root_window = getattr(graphicsUtils, '_root_window', None)
            
            if _canvas is None or _root_window is None:
                print("警告: Canvas未初始化，无法导出截图")
                return None
            
            # 确保窗口已更新
            _root_window.update()
            _root_window.update_idletasks()
            _canvas.update()
            
            import time
            time.sleep(0.1)
            
            # 使用mss库截图
            import mss
            from PIL import Image
            
            # 获取Canvas的配置尺寸（确保是整数）
            # 优先使用缓存的尺寸，避免窗口大小变化
            if self.cached_canvas_width is not None and self.cached_canvas_height is not None:
                canvas_width = self.cached_canvas_width
                canvas_height = self.cached_canvas_height
            else:
                # 第一次获取并缓存尺寸
                _canvas_xs = getattr(graphicsUtils, '_canvas_xs', None)
                _canvas_ys = getattr(graphicsUtils, '_canvas_ys', None)
                
                if _canvas_xs is not None and _canvas_ys is not None:
                    canvas_width = int(_canvas_xs + 1)
                    canvas_height = int(_canvas_ys + 1)
                else:
                    # 等待窗口完全初始化
                    time.sleep(0.2)
                    canvas_width = int(_canvas.winfo_width())
                    canvas_height = int(_canvas.winfo_height())
                    if canvas_width <= 1 or canvas_height <= 1:
                        canvas_width = int(_canvas.winfo_reqwidth())
                        canvas_height = int(_canvas.winfo_reqheight())
                
                # 缓存尺寸
                self.cached_canvas_width = canvas_width
                self.cached_canvas_height = canvas_height
                print(f"缓存Canvas尺寸: {canvas_width}x{canvas_height}")
            
            # 获取Canvas在屏幕上的位置（确保是整数）
            canvas_x = int(_canvas.winfo_rootx())
            canvas_y = int(_canvas.winfo_rooty())
            
            # 使用mss截取Canvas区域
            with mss.mss() as sct:
                monitor = {
                    "top": canvas_y,
                    "left": canvas_x,
                    "width": canvas_width,
                    "height": canvas_height
                }
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                img.save(filename, 'PNG')
                print(f"截图已保存: {filename} (Canvas位置: {canvas_x},{canvas_y}, 尺寸: {canvas_width}x{canvas_height})")
                return filename
                    
        except ImportError:
            print("错误: mss库未安装，请运行: pip install mss")
            return None
        except Exception as e:
            print(f"截图导出错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def export_state(self, game_state, turn=None, format='pkl'):
        """
        导出游戏状态
        Args:
            game_state: GameState对象
            turn: 回合数，如果为None则使用内部计数器
            format: 导出格式，'pkl'（Python pickle，完整对象）或 'json'（JSON，仅关键信息）
        Returns:
            状态文件路径
        """
        if turn is None:
            turn = self.turn_count
        
        if format == 'pkl':
            # 使用pickle格式：完整保存GameState对象（包括所有嵌套对象）
            # 优点：可以完整恢复对象，支持复杂数据结构
            # 缺点：只能被Python读取，文件较大
            filename = os.path.join(self.state_dir, f"state_{turn:06d}.pkl")
            try:
                with open(filename, 'wb') as f:
                    pickle.dump(game_state, f)
                return filename
            except Exception as e:
                print(f"状态导出错误: {e}")
                return None
        elif format == 'json':
            # 使用JSON格式：只保存关键信息（人类可读）
            # 优点：人类可读，可以被其他语言读取
            # 缺点：不能完整恢复GameState对象，只能保存基本信息
            import json
            filename = os.path.join(self.state_dir, f"state_{turn:06d}.json")
            try:
                state_info = {
                    'turn': turn,
                    'score': game_state.getScore(),
                    'pacman_position': game_state.getPacmanPosition(),
                    'pacman_direction': str(game_state.getPacmanDirection()),
                    'ghost_positions': [game_state.getGhostPosition(i) for i in range(1, game_state.getNumAgents())],
                    'food_count': game_state.getNumFood(),
                    'capsules_count': len(game_state.getCapsules()),
                    'is_win': game_state.isWin(),
                    'is_lose': game_state.isLose()
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(state_info, f, indent=2, ensure_ascii=False)
                return filename
            except Exception as e:
                print(f"JSON状态导出错误: {e}")
                return None
        else:
            print(f"不支持的格式: {format}，使用 'pkl' 或 'json'")
            return None
    
    def export_turn(self, game_state, turn=None):
        """
        导出当前回合的截图和状态
        Args:
            game_state: GameState对象
            turn: 回合数，如果为None则使用内部计数器
        Returns:
            (screenshot_path, state_path) 元组
        """
        if turn is None:
            turn = self.turn_count
            self.turn_count += 1
        
        screenshot_path = self.export_screenshot(turn)
        state_path = self.export_state(game_state, turn)
        
        return (screenshot_path, state_path)
    
    def load_state(self, turn):
        """
        加载指定回合的游戏状态
        Args:
            turn: 回合数
        Returns:
            GameState对象
        """
        filename = os.path.join(self.state_dir, f"state_{turn:06d}.pkl")
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"状态加载错误: {e}")
            return None

