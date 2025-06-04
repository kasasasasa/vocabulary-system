import os
import json
import random
from datetime import datetime, timedelta

# 常量定义
WORD_BANK_FILE = "word_bank.txt"  # 单词库文件
PROGRESS_FILE = "learning_progress.json"  # 学习进度文件
DAILY_WORDS = 20  # 每日学习单词数量


def load_word_bank():
    """从文件加载单词库"""

    words = []
    with open(WORD_BANK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "," in line:
                word, meaning = line.strip().split(",", 1)
                words.append({"word": word, "meaning": meaning})
    return words


def load_learning_progress():
    """加载学习进度"""
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                progress = json.load(f)
        except:
            print("进度文件损坏，已创建新的进度文件")
    return progress


def save_learning_progress(progress):
    """保存学习进度"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def get_today_words(all_words, progress):
    """获取今天要学习的单词"""
    today = datetime.now().strftime("%Y-%m-%d")

    # 检查今天是否已经学习过
    if today in progress:
        print("今天已经学习过了！")
        return []

    # 找出未学习过的单词
    new_words = [word for word in all_words if word["word"] not in progress]

    # 如果新单词不足，从已学单词中随机补充
    if len(new_words) < DAILY_WORDS:
        learned_words = [word for word in all_words if word["word"] in progress]
        new_words.extend(random.sample(learned_words, min(DAILY_WORDS - len(new_words), len(learned_words))))

    # 随机选择DAILY_WORDS个单词
    selected = random.sample(new_words, min(DAILY_WORDS, len(new_words)))
    progress[today] = [word["word"] for word in selected]
    return selected


def review_words(words):
    """单词学习流程"""
    print(f"\n今日学习任务 ({len(words)}个单词):")
    print("=" * 40)

    for i, word in enumerate(words, 1):
        input(f"\n单词 {i}/{len(words)}: {word['word']}\n按回车查看释义...")
        print(f"释义: {word['meaning']}")

        # 用户自我评估
        while True:
            known = input("是否记住? (y/n): ").lower()
            if known in ["y", "n"]:
                word["known"] = (known == "y")
                break
            print("请输入 y 或 n")

    # 显示学习结果
    known_count = sum(1 for word in words if word.get("known"))
    print(f"\n今日学习完成! 掌握了 {known_count}/{len(words)} 个单词")

    # 显示未掌握的单词
    unknown_words = [word["word"] for word in words if not word.get("known")]
    if unknown_words:
        print("需要复习的单词:", ", ".join(unknown_words))


def main():
    """主程序"""
    print("=" * 40)
    print("每日背单词系统")
    print("=" * 40)

    # 加载数据
    all_words = load_word_bank()
    progress = load_learning_progress()

    # 获取今日单词
    today_words = get_today_words(all_words, progress)

    if not today_words:
        print("没有需要学习的新单词，或者今天已经学习过了")
        return

    # 学习过程
    review_words(today_words)

    # 保存进度
    save_learning_progress(progress)
    print("\n学习进度已保存!")


if __name__ == "__main__":
    main()
