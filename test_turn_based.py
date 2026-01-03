#!/usr/bin/env python
"""
测试回合制游戏逻辑（带截图和状态导出）
支持命令行参数配置
"""
from pacman import *
from game import *
from keyboardAgents import KeyboardAgent
from ghostAgents import DirectionalGhost
import layout
import graphicsDisplay
from turnBasedInterface import TurnBasedInterface
import argparse
import sys

def load_pacman_agent(agent_name):
    """加载Pac-Man agent"""
    if agent_name.lower() == 'keyboard' or agent_name.lower() == 'manual':
        return KeyboardAgent()
    elif agent_name.lower() == 'random':
        from simpleAgents import RandomAgent
        return RandomAgent()
    elif agent_name.lower() == 'greedy':
        from simpleAgents import GreedyAgent
        return GreedyAgent()
    else:
        # 尝试从其他模块加载
        try:
            # 尝试从pacmanAgents加载（如果存在）
            import pacmanAgents
            if hasattr(pacmanAgents, agent_name):
                agent_class = getattr(pacmanAgents, agent_name)
                return agent_class()
        except ImportError:
            pass
        
        # 如果找不到，使用默认的KeyboardAgent
        print(f"警告: 未找到agent '{agent_name}'，使用默认的KeyboardAgent")
        return KeyboardAgent()

def test_turn_based(layout_name='merged_mask_frame_0_small', 
                    num_ghosts=4, 
                    pacman_agent='keyboard',
                    mode='turn-based',
                    zoom=0.5,
                    output_dir='turn_based_output'):
    """
    测试回合制游戏逻辑（带截图和状态导出）
    
    Args:
        layout_name: 地图名称（不包含.lay扩展名）
        num_ghosts: Ghost数量
        pacman_agent: Pac-Man agent类型 ('keyboard', 'random', 'greedy', 或其他agent类名)
        mode: 游戏模式 ('turn-based' 或 'realtime')，目前只支持turn-based
        zoom: 窗口缩放比例
        output_dir: 输出目录
    """
    print("=" * 60)
    if mode == 'turn-based':
        print("回合制游戏测试（带导出功能）")
    else:
        print("实时游戏测试（带导出功能）")
    print("=" * 60)
    
    # 加载地图
    layout_obj = layout.getLayout(layout_name)
    if layout_obj == None:
        print(f"错误: 无法加载地图 '{layout_name}'")
        print("提示: 确保地图文件存在于 layouts/ 目录下")
        return
    
    print(f"地图: {layout_name}")
    print(f"地图尺寸: {layout_obj.width} x {layout_obj.height}")
    print(f"地图中Ghost数量: {layout_obj.getNumGhosts()}")
    
    # 设置鬼的数量
    print(f"实际使用Ghost数量: {num_ghosts}")
    
    # 创建回合制接口（导出截图和状态）
    export_interface = TurnBasedInterface(output_dir=output_dir)
    print(f"输出目录: {export_interface.output_dir}")
    print(f"截图目录: {export_interface.screenshot_dir}")
    print(f"状态目录: {export_interface.state_dir}")
    
    # 创建agents
    pacman = load_pacman_agent(pacman_agent)
    print(f"Pac-Man Agent: {pacman_agent}")
    
    ghosts = [DirectionalGhost(i+1) for i in range(num_ghosts)]
    
    # 创建游戏（传入exportInterface）
    rules = ClassicGameRules()
    display = graphicsDisplay.PacmanGraphics(zoom=zoom)
    game = rules.newGame(layout_obj, pacman, ghosts, display, quiet=False, catchExceptions=True)
    
    # 设置导出接口
    game.exportInterface = export_interface
    
    print("\n游戏开始！")
    if mode == 'turn-based':
        print("回合制规则：Pac-Man先移动，然后所有Ghost依次移动")
    else:
        print("实时模式：所有agent同时移动（基于时间）")
    
    if pacman_agent.lower() == 'keyboard' or pacman_agent.lower() == 'manual':
        print("控制：WASD 或方向键移动，空格键不走，Q停止")
    print("每回合会自动导出截图和状态到输出目录\n")
    
    # 运行游戏
    game.run()
    
    print(f"\n游戏结束！共 {game.numMoves} 回合")
    print(f"截图保存在: {export_interface.screenshot_dir}")
    print(f"状态保存在: {export_interface.state_dir}")

def main():
    """主函数：解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Pac-Man 回合制游戏（带截图和状态导出）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用默认设置
  python test_turn_based.py
  
  # 指定地图和Ghost数量
  python test_turn_based.py --layout auto_generated --ghosts 4
  
  # 使用随机agent（自动游戏）
  python test_turn_based.py --layout auto_generated --agent random
  
  # 使用贪心agent
  python test_turn_based.py --layout auto_generated --agent greedy
  
  # 手动控制（默认）
  python test_turn_based.py --layout auto_generated --agent keyboard
  
  # 完整参数示例
  python test_turn_based.py -l test_map -g 6 -a keyboard -m turn-based -z 0.5
        """
    )
    
    parser.add_argument(
        '-l', '--layout',
        type=str,
        default='merged_mask_frame_0_small',
        help='地图名称（不包含.lay扩展名，默认: merged_mask_frame_0_small）'
    )
    
    parser.add_argument(
        '-g', '--ghosts',
        type=int,
        default=4,
        help='Ghost数量（默认: 4）'
    )
    
    parser.add_argument(
        '-a', '--agent',
        type=str,
        default='keyboard',
        choices=['keyboard', 'manual', 'random', 'greedy'],
        help='Pac-Man agent类型: keyboard/manual(手动控制), random(随机), greedy(贪心) (默认: keyboard)'
    )
    
    parser.add_argument(
        '-m', '--mode',
        type=str,
        default='turn-based',
        choices=['turn-based', 'realtime'],
        help='游戏模式: turn-based(回合制), realtime(实时) (默认: turn-based，注意：realtime模式尚未实现)'
    )
    
    parser.add_argument(
        '-z', '--zoom',
        type=float,
        default=0.5,
        help='窗口缩放比例（默认: 0.5）'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='turn_based_output',
        help='输出目录（默认: turn_based_output）'
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if args.ghosts < 1:
        print("错误: Ghost数量必须大于0")
        sys.exit(1)
    
    if args.zoom <= 0:
        print("错误: 缩放比例必须大于0")
        sys.exit(1)
    
    if args.mode == 'realtime':
        print("警告: 实时模式尚未实现，将使用回合制模式")
        args.mode = 'turn-based'
    
    # 运行游戏
    test_turn_based(
        layout_name=args.layout,
        num_ghosts=args.ghosts,
        pacman_agent=args.agent,
        mode=args.mode,
        zoom=args.zoom,
        output_dir=args.output
    )

if __name__ == '__main__':
    main()

