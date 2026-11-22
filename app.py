
import streamlit as st
import pandas as pd
import random
from datetime import datetime, date, timedelta

# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="MedTimer",
    page_icon="🌿",
    layout="wide"
)

# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background-color: #F4F7F2;
}

h1, h2, h3 {
    color: #315C4B;
}

.stButton button {
    border-radius: 12px;
    min-height: 42px;
}

div[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #E1E9E1;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STORAGE ----------------

if "medicines" not in st.session_state:
    st.session_state.medicines = []

if "history" not in st.session_state:
    st.session_state.history = []

if "last_date" not in st.session_state:
    st.session_state.last_date = str(date.today())

# Reset today's checklist when a new day begins
if st.session_state.last_date != str(date.today()):
    st.session_state.medicines = []
    st.session_state.last_date = str(date.today())

medicines = st.session_state.medicines

# ---------------- FUNCTIONS ----------------

def adherence(records):
    if len(records) == 0:
        return 0

    completed = sum(m["taken"] for m in records)
    return round((completed / len(records)) * 100, 1)


def get_status(medicine):
    if medicine["taken"]:
        return "🟢 Recorded as taken"

    scheduled = datetime.strptime(
        medicine["time"], "%I:%M %p"
    ).time()

    current_time = datetime.now().time()

    if current_time < scheduled:
        return "🟡 Upcoming"

    return "🔴 Due — not yet recorded"


messages = [
    "Small steps make a big difference! 🌱",
    "You're building an organized routine.",
    "Every day is a fresh start.",
    "Progress matters more than perfection.",
    "Keep your schedule organized!"
]

# ---------------- HEADER ----------------

st.title("🌿 MedTimer")
st.subheader("Your Daily Health Companion")

st.write(
    "A simple way to organize your daily medicine schedule "
    "and keep track of your progress."
)

st.divider()

# ---------------- DASHBOARD ----------------

total = len(medicines)
completed = sum(m["taken"] for m in medicines)
remaining = total - completed
progress = adherence(medicines)

col1, col2, col3 = st.columns(3)

col1.metric("Scheduled", total)
col2.metric("Recorded as taken", completed)
col3.metric("Remaining", remaining)

st.progress(progress / 100)

st.write(f"**Today's progress: {progress}%**")

if progress == 100 and total > 0:
    st.success("🏆 All scheduled records completed!")
elif progress >= 50:
    st.info("⭐ Good progress so far!")
else:
    st.info("🌱 Your progress is being tracked.")

st.caption(random.choice(messages))

st.divider()

# ---------------- ADD MEDICINE ----------------

st.header("➕ Add to your schedule")

with st.form("medicine_form", clear_on_submit=True):

    medicine_name = st.text_input(
        "Medicine name",
        placeholder="Enter medicine name"
    )

    medicine_time = st.time_input(
        "Scheduled time",
        value=datetime.strptime("08:00 AM", "%I:%M %p").time()
    )

    submitted = st.form_submit_button("Add to schedule")

    if submitted:
        if medicine_name.strip():

            new_medicine = {
                "name": medicine_name.strip(),
                "time": medicine_time.strftime("%I:%M %p"),
                "taken": False,
                "date": str(date.today())
            }

            medicines.append(new_medicine)

            st.success("Schedule entry added!")
            st.rerun()

        else:
            st.warning("Please enter a name.")

# ---------------- DAILY CHECKLIST ----------------

st.header("📋 Today's schedule")

if not medicines:
    st.info("Your schedule is empty. Add an entry above.")

else:

    # Sort entries by scheduled time
    medicines.sort(
        key=lambda m: datetime.strptime(
            m["time"], "%I:%M %p"
        )
    )

    for i, medicine in enumerate(medicines):

        with st.container(border=True):

            col1, col2, col3 = st.columns([3, 2, 2])

            col1.markdown(f"### {medicine['name']}")
            col1.write(f"🕒 {medicine['time']}")

            col2.write(get_status(medicine))

            if not medicine["taken"]:

                if col3.button(
                    "Mark as taken",
                    key=f"taken_{i}"
                ):

                    medicine["taken"] = True

                    st.session_state.history.append({
                        "name": medicine["name"],
                        "date": str(date.today()),
                        "time": medicine["time"],
                        "recorded_at": datetime.now().strftime("%H:%M")
                    })

                    st.rerun()

            else:
                col3.success("Completed ✓")

            # Editing
            with st.expander("Edit / Delete"):

                updated_name = st.text_input(
                    "Change name",
                    value=medicine["name"],
                    key=f"name_{i}"
                )

                updated_time = st.time_input(
                    "Change scheduled time",
                    value=datetime.strptime(
                        medicine["time"], "%I:%M %p"
                    ).time(),
                    key=f"time_{i}"
                )

                if st.button("Save changes", key=f"edit_{i}"):

                    medicine["name"] = updated_name
                    medicine["time"] = updated_time.strftime(
                        "%I:%M %p"
                    )

                    st.success("Updated!")
                    st.rerun()

                if st.button("Delete entry", key=f"delete_{i}"):

                    medicines.pop(i)
                    st.rerun()

# ---------------- ACHIEVEMENTS ----------------

st.divider()

st.header("🏅 Achievements")

if total == 0:
    st.write("🌱 Add your first schedule entry to begin!")

elif completed == 0:
    st.write("🌱 Ready to begin!")

elif completed == total:
    st.success("🏆 Daily completion achievement!")

else:
    st.write("⭐ First step achievement!")

# ---------------- ACTIVITY HISTORY ----------------

st.divider()

st.header("📅 Recorded activity")

if st.session_state.history:

    history_df = pd.DataFrame(st.session_state.history)

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.write("Your recorded activity will appear here.")

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "MedTimer is an educational tracking application. "
    "It does not provide medical advice or replace instructions "
    "from a healthcare professional."
)
