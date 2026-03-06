# CrewAI 生活助理小助手

本示例基于 **CrewAI** 实现 3 类能力：
- 闹钟提醒（set_alarm）
- 会议安排（schedule_meeting）
- 健身计划（build_fitness_plan）

## 1. 安装
```bash
cd crewai_life_assistant
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 配置
请确保已经配置模型所需环境变量（例如 `OPENAI_API_KEY`）。

## 3. 运行
```bash
python main.py
```

运行后会在当前目录生成 `assistant_data.json`，用于保存闹钟、会议和健身计划数据。

## 4. 二次开发建议
- 将 `assistant_data.json` 替换为数据库（PostgreSQL / Redis）
- 将 `schedule_meeting` 对接 Google Calendar / Outlook API
- 为 `set_alarm` 增加推送通道（邮件、企业微信、钉钉）
