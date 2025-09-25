import streamlit as st 
import json
import os
from openai import OpenAI

st.set_page_config(page_title="Camanda LMS AI Agent", page_icon="🎓", layout="wide")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("courses.json") as f:
    lms_data = json.load(f)

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
    ["Tutor Assistant", "Study Buddy", "Admin Helper"]
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
    }
}

config = agent_configs[agent_choice]

st.header(config["header"])
st.caption(config["caption"])

if config["state_key"] not in st.session_state:
    st.session_state[config["state_key"]] = []

for msg in st.session_state[config["state_key"]]:
    st.chat_message(msg["role"]).markdown(msg["content"])

user_input = st.chat_input(config["prompt"])

if user_input:
    st.session_state[config["state_key"]].append({"role": "user", "content": user_input})
    reply = None
    lower_msg = user_input.lower()

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

    if reply is None:
        messages = [
            {"role": "system", "content": config["system_message"]},
        ]
        messages.extend(st.session_state[config["state_key"]]) 
        messages.append({"role": "user", "content": user_input})

        with st.spinner("Thinking... 🤔"): 
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
        reply = response.choices[0].message.content

    st.session_state[config["state_key"]].append({"role": "assistant", "content": reply})
    st.rerun()
