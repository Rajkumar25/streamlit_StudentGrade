import streamlit as st
import pandas as pd
import numpy as np
import io

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="GradeFlow | Student Grade Manager",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 10%, rgba(99,102,241,.12), transparent 30%),
            radial-gradient(circle at 90% 20%, rgba(14,165,233,.10), transparent 30%),
            #f7f9fc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #172033 100%);
        border-right: 1px solid rgba(255,255,255,.06);
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    /* Brand */
    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 30px;
    }

    .brand-icon {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 23px;
        box-shadow: 0 8px 25px rgba(99,102,241,.3);
    }

    .brand-name {
        font-size: 20px;
        font-weight: 800;
        color: white;
    }

    .brand-subtitle {
        font-size: 11px;
        color: #9ca3af;
    }

    /* Header */
    .page-title {
        font-size: 34px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 2px;
    }

    .page-subtitle {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 25px;
    }

    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,.85);
        border: 1px solid #e8ecf3;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 8px 30px rgba(15,23,42,.05);
        min-height: 130px;
    }

    .metric-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-bottom: 12px;
    }

    .purple {
        background: #ede9fe;
    }

    .blue {
        background: #dbeafe;
    }

    .green {
        background: #dcfce7;
    }

    .orange {
        background: #ffedd5;
    }

    .metric-label {
        color: #6b7280;
        font-size: 12px;
        font-weight: 600;
    }

    .metric-value {
        color: #111827;
        font-size: 28px;
        font-weight: 800;
        margin-top: 3px;
    }

    /* Section cards */
    .section-card {
        background: rgba(255,255,255,.9);
        border: 1px solid #e8ecf3;
        border-radius: 20px;
        padding: 22px;
        margin-top: 22px;
        box-shadow: 0 8px 30px rgba(15,23,42,.04);
    }

    .section-title {
        font-size: 18px;
        font-weight: 750;
        color: #111827;
    }

    .section-description {
        font-size: 12px;
        color: #6b7280;
        margin-top: 2px;
        margin-bottom: 16px;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 11px;
        border: 1px solid #e5e7eb;
        font-weight: 600;
        min-height: 42px;
        transition: .2s ease;
    }

    div.stButton > button:hover {
        border-color: #6366f1;
        color: #4f46e5;
        transform: translateY(-1px);
    }

    /* Primary buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#6366f1,#7c3aed);
        border: none;
        color: white;
    }

    /* Inputs */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 10px;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
    }

    .pass {
        background: #dcfce7;
        color: #166534;
    }

    .fail {
        background: #fee2e2;
        color: #991b1b;
    }

    /* Hide Streamlit elements */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================
if "students" not in st.session_state:
    st.session_state.students = []

if "subjects" not in st.session_state:
    st.session_state.subjects = [
        "Mathematics",
        "Science",
        "English",
        "Computer Science",
        "Social Studies"
    ]


# =========================================================
# GRADE CALCULATION
# =========================================================
def calculate_grade(percentage):
    if percentage >= 90:
        return "A+", 4.0
    elif percentage >= 80:
        return "A", 3.7
    elif percentage >= 70:
        return "B+", 3.3
    elif percentage >= 60:
        return "B", 3.0
    elif percentage >= 50:
        return "C", 2.0
    elif percentage >= 40:
        return "D", 1.0
    else:
        return "F", 0.0


def calculate_student_result(marks):
    total = sum(marks.values())
    max_marks = len(marks) * 100

    percentage = (total / max_marks) * 100
    grade, gpa = calculate_grade(percentage)

    passed = all(mark >= 40 for mark in marks.values())

    if not passed:
        grade = "F"
        gpa = 0.0

    return total, percentage, grade, gpa, passed


