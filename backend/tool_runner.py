#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import random
import csv
import matplotlib.pyplot as plt
from algorithm_core import get_risk_level, get_suggestions, suggestion_db


# In[28]:


#主程序（输入——计算——输出）；单条测试用
# 示例输入（你可以改成 input() 让用户输入）
user_answers = {
    "任务厌恶": 80,
    "结果价值": 40,
    "自我控制": 50
}

level = get_risk_level(user_answers)
tips = get_suggestions(level)

print("你的拖延风险等级：", level)
print("个性化建议：")
for tip in tips:
    #删除所有换行、首尾空格，再标准化标点

    print(f"-{tip}")


# In[29]:


#===批量测试多条数据===
test_cases = [
    {"任务厌恶": 80, "结果价值": 40, "自我控制": 50},  # 预期：高
    {"任务厌恶": 50, "结果价值": 60, "自我控制": 60},  # 预期：中
    {"任务厌恶": 20, "结果价值": 90, "自我控制": 80},  # 预期：低
    {"任务厌恶": 70, "结果价值": 30, "自我控制": 40},  # 预期：高
]

w1, w2, w3 = 0.4, 0.3, 0.3

print("=== 批量测试结果 ===")
for i, answers in enumerate(test_cases, 1):
    score = (
        answers["任务厌恶"] * w1 +
        (100 - answers["结果价值"]) * w2 +
        (100 - answers["自我控制"]) * w3
    )
    if score < 30:
        level = "低"
    elif score < 70:
        level = "中"
    else:
        level = "高"

    tip = random.choice(suggestion_db[level])

    print(f"\n【测试 {i}】")
    print(f"输入：{answers}")
    print(f"风险分数：{score:.1f} → 风险等级：{level}")
    print("建议：-", tip)


# In[30]:


#批量测试导出csv
import random
import csv

# ===== 批量测试多条数据并导出 CSV =====
test_cases = [
    {"任务厌恶": 80, "结果价值": 40, "自我控制": 50},
    {"任务厌恶": 50, "结果价值": 60, "自我控制": 60},
    {"任务厌恶": 20, "结果价值": 90, "自我控制": 80},
    {"任务厌恶": 70, "结果价值": 30, "自我控制": 40},
]

w1, w2, w3 = 0.4, 0.3, 0.3

# CSV 文件名
filename = "test_results.csv"

