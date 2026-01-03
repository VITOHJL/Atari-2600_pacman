# generate_map_example.py
# 地图生成器使用示例

from map_generator import generate_map
import sys

def main():
    """生成地图的示例脚本"""
    
    print("=" * 50)
    print("Pac-Man 地图自动生成器")
    print("=" * 50)
    
    # 默认参数
    width = 21
    height = 21
    food_density = 0.7
    capsule_count = 4
    output_file = "layouts/auto_generated.lay"
    
    # 从命令行参数读取（如果提供）
    if len(sys.argv) > 1:
        try:
            width = int(sys.argv[1])
        except ValueError:
            print(f"警告: 无效的宽度参数 '{sys.argv[1]}', 使用默认值 {width}")
    
    if len(sys.argv) > 2:
        try:
            height = int(sys.argv[2])
        except ValueError:
            print(f"警告: 无效的高度参数 '{sys.argv[2]}', 使用默认值 {height}")
    
    if len(sys.argv) > 3:
        try:
            food_density = float(sys.argv[3])
            if not 0 <= food_density <= 1:
                print(f"警告: 食物密度应在0-1之间, 使用默认值 0.7")
                food_density = 0.7
        except ValueError:
            print(f"警告: 无效的食物密度参数 '{sys.argv[3]}', 使用默认值 0.7")
            food_density = 0.7
    
    if len(sys.argv) > 4:
        try:
            capsule_count = int(sys.argv[4])
            if capsule_count < 0:
                capsule_count = 4
        except ValueError:
            print(f"警告: 无效的能量豆数量参数 '{sys.argv[4]}', 使用默认值 4")
            capsule_count = 4
    
    if len(sys.argv) > 5:
        output_file = sys.argv[5]
    
    print(f"\n生成参数:")
    print(f"  宽度: {width}")
    print(f"  高度: {height}")
    print(f"  食物密度: {food_density}")
    print(f"  能量豆数量: {capsule_count}")
    print(f"  输出文件: {output_file}")
    print()
    
    # 生成地图
    print("正在生成地图...")
    map_lines = generate_map(width, height, food_density, capsule_count, output_file)
    
    # 统计信息
    q_count = sum(line.count('Q') for line in map_lines)
    p_count = sum(line.count('P') for line in map_lines)
    g_count = sum(line.count('G') for line in map_lines)
    o_count = sum(line.count('o') for line in map_lines)
    dot_count = sum(line.count('.') for line in map_lines)
    
    print(f"\n生成完成！")
    print(f"地图统计:")
    print(f"  传送门 (Q): {q_count}")
    print(f"  Pac-Man (P): {p_count}")
    print(f"  Ghost (G): {g_count}")
    print(f"  能量豆 (o): {o_count}")
    print(f"  食物 (.): {dot_count}")
    
    # 显示地图预览
    print(f"\n地图预览 (前15行):")
    print("-" * width)
    for i, line in enumerate(map_lines[:15]):
        print(line)
    if len(map_lines) > 15:
        print("...")
        print(f"(共 {len(map_lines)} 行)")
    print("-" * width)
    
    print(f"\n地图已保存到: {output_file}")
    print("\n使用方法:")
    print(f"  python test_turn_based.py --layout auto_generated")


if __name__ == "__main__":
    main()