# =========================================================
# DATAFRAME
# =========================================================
def students_dataframe():

    rows = []

    for student in st.session_state.students:

        row = {
            "ID": student["id"],
            "Student": student["name"],
            "Class": student["class"],
            "Total": student["total"],
            "Percentage": round(student["percentage"], 2),
            "Grade": student["grade"],
            "GPA": student["gpa"],
            "Status": "Pass" if student["passed"] else "Fail",
        }

        rows.append(row)

    return pd.DataFrame(rows)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.markdown("""
    <div class="brand">
        <div class="brand-icon">🎓</div>
        <div>
            <div class="brand-name">GradeFlow</div>
            <div class="brand-subtitle">Student Grade Manager</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Navigation")

    page = st.radio(
        "Navigate",
        [
            "📊 Dashboard",
            "➕ Add Student",
            "👥 Students",
            "📈 Analytics",
            "⚙️ Settings",
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.caption("Academic Year")

    academic_year = st.selectbox(
        "Year",
        ["2026–27", "2025–26", "2024–25"],
        label_visibility="collapsed"
    )

    st.divider()

    st.caption("GradeFlow v1.0")
    st.caption("Simple academic performance management.")


# =========================================================
# DASHBOARD
# =========================================================
if page == "📊 Dashboard":

    st.markdown(
        '<div class="page-title">Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Monitor student performance and academic progress at a glance.'
        '</div>',
        unsafe_allow_html=True
    )

    df = students_dataframe()

    total_students = len(df)

    if total_students > 0:
        average_percentage = df["Percentage"].mean()
        passed_students = (df["Status"] == "Pass").sum()
        pass_rate = (passed_students / total_students) * 100
        average_gpa = df["GPA"].mean()
    else:
        average_percentage = 0
        passed_students = 0
        pass_rate = 0
        average_gpa = 0

    # Metrics
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon purple">👥</div>
            <div class="metric-label">TOTAL STUDENTS</div>
            <div class="metric-value">{total_students}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon blue">📊</div>
            <div class="metric-label">AVERAGE SCORE</div>
            <div class="metric-value">{average_percentage:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon green">✓</div>
            <div class="metric-label">PASS RATE</div>
            <div class="metric-value">{pass_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon orange">⭐</div>
            <div class="metric-label">AVERAGE GPA</div>
            <div class="metric-value">{average_gpa:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Main content
    if total_students == 0:

        st.markdown("""
        <div class="section-card">
            <div style="text-align:center;padding:45px 20px;">
                <div style="font-size:50px;">🎓</div>
                <div style="
                    font-size:20px;
                    font-weight:750;
                    color:#111827;
                    margin-top:10px;
                ">
                    No students yet
                </div>
                <div style="
                    color:#6b7280;
                    font-size:13px;
                    margin-top:6px;
                ">
                    Add your first student to start managing grades.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:

        left, right = st.columns([1.4, 1])

        with left:

            st.markdown("""
            <div class="section-card">
                <div class="section-title">Recent Students</div>
                <div class="section-description">
                    Latest student performance records
                </div>
            """, unsafe_allow_html=True)

            recent_df = df.head(8).copy()

            st.dataframe(
                recent_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Percentage": st.column_config.NumberColumn(
                        "Score",
                        format="%.1f%%"
                    ),
                    "GPA": st.column_config.NumberColumn(
                        "GPA",
                        format="%.2f"
                    ),
                }
            )

            st.markdown("</div>", unsafe_allow_html=True)

        with right:

            st.markdown("""
            <div class="section-card">
                <div class="section-title">Grade Distribution</div>
                <div class="section-description">
                    Students by grade
                </div>
            """, unsafe_allow_html=True)

            grade_counts = df["Grade"].value_counts()

            st.bar_chart(grade_counts)

            st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# ADD STUDENT
