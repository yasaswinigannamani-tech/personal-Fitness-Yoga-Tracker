# llm_engine.py
"""LLM Engine - Generates personalized yoga routines.
Integrates Arrays (lists of asanas) and rule-based AI logic.
"""

import random
from datetime import datetime, timedelta

# Arrays of yoga asanas categorized by type (Topics: Arrays)
BEGINNER_ASANAS = [
    ("Tadasana", "Mountain Pose", "Improves posture and focus"),
    ("Vrikshasana", "Tree Pose", "Enhances balance"),
    ("Bhujangasana", "Cobra Pose", "Strengthens spine"),
    ("Balasana", "Child's Pose", "Relieves stress"),
    ("Marjariasana", "Cat-Cow Pose", "Flexibility of spine"),
]

INTERMEDIATE_ASANAS = [
    ("Trikonasana", "Triangle Pose", "Stretches legs and torso"),
    ("Virabhadrasana", "Warrior Pose", "Strengthens legs"),
    ("Setu Bandhasana", "Bridge Pose", "Calms the brain"),
    ("Dhanurasana", "Bow Pose", "Strengthens back muscles"),
    ("Paschimottanasana", "Seated Forward Bend", "Stretches hamstrings"),
]

ADVANCED_ASANAS = [
    ("Sirsasana", "Headstand", "Improves circulation"),
    ("Sarvangasana", "Shoulder Stand", "Boosts immunity"),
    ("Padmasana", "Lotus Pose", "Calms the mind"),
    ("Bakasana", "Crow Pose", "Builds core strength"),
    ("Chakrasana", "Wheel Pose", "Full body stretch"),
]

PRANAYAMA = [
    ("Anulom Vilom", "Alternate Nostril Breathing", 5, "Balances mind"),
    ("Kapalbhati", "Skull Shining Breath", 3, "Detoxifies body"),
    ("Bhramari", "Bee Breath", 5, "Reduces anxiety"),
    ("Ujjayi", "Ocean Breath", 5, "Builds energy"),
]

MEDITATION = [
    ("Mindfulness Meditation", 10, "Improves concentration"),
    ("Guided Visualization", 15, "Reduces stress"),
    ("Body Scan", 10, "Releases tension"),
    ("Loving-Kindness", 12, "Develops compassion"),
]


def get_asana_pool(level):
    """Return array of asanas based on fitness level."""
    if level == "beginner":
        return BEGINNER_ASANAS
    elif level == "intermediate":
        return BEGINNER_ASANAS + INTERMEDIATE_ASANAS
    else:
        return BEGINNER_ASANAS + INTERMEDIATE_ASANAS + ADVANCED_ASANAS


def generate_weekly_plan(user_data, logs):
    """LLM-like engine: generates personalized weekly yoga plan.
    
    Uses arrays to store plan, considers user's fitness level,
    available time, goals, and past practice history.
    
    Returns: Array of 7 daily plans (Monday-Sunday)
    """
    level = user_data.get("level", "beginner")
    goal = user_data.get("goal", "general")
    time_per_day = user_data.get("time_per_day", 30)
    name = user_data.get("name", "Yogi")

    asana_pool = get_asana_pool(level)
    weekly_plan = []

    # Analyze past practices using arrays
    practiced_asanas = [log["asana"] for log in logs] if logs else []

    days = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]

    # Focus themes for each day (array)
    day_themes = [
        "Grounding & Stability",
        "Strength Building",
        "Flexibility & Stretching",
        "Balance & Focus",
        "Core Strength",
        "Full Body Flow",
        "Restoration & Meditation"
    ]

    for i, day in enumerate(days):
        # Select 3-4 asanas based on theme
        num_asanas = min(4, max(2, time_per_day // 10))
        selected = random.sample(asana_pool, num_asanas)

        # Add pranayama
        pranayama = random.choice(PRANAYAMA)

        # Add meditation on rest days
        meditation = random.choice(MEDITATION) if i == 6 else None

        daily_plan = {
            "day": day,
            "theme": day_themes[i],
            "asanas": [
                {
                    "name": asana[0],
                    "english_name": asana[1],
                    "benefit": asana[2],
                    "duration_minutes": time_per_day // num_asanas
                }
                for asana in selected
            ],
            "pranayama": {
                "name": pranayama[0],
                "english": pranayama[1],
                "duration": pranayama[2],
                "benefit": pranayama[3]
            },
            "meditation": {
                "name": meditation[0],
                "duration": meditation[1],
                "benefit": meditation[2]
            } if meditation else None,
            "total_time": time_per_day
        }
        weekly_plan.append(daily_plan)

    # Generate LLM-style motivational message
    messages = {
        "beginner": f"Namaste {name}! Your weekly plan focuses on building foundations. "
                    f"Remember: consistency beats intensity. Start slow, breathe deeply. 🌱",
        "intermediate": f"Namaste {name}! Time to deepen your practice. "
                        f"Focus on alignment and breath-movement coordination. 🔥",
        "advanced": f"Namaste {name}! Your advanced plan challenges both body and mind. "
                   f"Honor your body's limits while exploring your edges. ✨"
    }

    # Goal-specific tip
    goal_tips = {
        "weight_loss": "Tip: Practice Surya Namaskar daily for effective calorie burn.",
        "stress_relief": "Tip: End each session with 5 min of Bhramari pranayama.",
        "flexibility": "Tip: Hold each stretch for 30-60 seconds for maximum benefit.",
        "strength": "Tip: Focus on poses like Warrior and Plank for building strength.",
        "general": "Tip: Balance effort with ease. Yoga is about harmony, not perfection."
    }

    return {
        "plan": weekly_plan,
        "motivation": messages.get(level, messages["beginner"]),
        "goal_tip": goal_tips.get(goal, goal_tips["general"]),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "practiced_count": len(practiced_asanas)
    }


def analyze_progress(logs):
    """Analyze practice logs using arrays and return statistics."""
    if not logs:
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "avg_intensity": 0,
            "most_practiced": "None yet",
            "streak": 0,
            "weekly_distribution": [0] * 7
        }

    # Arrays for analysis
    asana_count = {}
    total_minutes = 0
    intensity_sum = 0
    weekly_dist = [0] * 7  # Monday=0 ... Sunday=6

    for log in logs:
        # Count asana frequency
        asana = log["asana"]
        asana_count[asana] = asana_count.get(asana, 0) + 1

        total_minutes += log["duration"]
        intensity_sum += log["intensity"]

        # Weekly distribution
        try:
            log_date = datetime.strptime(log["date"], "%Y-%m-%d")
            weekly_dist[log_date.weekday()] += 1
        except (ValueError, KeyError):
            pass

    # Find most practiced asana (sort array)
    sorted_asanas = sorted(asana_count.items(),
                           key=lambda x: x[1], reverse=True)
    most_practiced = sorted_asanas[0][0] if sorted_asanas else "None"

    # Calculate streak
    dates = sorted(set(log["date"] for log in logs), reverse=True)
    streak = 1 if dates else 0
    for i in range(len(dates) - 1):
        d1 = datetime.strptime(dates[i], "%Y-%m-%d")
        d2 = datetime.strptime(dates[i + 1], "%Y-%m-%d")
        if (d1 - d2).days == 1:
            streak += 1
        else:
            break

    return {
        "total_sessions": len(logs),
        "total_minutes": total_minutes,
        "avg_intensity": round(intensity_sum / len(logs), 1) if logs else 0,
        "most_practiced": most_practiced,
        "streak": streak,
        "weekly_distribution": weekly_dist,
        "asana_frequency": dict(sorted_asanas[:5])
    }