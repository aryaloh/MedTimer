import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import csv
import io
import random
from datetime import date, datetime, timedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="MedTimer",
    page_icon="💊",
    layout="wide"
)

# ---------------- SESSION DATA ----------------
if "medicines" not in st.session_state:
    st.session_state.medicines = []

if "logs" not in st.session_state:
    st.session_state.logs = {}

if "next_id" not in st.session_state:
    st.session_state.next_id = 1

# ---------------- STYLING ----------------
st.markdown("""
<style>
    .stApp {
        background-color: #F5F8F4;
    }
    h1, h2, h3 {
        color: #355E50;
    }
    .main {
        padding-top: 1rem;
    }
    div[data-testid="stMetric"] {
        background-color: #E7F0E8;
        padding: 15px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HELPER FUNCTIONS ----------------

def get_log_key(medicine_id, day):
    return f"{medicine_id}_{day.isoformat()}"

def is_taken(medicine_id, day):
    return st.session_state.logs.get(get_log_key(medicine_id, day), False)

def mark_taken(medicine_id, day):
    st.session_state.logs[get_log_key(medicine_id, day)] = True

def unmark_taken(medicine_id, day):
    st.session_state.logs[get_log_key(medicine_id, day)] = False

def get_status(medicine, day):
    key = get_log_key(medicine["id"], day)

    if st.session_state.logs.get(key, False):
        return "Taken", "🟢"

    scheduled_time = datetime.strptime(
        medicine["time"], "%H:%M"
    ).time()

    scheduled_datetime = datetime.combine(day, scheduled_time)
    current_datetime = datetime.now()

    if day < date.today():
        return "Missed", "🔴"

    if day == date.today():
        if current_datetime >= scheduled_datetime:
            return "Due / Missed", "🔴"
        else:
            return "Upcoming", "🟡"

    return "Upcoming", "🟡"

def calculate_weekly_adherence():
    today = date.today()
    start_of_week = today - timedelta(days=6)

    total = 0
    taken_count = 0

    for medicine in st.session_state.medicines:
        medicine_start = medicine["start_date"]

        for day_offset in range(7):
            day = start_of_week + timedelta(days=day_offset)

            if day < medicine_start or day > today:
                continue

            total += 1

            if is_taken(medicine["id"], day):
                taken_count += 1

    if total == 0:
        return 0, 0, 0

    percentage = (taken_count / total) * 100

    return taken_count, total, percentage

def calculate_today():
    scheduled = len(st.session_state.medicines)

    taken = sum(
        1 for medicine in st.session_state.medicines
        if is_taken(medicine["id"], date.today())
    )

    remaining = scheduled - taken

    percentage = (
        (taken / scheduled) * 100
        if scheduled > 0 else 0
    )

    return scheduled, taken, remaining, percentage

def generate_report():
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Date",
        "Medicine",
        "Scheduled Time",
        "Status"
    ])

    today = date.today()

    for medicine in st.session_state.medicines:
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)

            if day < medicine["start_date"]:
                continue

            if is_taken(medicine["id"], day):
                status = "Taken"
            else:
                scheduled_datetime = datetime.combine(
                    day,
                    datetime.strptime(
                        medicine["time"], "%H:%M"
                    ).time()
                )

                if day < today:
                    status = "Missed"
                elif datetime.now() >= scheduled_datetime:
                    status = "Missed / Not recorded"
                else:
                    status = "Upcoming"

            writer.writerow([
                day.strftime("%d-%m-%Y"),
                medicine["name"],
                medicine["time"],
                status
            ])

    return output.getvalue()

# ---------------- TURTLE-INSPIRED DRAWING ----------------

def draw_celebration():
    """
    Draws a celebratory star using Turtle-style
    forward movement and turning logic.

    Matplotlib is used to display the drawing because
    Streamlit Cloud does not support Turtle's GUI window.
    """

    fig, ax = plt.subplots(figsize=(4, 4))

    x, y = 0, 0
    angle = -90
    points = [(x, y)]

    # Turtle-style movement
    for i in range(5):
        angle_rad = math.radians(angle)

        x += 100 * math.cos(angle_rad)
        y += 100 * math.sin(angle_rad)

        points.append((x, y))

        angle += 144

    # Close the star
    points.append(points[0])

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    ax.plot(xs, ys, linewidth=3)

    ax.set_title("A little celebration for you! ⭐")
    ax.axis("off")
    ax.set_aspect("equal")

    st.pyplot(fig)
    plt.close(fig)

# ---------------- HEADER ----------------

st.title("💊 MedTimer")
st.subheader("Your Daily Medicine Companion")

st.write(
    "A simple companion to help you organize your daily "
    "medicine schedule and keep track of your routine."
)

st.caption(
    "MedTimer is a tracking tool, not a substitute "
    "for professional medical advice."
)

st.divider()

# ---------------- DASHBOARD ----------------

scheduled, taken, remaining, today_percentage = calculate_today()

weekly_taken, weekly_total, weekly_percentage = calculate_weekly_adherence()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Today's Schedule", scheduled)
col2.metric("Recorded as Taken", taken)
col3.metric("Remaining", remaining)
col4.metric("Daily Progress", f"{today_percentage:.0f}%")

st.progress(int(today_percentage) / 100)

st.caption(f"Today's completion: {today_percentage:.1f}%")

# ---------------- WEEKLY ADHERENCE ----------------

st.header("📊 Weekly Adherence")

w1, w2, w3 = st.columns(3)

w1.metric("Doses Recorded", weekly_taken)
w2.metric("Scheduled Doses", weekly_total)
w3.metric("Weekly Adherence", f"{weekly_percentage:.1f}%")

st.progress(weekly_percentage / 100)

if weekly_total > 0:

    if weekly_percentage >= 80:
        st.success("🌟 Great consistency! Keep building your routine.")

    elif weekly_percentage >= 50:
        st.info("👏 You're making progress. Keep tracking your routine.")

    else:
        st.warning(
            "Every day is a fresh start. "
            "Use MedTimer to keep organizing your schedule."
        )

else:
    st.info("Add medicines to begin tracking your weekly progress.")

# ---------------- ADD MEDICINE ----------------

st.divider()

st.header("➕ Add Medicine")

with st.form("add_medicine_form", clear_on_submit=True):

    medicine_name = st.text_input(
        "Medicine name",
        placeholder="Enter medicine name"
    )

    medicine_time = st.time_input(
        "Scheduled time",
        value=datetime.strptime("08:00", "%H:%M").time()
    )

    submitted = st.form_submit_button(
        "Add to Schedule",
        use_container_width=True
    )

    if submitted:

        if medicine_name.strip() == "":
            st.error("Please enter a medicine name.")

        else:

            new_medicine = {
                "id": st.session_state.next_id,
                "name": medicine_name.strip(),
                "time": medicine_time.strftime("%H:%M"),
                "start_date": date.today()
            }

            st.session_state.medicines.append(new_medicine)

            st.session_state.next_id += 1

            st.success(
                f"{medicine_name} added successfully!"
            )

            st.rerun()

# ---------------- DAILY MEDICINE CHECKLIST ----------------

st.divider()

st.header("📋 Today's Medicine Checklist")

if not st.session_state.medicines:

    st.info(
        "Your schedule is empty. Add a medicine above "
        "to get started."
    )

else:

    sorted_medicines = sorted(
        st.session_state.medicines,
        key=lambda medicine: medicine["time"]
    )

    for medicine in sorted_medicines:

        status, emoji = get_status(medicine, date.today())

        with st.container(border=True):

            left, middle, right = st.columns([3, 2, 2])

            left.markdown(
                f"### 💊 {medicine['name']}"
            )

            middle.write(
                f"🕒 {medicine['time']}"
            )

            right.write(
                f"{emoji} **{status}**"
            )

            if is_taken(medicine["id"], date.today()):

                st.success("Recorded as taken today.")

                if st.button(
                    "Undo",
                    key=f"undo_{medicine['id']}"
                ):

                    unmark_taken(
                        medicine["id"],
                        date.today()
                    )

                    st.rerun()

            else:

                if st.button(
                    "Mark as Taken ✓",
                    key=f"taken_{medicine['id']}",
                    use_container_width=True
                ):

                    mark_taken(
                        medicine["id"],
                        date.today()
                    )

                    st.rerun()

# ---------------- EDIT / DELETE ----------------

st.divider()

st.header("⚙️ Manage Medicines")

if st.session_state.medicines:

    for medicine in st.session_state.medicines:

        with st.expander(
            f"Edit or Delete — {medicine['name']}"
        ):

            with st.form(
                f"edit_form_{medicine['id']}"
            ):

                updated_name = st.text_input(
                    "Medicine name",
                    value=medicine["name"],
                    key=f"name_{medicine['id']}"
                )

                updated_time = st.time_input(
                    "Scheduled time",
                    value=datetime.strptime(
                        medicine["time"], "%H:%M"
                    ).time(),
                    key=f"time_{medicine['id']}"
                )

                save_changes = st.form_submit_button(
                    "Save Changes"
                )

                if save_changes:

                    if updated_name.strip() == "":
                        st.error("Name cannot be empty.")

                    else:

                        medicine["name"] = updated_name.strip()

                        medicine["time"] = (
                            updated_time.strftime("%H:%M")
                        )

                        st.success("Medicine updated.")

                        st.rerun()

            if st.button(
                "🗑️ Delete Medicine",
                key=f"delete_{medicine['id']}"
            ):

                st.session_state.medicines = [
                    m for m in st.session_state.medicines
                    if m["id"] != medicine["id"]
                ]

                st.success("Medicine deleted.")

                st.rerun()

# ---------------- WEEKLY REPORT DOWNLOAD ----------------

st.divider()

st.header("📥 Download Weekly Report")

st.write(
    "Download a CSV report of your medicine tracking "
    "records from the last seven days."
)

report = generate_report()

st.download_button(
    label="Download My Weekly Report",
    data=report,
    file_name="MedTimer_Weekly_Report.csv",
    mime="text/csv",
    use_container_width=True
)

# ---------------- ACHIEVEMENTS ----------------

st.divider()

st.header("🏆 Achievements")

if scheduled == 0:

    st.write("Add medicines to start earning achievements.")

elif taken == 0:

    st.info("🌱 First Step — Record your first dose.")

else:

    st.success("🌱 First Step Achievement Unlocked!")

if today_percentage == 100 and scheduled > 0:

    st.success("🏆 Daily Champion — Today's checklist is complete!")

    draw_celebration()

if weekly_percentage >= 80 and weekly_total > 0:

    st.success("🌟 Consistency Star — 80% or higher weekly adherence!")

# ---------------- MOTIVATIONAL MESSAGE ----------------

st.divider()

st.header("💚 A Little Encouragement")

messages = [
    "Small steps create consistent habits.",
    "Progress matters more than perfection.",
    "Every day is a new opportunity.",
    "Taking care of yourself is important.",
    "Consistency grows one day at a time.",
    "You are doing your best. Keep going!"
]

st.info(random.choice(messages))

# ---------------- HISTORY ----------------

st.divider()

st.header("📅 Recent Tracking History")

history_rows = []

today = date.today()

for medicine in st.session_state.medicines:

    for offset in range(6, -1, -1):

        day = today - timedelta(days=offset)

        if day < medicine["start_date"]:
            continue

        if is_taken(medicine["id"], day):
            history_status = "🟢 Taken"

        elif day < today:
            history_status = "🔴 Missed"

        else:

            scheduled_datetime = datetime.combine(
                day,
                datetime.strptime(
                    medicine["time"], "%H:%M"
                ).time()
            )

            if datetime.now() >= scheduled_datetime:
                history_status = "🔴 Due / Not Recorded"
            else:
                history_status = "🟡 Upcoming"

        history_rows.append({
            "Date": day.strftime("%d %b %Y"),
            "Medicine": medicine["name"],
            "Time": medicine["time"],
            "Status": history_status
        })

if history_rows:

    history_df = pd.DataFrame(history_rows)

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.write("Your tracking history will appear here.")

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "MedTimer | Built using Python and Streamlit "
    "| CRS Artificial Intelligence Project"
)

st.caption(
    "This app is for tracking and organization only. "
    "Always follow instructions from your doctor or pharmacist."
)
