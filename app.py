import os
import json
import random
from datetime import datetime
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# 常量定义
WORD_BANK_FILE = "word_bank.txt"  # 单词库文件
PROGRESS_FILE = "learning_progress.json"  # 学习进度文件
DAILY_WORDS = 20  # 每日学习单词数量


# 加载单词库
def load_word_bank():
    """从文件加载单词库"""
    try:
        with open(WORD_BANK_FILE, "r", encoding="utf-8") as file:
            words = []
            for line in file:
                if "," in line:
                    word, meaning = line.strip().split(",", 1)
                    words.append({"word": word.strip(), "meaning": meaning.strip()})
            return words
    except FileNotFoundError:
        print("未找到单词库文件")
        return []


# 加载学习进度
def load_learning_progress():
    """加载学习进度"""
    progress = {}
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
                progress = json.load(file)
        except json.JSONDecodeError:
            print("学习进度文件损坏，已创建新的进度文件")
    return progress


# 保存学习进度
def save_learning_progress(progress):
    """保存学习进度"""
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as file:
            json.dump(progress, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存学习进度时出错: {str(e)}")


# 获取今日单词
def get_today_words(all_words, progress):
    """获取今天要学习的单词"""
    today = datetime.now().strftime("%Y-%m-%d")

    # 检查今天是否已经学习过
    if today in progress.get("learned_words", {}):
        return []

    unlearned_words = [word for word in all_words
                       if word["word"] not in progress.get("learned_words", {})]

    # 如果新单词不足，从已学单词中随机补充
    if len(unlearned_words) < DAILY_WORDS:
        learned_words = [word for word in all_words
                         if word["word"] in progress.get("learned_words", {})]
        selected_words = unlearned_words.copy()
        random.shuffle(learned_words)
        selected_words.extend(learned_words[:DAILY_WORDS - len(selected_words)])
    else:
        selected_words = random.sample(unlearned_words, DAILY_WORDS)

    return selected_words


# 更新学习进度
def update_progress(progress, word, learned, date):
    """更新学习进度"""
    if "word_progress" not in progress:
        progress["word_progress"] = {}

    if word not in progress["word_progress"]:
        progress["word_progress"][word] = []

    progress["word_progress"][word].append({
        "date": date,
        "learned": learned
    })

    if date not in progress.get("daily_progress", {}):
        progress["daily_progress"] = {}

    if date not in progress["daily_progress"]:
        progress["daily_progress"][date] = {
            "total": 0,
            "known": 0,
            "unknown": []
        }

    progress["daily_progress"][date]["total"] += 1
    if learned:
        progress["daily_progress"][date]["known"] += 1
    else:
        progress["daily_progress"][date]["unknown"].append(word)

    return progress


# 检查用户今天是否已经学习过
@app.route('/check-learned', methods=['GET'])
def check_learned():
    """检查用户今天是否已经学习过"""
    progress = load_learning_progress()
    today = datetime.now().strftime("%Y-%m-%d")

    learned = today in progress.get("daily_progress", {})
    return jsonify({"learned": learned})


# 获取今日学习单词
@app.route('/get-today-words', methods=['GET'])
def get_today_words_route():
    """获取今日学习单词"""
    all_words = load_word_bank()
    progress = load_learning_progress()
    today_words = get_today_words(all_words, progress)

    if not today_words:
        return jsonify({"message": "今日单词已学习完毕或无可用单词", "words": []})

    # 记录今日单词
    today = datetime.now().strftime("%Y-%m-%d")
    if "learned_words" not in progress:
        progress["learned_words"] = {}

    progress["learned_words"][today] = [word["word"] for word in today_words]
    save_learning_progress(progress)

    return jsonify({"words": today_words})


# 更新单词学习进度
@app.route('/update-progress', methods=['POST'])
def update_progress_route():
    """更新单词学习进度"""
    progress = load_learning_progress()
    data = request.get_json()

    if not data or "word" not in data or "learned" not in data:
        return jsonify({"error": "缺少必要参数"}), 400

    word = data["word"]
    learned = data["learned"]
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    updated_progress = update_progress(progress, word, learned, date)
    save_learning_progress(updated_progress)

    return jsonify({"message": "学习进度已更新"})


# 保存学习进度
@app.route('/save-progress', methods=['POST'])
def save_progress_route():
    """保存学习进度"""
    progress = load_learning_progress()
    data = request.get_json()

    if not data or "date" not in data or "totalWords" not in data:
        return jsonify({"error": "缺少必要参数"}), 400

    date = data["date"]
    total_words = data["totalWords"]
    known_words = data["knownWords"]
    unknown_words = data["unknownWords"]

    if "daily_progress" not in progress:
        progress["daily_progress"] = {}

    progress["daily_progress"][date] = {
        "total": total_words,
        "known": known_words,
        "unknown": unknown_words
    }

    save_learning_progress(progress)

    return jsonify({"message": "学习进度已保存"})


# 用于前端显示
@app.route('/')
def home():
    """Flask应用的根路由"""
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)