# 打开文件写入（utf-8-sig 保证 WPS 无乱码）
with open(filename, mode="w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    # 写表头
    writer.writerow(["编号", "任务厌恶", "结果价值", "自我控制", "风险分数", "风险等级", "建议"])

    print("=== 批量测试结果 ===")
    for i, answers in enumerate(test_cases, 1):
        score = (
            answers["任务厌恶"] * w1 +
            (100 - answers["结果价值"]) * w2 +
            (100 - answers["自我控制"]) * w3
        )
        if score < 30:
            level = "低"
        elif score < 70:
            level = "中"
        else:
            level = "高"

        tip = random.choice(suggestion_db[level])

        # 写入 CSV
        writer.writerow([i, answers["任务厌恶"], answers["结果价值"], answers["自我控制"], round(score, 1), level, tip])

        # 同时在 Notebook 里打印
        print(f"\n【测试 {i}】")
        print(f"输入：{answers}")
        print(f"风险分数：{score:.1f} → 风险等级：{level}")
        print("建议：-", tip)

print(f"\n测试结果已导出到文件：{filename}")


# In[31]:


import random
import csv
import matplotlib.pyplot as plt

# ===== 批量测试多条数据并导出 CSV + 生成图片（带完整标注） =====
test_cases = [
    {"任务厌恶": 80, "结果价值": 40, "自我控制": 50},
    {"任务厌恶": 50, "结果价值": 60, "自我控制": 60},
    {"任务厌恶": 20, "结果价值": 90, "自我控制": 80},
    {"任务厌恶": 70, "结果价值": 30, "自我控制": 40},
]

w1, w2, w3 = 0.4, 0.3, 0.3

# 用于存储结果以便绘图
results = []

# CSV 文件名
filename = "test_results.csv"

# 打开文件写入（utf-8-sig 保证 WPS 无乱码）
with open(filename, mode="w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["编号", "任务厌恶", "结果价值", "自我控制", "风险分数", "风险等级", "建议"])

    print("=== 批量测试结果 ===")
    for i, answers in enumerate(test_cases, 1):
        score = (
            answers["任务厌恶"] * w1 +
            (100 - answers["结果价值"]) * w2 +
            (100 - answers["自我控制"]) * w3
        )
        if score < 30:
            level = "低"
        elif score < 70:
            level = "中"
        else:
            level = "高"

        tip = random.choice(suggestion_db[level])

        # 保存结果
        results.append((i, answers["任务厌恶"], answers["结果价值"], answers["自我控制"], round(score, 1), level, tip))

        # 写入 CSV
        writer.writerow([i, answers["任务厌恶"], answers["结果价值"], answers["自我控制"], round(score, 1), level, tip])

        # 打印
        print(f"\n【测试 {i}】")
        print(f"输入：{answers}")
        print(f"风险分数：{score:.1f} → 风险等级：{level}")
        print("建议：-", tip)

print(f"\n测试结果已导出到文件：{filename}")

# ===== 统计绘图数据 =====
level_count = {"高": 0, "中": 0, "低": 0}
for _, _, _, _, _, level, _ in results:
    level_count[level] += 1

numbers = [r[0] for r in results]           # 编号
scores = [r[4] for r in results]           # 风险分数

# ===== 生成三合一多子图 =====
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 子图1：风险等级分布柱状图
bars = axes[0].bar(level_count.keys(), level_count.values(), 
                   color=["red", "orange", "green"], 
                   label=["高风险", "中风险", "低风险"])
for bar in bars:
    height = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width()/2, height + 0.05,
                 f'{int(height)}', ha='center', va='bottom')
axes[0].set_title("风险等级分布", fontsize=14)
axes[0].set_xlabel("风险等级", fontsize=12)
axes[0].set_ylabel("数量", fontsize=12)
axes[0].legend(title="图例")

# 子图2：风险分数折线图
axes[1].plot(numbers, scores, marker='o', color='blue', linewidth=2, markersize=8)
axes[1].set_title("各测试案例风险分数变化", fontsize=14)
axes[1].set_xlabel("测试编号", fontsize=12)
axes[1].set_ylabel("风险分数", fontsize=12)
axes[1].set_xticks(numbers)
axes[1].grid(True, linestyle='--', alpha=0.5)
for x, y in zip(numbers, scores):
    axes[1].text(x, y + 1, f"{y}", ha='center', va='bottom', fontsize=10)

# 子图3：各风险等级建议占比饼图（带颜色说明）
pie_data = [level_count["高"], level_count["中"], level_count["低"]]
labels = ["高风险\n(红色)", "中风险\n(橙色)", "低风险\n(绿色)"]
colors = ["red", "orange", "green"]
wedges, texts, autotexts = axes[2].pie(
    pie_data, 
    labels=labels, 
    colors=colors, 
    autopct="%1.1f%%", 
    startangle=140,
    textprops={'fontsize': 12}
)
axes[2].set_title("各风险等级建议占比", fontsize=14)
axes[2].axis("equal")

plt.tight_layout()
plt.savefig("summary_figure.png", dpi=150, bbox_inches="tight")
plt.show()

print("三合一汇总图已保存为：summary_figure.png")


# In[32]:


#命令行交互版主程序
import random

def main():
    print("=== 拖延小工具 MVP（命令行版）===")

    # 1. 输入
    print("\n请按 0-100 打分：")
    task_aversion = int(input("1）任务厌恶度（越讨厌这任务分数越高）："))
    result_value = int(input("2）结果价值感（任务完成后对你多重要）："))
    self_control = int(input("3）自我控制能力（你觉得自己自控力如何）："))

    # 2. 计算风险等级（直接用 score 变量）
    w1, w2, w3 = 0.4, 0.3, 0.3
    score = (
        task_aversion * w1 +
        (100 - result_value) * w2 +
        (100 - self_control) * w3
    )

    if score < 30:
        level = "低"
    elif score < 70:
        level = "中"
    else:
        level = "高"

    # 3. 取建议
    tips = suggestion_db[level]
    tip = random.choice(tips)

    # 4. 输出
    print(f"\n你的拖延风险等级：{level}")
    print("给你一条个性化建议：")
    print("-", tip)

# 运行
main()


# In[ ]:




