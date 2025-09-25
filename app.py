import streamlit as st 
import json
import os
from openai import OpenAI

st.set_page_config(page_title="Camanda LMS AI Agent", page_icon="🎓", layout="wide")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OpenAI API key not found. Please add it in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

@st.cache_data
def load_lms_data():
    with open("courses.json") as f:
        return json.load(f)

lms_data = load_lms_data()

def camanda_context():
    return {
        "role": "system",
        "content": (
            "You are an AI Agent in Camanda Academy's LMS. "
            "Here is the LMS data (courses, assignments, schedules, onboarding):\n\n"
            f"{json.dumps(lms_data, indent=2)}"
        )
    }

if st.sidebar.button("🔄 Reset Onboarding"):
    if "onboarded" in st.session_state:
        del st.session_state["onboarded"]
    st.rerun()

if "onboarded" not in st.session_state:
    st.title("👋 Welcome to Camanda LMS!")
    st.write("Since this is your first time here, let’s get you started with onboarding.")

    if "onboarding" in lms_data:
        st.subheader("Your Onboarding Checklist")
        for step in lms_data["onboarding"]["steps"]:
            st.checkbox(step, value=False, disabled=True)

        st.info("✅ Complete these steps to get familiar with Camanda LMS!")

    if st.button("Continue to Dashboard ➡️"):
        st.session_state["onboarded"] = True
        st.rerun()

    st.stop()

col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("### 🎓 Camanda LMS AI Agent - Welcome, **Emmanuel**")
with col2:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

st.sidebar.title("Dashboard")
agent_choice = st.sidebar.radio(
    "Choose an Agent:",
    ["Tutor Assistant", "Study Buddy", "Admin Helper", "Career Coach"]
)

agent_configs = {
    "Tutor Assistant": {
        "state_key": "tutor_chat",
        "header": "📘 Tutor Assistant",
        "caption": "Ask me about assignments, schedules, or study materials.",
        "prompt": "Ask your Tutor Assistant...",
        "system_message": "You are a helpful Tutor Assistant in Camanda LMS."
    },
    "Study Buddy": {
        "state_key": "buddy_chat",
        "header": "🤝 Study Buddy",
        "caption": "I’m your friendly study partner. I’ll motivate you and quiz you.",
        "prompt": "Chat with your Study Buddy...",
        "system_message": "You are a friendly Study Buddy. Motivate learners and quiz them."
    },
    "Admin Helper": {
        "state_key": "admin_chat",
        "header": "⚙️ Admin Helper",
        "caption": "I help with LMS admin tasks (managing courses, users, etc.).",
        "prompt": "Ask Admin Helper...",
        "system_message": "You are the LMS Admin Helper. Give clear, structured answers."
    },
    "Career Coach": {  
        "state_key": "career_chat",
        "header": "💼 Career Coach",
        "caption": "Ask me for career guidance, skills advice, and course recommendations.",
        "prompt": "Ask your Career Coach...",
        "system_message": "You are a Career Coach. Give practical, encouraging advice and recommend courses/skills based on user goals."
    }
}

config = agent_configs[agent_choice]

st.header(config["header"])
st.caption(config["caption"])

if config["state_key"] not in st.session_state:
    st.session_state[config["state_key"]] = [
        {"role": "assistant", "content": "👋 Welcome to Camanda LMS AI! How can I help you today?"}
    ]

for msg in st.session_state[config["state_key"]]:
    if msg["role"] == "user":
        st.chat_message("user", avatar="👨‍💻").write(msg["content"])
    else:
        st.chat_message("assistant", avatar="🤖").write(msg["content"])

user_input = st.chat_input(config["prompt"])

if user_input:
    st.session_state[config["state_key"]].append({"role": "user", "content": user_input})
    st.rerun()

if st.session_state[config["state_key"]]:
    last_msg = st.session_state[config["state_key"]][-1]

    if last_msg["role"] == "user":
        reply = None
        lower_msg = last_msg["content"].lower()

        if agent_choice == "Tutor Assistant":
            if "assignment" in lower_msg:
                assignments = []
                for course in lms_data["courses"]:
                    for a in course["assignments"]:
                        assignments.append(f"**{course['name']}**: {a['title']} (📅 Due {a['due']})")
                reply = "Here are your assignments:\n\n" + "\n".join(assignments)

            elif "schedule" in lower_msg or "class" in lower_msg:
                schedule = []
                for course in lms_data["courses"]:
                    for s in course["schedule"]:
                        schedule.append(f"**{course['name']}**: {s['day']} at {s['time']}")
                reply = "Here’s your schedule:\n\n" + "\n".join(schedule)

        if agent_choice == "Study Buddy" and "quiz" in lower_msg:
            quizzes = []
            for course in lms_data["courses"]:
                quizzes.append(f"**{course['name']}**:")
                for t in course["topics"]:
                    quizzes.append(f"- What do you know about *{t}*?")
            reply = "Here’s a quiz for you:\n\n" + "\n".join(quizzes)

        if agent_choice == "Career Coach":
            matched = []
            for course in lms_data.get("courses", []):
                course_text = (course.get("name", "") + " " + " ".join(course.get("topics", []))).lower()
                if any(token in lower_msg for token in course_text.split()):
                    matched.append(course)

            if matched:
                recs = []
                for c in matched:
                    rec_line = f"**{c['name']}** — topics: {', '.join(c.get('topics', []))}."
                    enrollment = c.get("enrollment", {}).get("steps") if c.get("enrollment") else None
                    if enrollment:
                        rec_line += f" Enrollment: {enrollment[0]} (see course page for full steps)."
                    recs.append(rec_line)
                reply = (
                    "Based on what you said, here are some Camanda courses that look relevant:\n\n"
                    + "\n".join(recs)
                    + "\n\nIf you'd like, I can suggest which course to start with given your goals — tell me a bit about your career interests."
                )

            else:
                messages = [camanda_context()]
                messages.append({"role": "system", "content": config["system_message"]})
                messages.extend(st.session_state[config["state_key"]])

                with st.spinner("Thinking... 🤔"):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages
                    )
                reply = response.choices[0].message.content

        if reply is None:
            messages = [camanda_context()] 
            messages.append({"role": "system", "content": config["system_message"]})
            messages.extend(st.session_state[config["state_key"]])

            with st.spinner("Thinking... 🤔"):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )
            reply = response.choices[0].message.content

        st.session_state[config["state_key"]].append({"role": "assistant", "content": reply})
        st.rerun()
