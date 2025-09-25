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

def camanda_context():
    """Turn courses.json into a text context string for the AI."""
    context = "Here is Camanda LMS data:\n"
    for course in lms_data.get("courses", []):
        context += f"\n📘 Course: {course['name']}\n"
        if "assignments" in course:
            for a in course["assignments"]:
                context += f"- Assignment: {a['title']} (Due {a['due']})\n"
        if "schedule" in course:
            for s in course["schedule"]:
                context += f"- Schedule: {s['day']} at {s['time']}\n"
        if "topics" in course:
            context += "- Topics: " + ", ".join(course["topics"]) + "\n"
    return context

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

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful Tutor Assistant in Camanda LMS. Use the knowledge provided when possible."},
                {"role": "system", "content": camanda_context()},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content

        st.session_state["tutor_chat"].append({"role": "assistant", "content": reply})
        st.rerun()

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

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly Study Buddy. Motivate learners and quiz them. Use the Camanda LMS data when useful."},
                {"role": "system", "content": camanda_context()},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content

        st.session_state["buddy_chat"].append({"role": "assistant", "content": reply})
        st.rerun()

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
                {"role": "system", "content": "You are the LMS Admin Helper. Give clear, structured answers, and use Camanda knowledge when useful."},
                {"role": "system", "content": camanda_context()},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content

        st.session_state["admin_chat"].append({"role": "assistant", "content": reply})
        st.rerun()
