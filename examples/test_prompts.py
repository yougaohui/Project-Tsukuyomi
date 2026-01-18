#!/usr/bin/env python3
"""
示例脚本：查看和测试 Prompt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.video_generator.prompt_manager import PromptManager
from src.utils.logger import setup_logger

setup_logger("example_prompts", "INFO")


def main():
    """主函数"""
    print("=" * 50)
    print("火影忍者 Prompt 系统示例")
    print("=" * 50 + "\n")

    prompt_manager = PromptManager()

    while True:
        print("\n请选择操作：")
        print("1. 查看所有分类")
        print("2. 获取随机 Prompt（所有类别）")
        print("3. 获取特定类别的随机 Prompt")
        print("4. 自定义 Prompt")
        print("5. 查看统计信息")
        print("0. 退出")

        choice = input("\n请输入选项：").strip()

        if choice == "0":
            print("\n再见！")
            break

        elif choice == "1":
            categories = prompt_manager.get_all_categories()
            print(f"\n共有 {len(categories)} 个分类：")
            for category in categories:
                count = prompt_manager.get_prompt_count(category)
                print(f"  - {category}: {count} 个 Prompt")

        elif choice == "2":
            prompt = prompt_manager.get_random_prompt()
            print(f"\n随机 Prompt：\n{prompt}\n")

        elif choice == "3":
            categories = prompt_manager.get_all_categories()
            print("\n可用分类：")
            for i, category in enumerate(categories, 1):
                print(f"  {i}. {category}")

            cat_choice = input("\n请选择分类编号：").strip()
            try:
                category_index = int(cat_choice) - 1
                if 0 <= category_index < len(categories):
                    category = categories[category_index]
                    prompt = prompt_manager.get_random_prompt(category)
                    print(f"\n[{category}] Prompt：\n{prompt}\n")
                else:
                    print("\n❌ 无效的选项")
            except ValueError:
                print("\n❌ 请输入数字")

        elif choice == "4":
            print("\n自定义 Prompt 生成器\n")
            character = input("角色名称（可选）：").strip() or None
            action = input("动作描述（可选）：").strip() or None
            style = input("艺术风格（可选）：").strip() or None
            background = input("背景场景（可选）：").strip() or None

            prompt = prompt_manager.get_custom_prompt(
                character=character,
                action=action,
                style=style,
                background=background
            )

            print(f"\n自定义 Prompt：\n{prompt}\n")

        elif choice == "5":
            total = prompt_manager.get_prompt_count()
            print(f"\n统计信息：")
            print(f"  总 Prompt 数量：{total}")

            categories = prompt_manager.get_all_categories()
            print(f"  分类数量：{len(categories)}")
            print("\n各分类详情：")

            for category in categories:
                count = prompt_manager.get_prompt_count(category)
                bar = "█" * (count // 2)
                print(f"  {category:20} {count:3} {bar}")

        else:
            print("\n❌ 无效的选项")


if __name__ == "__main__":
    main()
