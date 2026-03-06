"""CrewAI 生活助理示例：闹钟提醒、会议安排、健身计划。"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai_tools import tool

DATA_FILE = Path(__file__).parent / "assistant_data.json"


def _load_data() -> dict[str, Any]:
    if not DATA_FILE.exists():
        return {"alarms": [], "meetings": [], "fitness_plans": []}
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _save_data(data: dict[str, Any]) -> None:
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@tool("set_alarm")
def set_alarm(time_text: str, label: str) -> str:
    """创建闹钟提醒。time_text 使用 YYYY-MM-DD HH:MM 格式。"""
    dt = datetime.strptime(time_text, "%Y-%m-%d %H:%M")
    data = _load_data()
    data["alarms"].append({"time": dt.isoformat(), "label": label})
    _save_data(data)
    return f"闹钟已设置：{dt.strftime('%Y-%m-%d %H:%M')} - {label}"


@tool("schedule_meeting")
def schedule_meeting(title: str, start_time: str, duration_minutes: int, participants: str) -> str:
    """安排会议。participants 使用逗号分隔。时间格式 YYYY-MM-DD HH:MM。"""
    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    meeting = {
        "title": title,
        "start": start.isoformat(),
        "duration_minutes": duration_minutes,
        "participants": [p.strip() for p in participants.split(",") if p.strip()],
    }
    data = _load_data()
    data["meetings"].append(meeting)
    _save_data(data)
    return f"会议已安排：{title}，开始于 {start.strftime('%Y-%m-%d %H:%M')}，时长 {duration_minutes} 分钟。"


@tool("build_fitness_plan")
def build_fitness_plan(goal: str, days_per_week: int, level: str) -> str:
    """创建健身计划。level 可选 beginner/intermediate/advanced。"""
    templates = {
        "beginner": ["快走 30 分钟", "自重深蹲 3x12", "平板支撑 3x30 秒"],
        "intermediate": ["慢跑 40 分钟", "俯卧撑 4x15", "深蹲 4x15", "核心训练 15 分钟"],
        "advanced": ["间歇跑 30 分钟", "力量训练 45 分钟", "HIIT 20 分钟", "拉伸恢复 15 分钟"],
    }
    exercises = templates.get(level.lower(), templates["beginner"])
    plan = {
        "goal": goal,
        "days_per_week": days_per_week,
        "level": level,
        "workouts": exercises,
    }
    data = _load_data()
    data["fitness_plans"].append(plan)
    _save_data(data)
    return f"已生成每周 {days_per_week} 天的健身计划（{level}）：" + "；".join(exercises)


def build_crew() -> Crew:
    life_assistant = Agent(
        role="生活助理",
        goal="帮助用户管理日程、提醒事项和健身计划",
        backstory="你是一个细致、可靠的私人生活助理，能够主动整理任务并给出清晰建议。",
        tools=[set_alarm, schedule_meeting, build_fitness_plan],
        verbose=True,
    )

    assistant_task = Task(
        description=(
            "根据用户输入执行对应任务：\n"
            "1) 闹钟提醒：调用 set_alarm\n"
            "2) 会议安排：调用 schedule_meeting\n"
            "3) 健身计划：调用 build_fitness_plan\n"
            "最后输出执行摘要。"
        ),
        expected_output="简要结果摘要，包含新增闹钟、会议、健身计划信息。",
        agent=life_assistant,
    )

    return Crew(
        agents=[life_assistant],
        tasks=[assistant_task],
        process=Process.sequential,
        verbose=True,
    )


if __name__ == "__main__":
    crew = build_crew()

    # 示例输入：可替换为你的真实需求
    result = crew.kickoff(
        inputs={
            "request": (
                "请帮我设置一个明天 07:00 的起床闹钟；"
                "安排周五 10:00 的产品评审会，时长 60 分钟，参与人 Alice,Bob；"
                "制定一个减脂目标、每周 4 天的 beginner 健身计划。"
            )
        }
    )
    print("\n=== 执行结果 ===")
    print(result)
