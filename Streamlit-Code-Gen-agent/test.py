import streamlit as st
import pandas as pd
import datetime

# Initialize attendance data
if 'attendance' not in st.session_state:
    st.session_state.attendance = pd.DataFrame(columns=['Name', 'Date'])

# Page configuration
st.set_page_config(
    page_title="Attendance Management System",
    page_icon="🚀",
    layout="wide"
)

# Main title
st.title("Attendance Management System")
st.markdown("---")

# Description
st.markdown("""
A simple attendance management system
""")

# Main content area
def main():
    with st.form("attendance_form"):
        student_name = st.text_input("Student Name", placeholder="Enter name")
        attendance_date = st.date_input("Date", value=datetime.date.today())
        submitted = st.form_submit_button("Record Attendance")

        if submitted:
            new_record = pd.DataFrame([{'Name': student_name, 'Date': attendance_date}])
            st.session_state.attendance = pd.concat([st.session_state.attendance, new_record], ignore_index=True)
            st.success(f"Attendance recorded for {student_name} on {attendance_date}")

    if not st.session_state.attendance.empty:
        st.header("Attendance Records")
        st.dataframe(st.session_state.attendance, use_container_width=True)
    else:
        st.info("No attendance records yet.")


if __name__ == "__main__":
    main()
