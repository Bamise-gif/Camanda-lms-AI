import streamlit as st 
import json
import os
from openai import OpenAI

st.set_page_config(page_title="Camanda LMS", page_icon="🎓", layout="wide")

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

# ===========================
# MAIN DASHBOARD LAYOUT
# ===========================
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("### 🎓 Camanda LMS Dashboard - Welcome, **Emmanuel**")
with col2:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# ===========================
# SIDEBAR MENU
# ===========================
st.sidebar.title("Navigation")
menu_choice = st.sidebar.radio(
    "Go to:",
    ["Dashboard", "My Courses", "Assignments", "Progress", "Schedule", "Discussion", "Settings", "AI Mode"]
)

# ===========================
# DASHBOARD TAB
# ===========================
if menu_choice == "Dashboard":
    st.header("📊 Dashboard Overview")

    tab1, tab2, tab3, tab4 = st.tabs(["Active Courses", "Assignments Due", "Learning Hours", "AI Recommendations"])

    with tab1:
        st.subheader("Your Active Courses")
        for course in lms_data.get("courses", []):
            st.write(f"- **{course['name']}** ({len(course['topics'])} topics)")

    with tab2:
        st.subheader("Assignments Due")
        for course in lms_data.get("courses", []):
            for a in course["assignments"]:
                st.write(f"- **{a['title']}** for {course['name']} (📅 Due: {a['due']})")

    with tab3:
        st.subheader("Learning Hours Summary")
        st.info("📈 You’ve logged approximately 25 learning hours this month.")

    with tab4:
        st.subheader("AI Recommendations")
        st.write("🤖 Based on your activity, here are some suggested next steps:")
        st.markdown("- Review your pending assignments.")
        st.markdown("- Continue ‘Python for Beginners’ course.")
        st.markdown("- Explore Data Visualization lessons in Power BI.")

# ===========================
# MY COURSES TAB
# ===========================
elif menu_choice == "My Courses":
    st.header("📚 My Courses")
    for course in lms_data.get("courses", []):
        with st.expander(course["name"]):
            st.write("**Topics:**", ", ".join(course["topics"]))
            st.write("**Instructor:**", course.get("instructor", "N/A"))
            st.write("**Schedule:**")
            for s in course["schedule"]:
                st.write(f"- {s['day']} at {s['time']}")

    st.info("💡 Tip: Click the button below to chat with AI about your courses.")
    if st.button("💬 Open AI Mode for Interactive Learning"):
        st.session_state["open_ai_mode"] = True
        st.session_state["active_section"] = "Courses"
        st.rerun()

# ===========================
# ASSIGNMENTS TAB
# ===========================
elif menu_choice == "Assignments":
    st.header("📝 Assignments")
    for course in lms_data.get("courses", []):
        st.subheader(course["name"])
        for a in course["assignments"]:
            st.write(f"- {a['title']} (📅 Due: {a['due']})")
    st.info("💬 Need help? Open AI Mode to get explanations or summaries of assignments.")

# ===========================
# PROGRESS TAB
# ===========================
elif menu_choice == "Progress":
    st.header("📈 Learning Progress")
    st.write("Here’s a summary of your learning achievements so far:")
    st.progress(0.68)
    st.write("✅ You’ve completed 68% of your active courses.")
    st.info("💬 Open AI Mode to get personalized improvement tips.")

# ===========================
# SCHEDULE TAB
# ===========================
elif menu_choice == "Schedule":
    st.header("📅 Class Schedule")
    for course in lms_data.get("courses", []):
        for s in course["schedule"]:
            st.write(f"**{course['name']}**: {s['day']} at {s['time']}")
    st.info("💬 Ask AI for reminders or scheduling recommendations in AI Mode.")

# ===========================
# DISCUSSION TAB
# ===========================
elif menu_choice == "Discussion":
    st.header("💬 Discussion Forum")
    st.write("Join conversations, share ideas, and collaborate with classmates!")
    st.info("💡 Tip: AI Mode can summarize or highlight key discussion points for you.")

# ===========================
# SETTINGS TAB
# ===========================
elif menu_choice == "Settings":
    st.header("⚙️ Settings")
    st.write("Manage your account, notifications, and preferences here.")

# ===========================
# AI MODE TAB (General Chat)
# ===========================
elif menu_choice == "AI Mode":
    st.header("🤖 AI Mode - Interactive Learning Assistant")
    st.caption("Chat with Camanda AI for explanations, guidance, and recommendations.")

    # Initialize chat history
    if "ai_chat" not in st.session_state:
        st.session_state["ai_chat"] = [
            {"role": "assistant", "content": "👋 Welcome to AI Mode! How can I help you today?"}
        ]

    # Expandable chat panel
    with st.expander("🧠 Open AI Chat Panel", expanded=True):
        for msg in st.session_state["ai_chat"]:
            if msg["role"] == "user":
                st.chat_message("user", avatar="👨‍💻").write(msg["content"])
            else:
                st.chat_message("assistant", avatar="🤖").write(msg["content"])

        # Quick start suggestions
        st.markdown("#### 💡 Quick Start Suggestions")
        st.markdown("- Explain my assignment")
        st.markdown("- Recommend a study plan")
        st.markdown("- Suggest career paths")
        st.markdown("- Help me understand a course topic")

        user_input = st.chat_input("Ask Camanda AI anything...")

        if user_input:
            st.session_state["ai_chat"].append({"role": "user", "content": user_input})
            messages = [camanda_context()]
            messages.extend(st.session_state["ai_chat"])

            with st.spinner("Thinking... 🤔"):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )
            reply = response.choices[0].message.content
            st.session_state["ai_chat"].append({"role": "assistant", "content": reply})
            st.rerun()
