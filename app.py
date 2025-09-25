import streamlit as st
import json
from openai import OpenAI

# ======================
# CONFIG & SETUP
# ======================
st.set_page_config(page_title="Camanda LMS AI Agent", page_icon="🎓", layout="wide")

# ✅ Replace with your OpenAI API key
client = OpenAI(api_key="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")

# ✅ Load LMS data (assignments, quizzes, onboarding, etc.)
with open("courses.json") as f:
    lms_data = json.load(f)

# ======================
# RESET ONBOARDING BUTTON
# ======================
if st.sidebar.button("🔄 Reset Onboarding"):
    if "onboarded" in st.session_state:
        del st.session_state["onboarded"]
    st.rerun()

# ======================
# HANDLE ONBOARDING FLOW
# ======================
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

    st.stop()  # don’t load dashboard until onboarding is done

# ======================
# MAIN DASHBOARD UI
# ======================

# Top bar with user + logout
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("### 🎓 Camanda LMS AI Agent - Welcome, **Emmanuel**")
with col2:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()


# Sidebar menu
st.sidebar.title("AI Agent Dashboard")
agent_choice = st.sidebar.radio(
    "Choose an Agent:",
    ["Tutor Assistant", "Study Buddy", "Admin Helper"]
)

# ======================
# PAGE: Tutor Assistant
# ======================
if agent_choice == "Tutor Assistant":
    st.header("📘 Tutor Assistant")
    st.caption("Ask me about assignments, schedules, or study materials.")

    if "tutor_chat" not in st.session_state:
        st.session_state["tutor_chat"] = []

    for msg in st.session_state["tutor_chat"]:
        st.chat_message(msg["role"]).markdown(msg["content"])

    user_input = st.chat_input("Ask your Tutor Assistant...")
    if user_input:
        st.session_state["tutor_chat"].append({"role": "user", "content": user_input})
        reply = None
        lower_msg = user_input.lower()

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

        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful Tutor Assistant in Camanda LMS."},
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response.choices[0].message.content

        st.session_state["tutor_chat"].append({"role": "assistant", "content": reply})
        st.rerun()

# ======================
# PAGE: Study Buddy
# ======================
elif agent_choice == "Study Buddy":
    st.header("🤝 Study Buddy")
    st.caption("I’m your friendly study partner. I’ll motivate you and quiz you.")

    if "buddy_chat" not in st.session_state:
        st.session_state["buddy_chat"] = []

    for msg in st.session_state["buddy_chat"]:
        st.chat_message(msg["role"]).markdown(msg["content"])

    user_input = st.chat_input("Chat with your Study Buddy...")
    if user_input:
        st.session_state["buddy_chat"].append({"role": "user", "content": user_input})
        reply = None

        if "quiz" in user_input.lower():
            quizzes = []
            for course in lms_data["courses"]:
                quizzes.append(f"**{course['name']}**:")
                for t in course["topics"]:
                    quizzes.append(f"- What do you know about *{t}*?")
            reply = "Here’s a quiz for you:\n\n" + "\n".join(quizzes)
        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a friendly Study Buddy. Motivate learners and quiz them."},
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response.choices[0].message.content

        st.session_state["buddy_chat"].append({"role": "assistant", "content": reply})
        st.rerun()

# ======================
# PAGE: Admin Helper
# ======================
elif agent_choice == "Admin Helper":
    st.header("⚙️ Admin Helper")
    st.caption("I help with LMS admin tasks (managing courses, users, etc.).")

    if "admin_chat" not in st.session_state:
        st.session_state["admin_chat"] = []

    for msg in st.session_state["admin_chat"]:
        st.chat_message(msg["role"]).markdown(msg["content"])

    user_input = st.chat_input("Ask Admin Helper...")
    if user_input:
        st.session_state["admin_chat"].append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are the LMS Admin Helper. Give clear, structured answers."},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content

        st.session_state["admin_chat"].append({"role": "assistant", "content": reply})
        st.rerun()
