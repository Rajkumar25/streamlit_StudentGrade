import streamlit as st

# Store students
if "students" not in st.session_state:
    st.session_state.students = []


def add_student():
    name = st.session_state.input_name
    mark = st.session_state.input_mark

    if name.strip():
        # Calculate grade
        if mark >= 90:
            grade = "A"
        elif mark >= 80:
            grade = "B"
        elif mark >= 70:
            grade = "C"
        elif mark >= 60:
            grade = "D"
        else:
            grade = "F"

        # Add student
        st.session_state.students.append({
            "Name": name,
            "Mark": mark,
            "Grade": grade
        })

        # Clear the input fields
        st.session_state.input_name = ""
        st.session_state.input_mark = 0


with st.form("add"):
    st.text_input("Name", key="input_name")

    st.number_input(
        "Mark",
        min_value=0,
        max_value=100,
        value=0,
        key="input_mark"
    )

    st.form_submit_button(
        "Add",
        on_click=add_student
    )


# Display students
if st.session_state.students:
    st.table(st.session_state.students)

    average_mark = sum(
        student["Mark"]
        for student in st.session_state.students
    ) / len(st.session_state.students)

    st.metric(
        "Average Mark",
        f"{average_mark:.2f}"
    )
