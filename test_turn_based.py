#!/usr/bin/env python
"""
测试回合制游戏逻辑（带截图和状态导出）
"""
from pacman import *
from game import *
from keyboardAgents import KeyboardAgent
from ghostAgents import DirectionalGhost
import layout
import graphicsDisplay
from turnBasedInterface import TurnBasedInterface

def test_turn_based():
    """测试回合制：鬼先动，Pac-Man后动，并导出截图和状态"""
    print("=" * 60)
    print("回合制游戏测试（带导出功能）")
    print("=" * 60)
    
    # 加载地图
    layout_obj = layout.getLayout('merged_mask_frame_0_small')
    if layout_obj == None:
        print("无法加载地图")
        return
    
    print(f"地图尺寸: {layout_obj.width} x {layout_obj.height}")
    print(f"Ghost数量: {layout_obj.getNumGhosts()}")
    
    # 创建回合制接口（导出截图和状态）
    export_interface = TurnBasedInterface(output_dir="turn_based_output")
    print(f"输出目录: {export_interface.output_dir}")
    print(f"截图目录: {export_interface.screenshot_dir}")
    print(f"状态目录: {export_interface.state_dir}\n")
    
    # 创建agents
    pacman = KeyboardAgent()
    ghosts = [DirectionalGhost(i+1) for i in range(layout_obj.getNumGhosts())]
    
    # 创建游戏（传入exportInterface）
    rules = ClassicGameRules()
    # 缩小窗口：使用较小的zoom值（0.5 = 一半大小，0.3 = 更小）
    display = graphicsDisplay.PacmanGraphics(zoom=0.5)
    game = rules.newGame(layout_obj, pacman, ghosts, display, quiet=False, catchExceptions=True)
    
    # 设置导出接口
    game.exportInterface = export_interface
    
    print("游戏开始！")
    print("回合制规则：每个Ghost走一步后，等待Pac-Man走一步")
    print("控制：WASD 或方向键移动，空格键不走，Q停止")
    print("每回合会自动导出截图和状态到输出目录\n")
    
    # 运行游戏（会在run()中实现回合制并自动导出）
    game.run()
    
    print(f"\n游戏结束！共 {game.numMoves} 回合")
    print(f"截图保存在: {export_interface.screenshot_dir}")
    print(f"状态保存在: {export_interface.state_dir}")

if __name__ == '__main__':
    test_turn_based()