# =========================================================
elif page == "➕ Add Student":

    st.markdown(
        '<div class="page-title">Add Student</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Enter student information and subject marks.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="section-card">
        <div class="section-title">Student Information</div>
        <div class="section-description">
            Basic student details
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        student_id = st.text_input(
            "Student ID",
            placeholder="e.g. STU001"
        )

    with c2:
        student_name = st.text_input(
            "Full Name",
            placeholder="e.g. John Smith"
        )

    with c3:
        student_class = st.selectbox(
            "Class",
            [
                "Grade 6",
                "Grade 7",
                "Grade 8",
                "Grade 9",
                "Grade 10",
                "Grade 11",
                "Grade 12",
            ]
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-card">
        <div class="section-title">Subject Marks</div>
        <div class="section-description">
            Enter marks between 0 and 100
        </div>
    """, unsafe_allow_html=True)

    marks = {}

    columns = st.columns(3)

    for i, subject in enumerate(st.session_state.subjects):

        with columns[i % 3]:

            marks[subject] = st.number_input(
                subject,
                min_value=0,
                max_value=100,
                value=0,
                step=1,
                key=f"mark_{subject}"
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # Preview
    total, percentage, grade, gpa, passed = calculate_student_result(marks)

    st.markdown("""
    <div class="section-card">
        <div class="section-title">Result Preview</div>
        <div class="section-description">
            Automatically calculated performance
        </div>
    """, unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.metric("Total", f"{total}/{len(marks) * 100}")

    with p2:
        st.metric("Percentage", f"{percentage:.1f}%")

    with p3:
        st.metric("Grade", grade)

    with p4:
        st.metric("GPA", f"{gpa:.2f}")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(
        "➕ Add Student",
        type="primary",
        use_container_width=True
    ):

        if not student_id.strip():
            st.error("Please enter a Student ID.")

        elif not student_name.strip():
            st.error("Please enter the student's name.")

        elif any(
            s["id"].lower() == student_id.lower()
            for s in st.session_state.students
        ):
            st.error("Student ID already exists.")

        else:

            student = {
                "id": student_id.strip(),
                "name": student_name.strip(),
                "class": student_class,
                "marks": marks,
                "total": total,
                "percentage": percentage,
                "grade": grade,
                "gpa": gpa,
                "passed": passed,
            }

            st.session_state.students.append(student)

            st.success(
                f"Student {student_name} was added successfully!"
            )

            st.balloons()


# =========================================================
# STUDENTS
# =========================================================
elif page == "👥 Students":

    st.markdown(
        '<div class="page-title">Students</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Search, filter and manage student records.'
        '</div>',
        unsafe_allow_html=True
    )

    df = students_dataframe()

    if df.empty:

        st.info("No students have been added yet.")

    else:

        c1, c2, c3 = st.columns([2, 1, 1])

        with c1:
            search = st.text_input(
                "🔎 Search",
                placeholder="Search by name or student ID..."
            )

        with c2:
            grade_filter = st.selectbox(
                "Grade",
                ["All"] + sorted(df["Grade"].unique().tolist())
            )

        with c3:
            status_filter = st.selectbox(
                "Status",
                ["All", "Pass", "Fail"]
            )

        filtered = df.copy()

        if search:
            filtered = filtered[
                filtered["Student"].str.contains(
                    search,
                    case=False,
                    na=False
                )
                |
                filtered["ID"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if grade_filter != "All":
            filtered = filtered[
                filtered["Grade"] == grade_filter
            ]

        if status_filter != "All":
            filtered = filtered[
                filtered["Status"] == status_filter
            ]

        st.markdown("""
        <div class="section-card">
        """, unsafe_allow_html=True)

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Percentage": st.column_config.ProgressColumn(
                    "Percentage",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%"
                ),
                "GPA": st.column_config.NumberColumn(
                    "GPA",
                    format="%.2f"
                ),
            }
        )

        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            "⬇️ Export Students as CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="students.csv",
            mime="text/csv",
            use_container_width=True
        )


# =========================================================
# ANALYTICS
# =========================================================
elif page == "📈 Analytics":

    st.markdown(
        '<div class="page-title">Analytics</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Understand academic performance across your class.'
        '</div>',
        unsafe_allow_html=True
    )

    df = students_dataframe()

    if df.empty:

        st.info("Add students to see analytics.")

    else:

        c1, c2 = st.columns(2)

        with c1:

            st.markdown("""
            <div class="section-card">
                <div class="section-title">Score Distribution</div>
                <div class="section-description">
                    Percentage distribution
                </div>
            """, unsafe_allow_html=True)

            histogram = pd.DataFrame({
                "Score": df["Percentage"]
            })

            st.bar_chart(
                histogram["Score"].value_counts().sort_index()
            )

            st.markdown("</div>", unsafe_allow_html=True)

        with c2:

            st.markdown("""
            <div class="section-card">
                <div class="section-title">Grade Distribution</div>
                <div class="section-description">
                    Number of students per grade
                </div>
            """, unsafe_allow_html=True)

            grade_distribution = (
                df["Grade"]
                .value_counts()
                .sort_index()
            )

            st.bar_chart(grade_distribution)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="section-card">
            <div class="section-title">Performance Summary</div>
            <div class="section-description">
                Key academic statistics
            </div>
        """, unsafe_allow_html=True)

        summary = pd.DataFrame({
            "Metric": [
                "Highest Score",
                "Lowest Score",
                "Average Score",
                "Highest GPA",
                "Average GPA",
                "Students Passed",
            ],
            "Value": [
                f"{df['Percentage'].max():.1f}%",
                f"{df['Percentage'].min():.1f}%",
                f"{df['Percentage'].mean():.1f}%",
                f"{df['GPA'].max():.2f}",
                f"{df['GPA'].mean():.2f}",
                str((df["Status"] == "Pass").sum()),
            ]
        })

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SETTINGS
# =========================================================
elif page == "⚙️ Settings":

    st.markdown(
        '<div class="page-title">Settings</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Customize subjects and application preferences.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="section-card">
        <div class="section-title">Subjects</div>
        <div class="section-description">
            Manage the subjects used when entering marks.
        </div>
    """, unsafe_allow_html=True)

    subjects_text = st.text_area(
        "Subjects",
        value=", ".join(st.session_state.subjects),
        help="Separate subjects using commas."
    )

    if st.button(
        "💾 Save Subjects",
        type="primary"
    ):

        new_subjects = [
            subject.strip()
            for subject in subjects_text.split(",")
            if subject.strip()
        ]

        if new_subjects:
            st.session_state.subjects = new_subjects
            st.success("Subjects updated successfully.")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-card">
        <div class="section-title">Danger Zone</div>
        <div class="section-description">
            These actions cannot be undone.
        </div>
    """, unsafe_allow_html=True)

    if st.button(
        "🗑️ Delete All Student Records",
        type="secondary"
    ):
        st.session_state.students = []
        st.success("All student records have been deleted.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div style="
    text-align:center;
    color:#9ca3af;
    font-size:11px;
    margin-top:40px;
    padding:20px;
">
    🎓 GradeFlow • Student Grade Manager
    <br>
    Built with Streamlit
</div>
""", unsafe_allow_html=True)
