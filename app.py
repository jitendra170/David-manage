import os

import streamlit as st


def load_env_value(key: str) -> str:
    aliases = {
        "SUPABASE_URL": ["SUPABASE_URL", "supabase_url"],
        "SUPABASE_KEY": [
            "SUPABASE_KEY",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "supabase_key",
            "sb_key",
            "SB_KEY",
        ],
    }

    for candidate in aliases.get(key, [key, key.lower()]):
        value = os.getenv(candidate)
        if value:
            return value.strip()

    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_file):
        return ""

    try:
        with open(env_file, encoding="utf-8") as env_file_handle:
            env_values = {}
            for line in env_file_handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                env_key, env_val = stripped.split("=", 1)
                env_values[env_key.strip()] = env_val.strip().strip('"').strip("'")

            normalized_env_values = {k.lower(): v for k, v in env_values.items()}
            for candidate in aliases.get(key, [key, key.lower()]):
                if candidate in env_values:
                    return env_values[candidate]
                if candidate.lower() in normalized_env_values:
                    return normalized_env_values[candidate.lower()]
    except Exception:
        return ""

    return ""


st.set_option("client.showSidebarNavigation", False)

st.set_page_config(page_title="School Management System", page_icon="🏫", layout="wide")

SUPABASE_URL = load_env_value("SUPABASE_URL")
SUPABASE_KEY = load_env_value("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        SUPABASE_URL = str(st.secrets.get("SUPABASE_URL", "")).strip()
        SUPABASE_KEY = str(st.secrets.get("SUPABASE_KEY", "") or st.secrets.get("SUPABASE_ANON_KEY", "") or st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", "")).strip()
    except Exception:
        SUPABASE_URL = SUPABASE_URL or ""
        SUPABASE_KEY = SUPABASE_KEY or ""

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
BANNER_IMAGE_PATH = os.path.join(ASSETS_DIR, "school_banner.svg")

ROLE_TASKS = {
    "teacher": ["Upload lesson plans", "Manage class attendance", "View student performance"],
    "principal": ["Review school reports", "Approve announcements", "Monitor staff activities"],
    "accountant": ["Manage fees", "Track expenses", "Generate payroll summaries"],
    "student": ["View timetable", "Submit assignments", "Check attendance"],
    "library": ["Manage book inventory", "Issue books", "Track returns"],
}

LOCAL_USERS = {}
LOCAL_RECORDS = {
    "students": [],
    "teachers": [],
    "fees": [],
    "attendance": [],
    "student_attendance": [],
    "teacher_attendance": [],
}

SCHOOL_DETAILS = {
    "name": "Bright Future Academy",
    "address": "Graphic Build, Kathmandu",
    "phone": "9805626037",
    "principal": "Dharmendra Yadav",
    "students": 1240,
    "staff": 86,
    "classes": 24,
    "attendance": 94,
    "fees_collected": 8750000,
    "pending_issues": 6,
}


def get_available_roles():
    return list(ROLE_TASKS.keys())


def get_role_tasks(role: str):
    return ROLE_TASKS.get(role, [])


def get_school_details():
    return SCHOOL_DETAILS


def get_dashboard_metrics(role: str):
    # Compute metrics from local in-memory records where possible so
    # newly added students/teachers/fees/attendance show up on the dashboard.
    role = (role or "").lower().strip()
    school = get_school_details()

    students_count = len(LOCAL_RECORDS.get("students", []))
    staff_count = len(LOCAL_RECORDS.get("teachers", []))

    # Compute average attendance from class-level attendance records if available
    attendance_value = None
    attendance_records = LOCAL_RECORDS.get("attendance", [])
    try:
        vals = []
        for r in attendance_records:
            v = r.get("attendance")
            if v is None:
                continue
            try:
                vals.append(float(str(v)))
            except Exception:
                continue
        if vals:
            attendance_value = round(sum(vals) / len(vals), 1)
    except Exception:
        attendance_value = None

    if attendance_value is None:
        attendance_value = school.get("attendance", 0)

    # Sum numeric fees when possible
    fees_total = 0.0
    for fr in LOCAL_RECORDS.get("fees", []):
        f = fr.get("fee")
        if f is None:
            continue
        try:
            fees_total += float(str(f).replace(",", "").replace("NPR", "").strip())
        except Exception:
            continue

    base = {
        "attendance": attendance_value,
        "students": students_count,
        "staff": staff_count,
        "pending_issues": school.get("pending_issues", 0),
        "fees_collected": int(fees_total) if fees_total.is_integer() else fees_total,
        "classes": school.get("classes", 0),
    }

    # Keep role-aware shape but return computed values (calling code expects some keys)
    return base


def get_dashboard_sections(role: str):
    role = (role or "").lower().strip()
    sections = [
        "Students",
        "Teachers",
        "Fees",
        "Attendance",
        "Teacher Attendance",
        "Student Attendance",
        "Reviews",
    ]
    return sections


def render_premium_sidebar():
    # Inject premium CSS for a modern, realistic look
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg,#071029,#08122a);
            color: #e6f0ff;
            padding: 18px;
            border-radius: 12px;
            box-shadow: 0 12px 40px rgba(3,7,18,0.6);
            font-family: 'Inter', system-ui, sans-serif;
        }
        [data-testid="stSidebar"] h3 { color: #fff; margin: 0 0 8px 0; }
        [data-testid="stSidebar"] .premium-topbar { padding: 10px 12px; border-radius: 10px; background: linear-gradient(90deg,#0ea5a4,#7c3aed); box-shadow: 0 8px 24px rgba(124,58,237,0.12); }
        [data-testid="stSidebar"] .stButton>button {
            background: linear-gradient(90deg,#0ea5a4,#06b6d4);
            color: white;
            border-radius: 10px;
            padding: 10px 12px;
            width: 100%;
            border: none;
            margin: 6px 0;
            font-weight: 600;
            box-shadow: 0 8px 24px rgba(2,6,23,0.45);
        }
        [data-testid="stSidebar"] .stButton>button:focus { outline: none; }
        [data-testid="stSidebar"] .section-title { color: #cfe9ff; font-weight:600; margin-top:8px; }
        .premium-topbar .sub { font-size:12px; opacity:0.9 }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<div class="premium-topbar"><h3>🏫 Premium Control</h3><div class="sub">Bright Future Academy</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🏠 Dashboard"):
            st.session_state["active_page"] = "Dashboard"
        if st.button("➕ Add Student"):
            st.session_state["active_page"] = "Add Student"
        if st.button("👩‍🏫 Teachers"):
            st.session_state["active_page"] = "Teachers"
        if st.button("💰 Fees"):
            st.session_state["active_page"] = "Fees"
        if st.button("📋 Attendance"):
            st.session_state["active_page"] = "Attendance"
        if st.button("🧑‍🏫 Teacher Attendance"):
            st.session_state["active_page"] = "Teacher Attendance"
        if st.button("🎒 Student Attendance"):
            st.session_state["active_page"] = "Student Attendance"
        if st.button("⭐ Review"):
            st.session_state["active_page"] = "Review"
        st.divider()
        if st.button("🔓 Logout"):
            st.session_state.pop("user", None)
            st.session_state.pop("active_page", None)
            st.rerun()


def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        from supabase import create_client

        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None


def _format_supabase_error(err) -> str:
    try:
        # If it's already a dict-like error from the client
        if isinstance(err, dict):
            # try common keys
            msg = err.get("message") or err.get("msg") or str(err)
            details = err.get("details")
            if details:
                # details can be a bytes-like repr from some clients
                try:
                    if isinstance(details, (bytes, bytearray)):
                        details = details.decode("utf-8", errors="ignore")
                except Exception:
                    pass
                return f"{msg} — details: {details}"
            return msg

        # If it's bytes wrapped in a string like: b'{"message":"..."}'
        s = str(err)
        if "Invalid API key" in s:
            return "Invalid API key. Double-check your SUPABASE_KEY (anon or service_role)."

        # Try to extract JSON-like content
        if "{" in s and "}" in s:
            # attempt to locate a JSON substring
            start = s.find("{")
            end = s.rfind("}") + 1
            json_part = s[start:end]
            try:
                import json

                parsed = json.loads(json_part)
                return parsed.get("message") or parsed.get("error") or s
            except Exception:
                pass

        return s
    except Exception:
        return str(err)


def is_supabase_configured():
    return bool(SUPABASE_URL and SUPABASE_KEY)


def get_supabase_status():
    if not is_supabase_configured():
        return False, "Supabase credentials are not configured."

    client = get_supabase_client()
    if not client:
        return False, "Supabase client initialization failed."

    try:
        response = client.table("app_users").select("email").limit(1).execute()
        response_error = getattr(response, "error", None)
        if response_error:
            message = _format_supabase_error(response_error)
            return False, f"Supabase error: {message}"
        return True, "Supabase is configured and reachable."
    except Exception as exc:
        return False, f"Supabase connection failed: {_format_supabase_error(exc)}"


def run_supabase_live_test():
    if not is_supabase_configured():
        return False, "Supabase credentials are not configured."

    client = get_supabase_client()
    if not client:
        return False, "Supabase client initialization failed."

    try:
        unique_email = f"live-test-{os.urandom(4).hex()}@example.com"
        payload = {"full_name": "Live Test", "email": unique_email, "password_hash": "live-test", "role": "student"}
        insert_response = client.table("app_users").insert(payload).execute()
        insert_error = getattr(insert_response, "error", None)
        if insert_error:
            return False, f"Supabase insert failed: {_format_supabase_error(insert_error)}"

        select_response = client.table("app_users").select("email").eq("email", unique_email).maybe_single().execute()
        select_error = getattr(select_response, "error", None)
        if select_error:
            return False, f"Supabase select failed: {_format_supabase_error(select_error)}"

        delete_response = client.table("app_users").delete().eq("email", unique_email).execute()
        delete_error = getattr(delete_response, "error", None)
        if delete_error:
            return False, f"Supabase delete failed: {_format_supabase_error(delete_error)}"

        return True, "Supabase live insert/select/delete test succeeded."
    except Exception as exc:
        return False, f"Supabase live test failed: {_format_supabase_error(exc)}"


def add_school_record(record_type: str, data: dict):
    if record_type not in LOCAL_RECORDS:
        return False

    client = get_supabase_client()
    # If Supabase is available, try to insert the record there first.
    if client:
        try:
            response = client.table(record_type).insert(data).execute()
            resp_data = getattr(response, "data", None)
            resp_error = getattr(response, "error", None)
            if resp_error:
                # On error, fall back to local store for UI responsiveness
                LOCAL_RECORDS[record_type].append(data)
                return False

            # If Supabase returned the created record(s), keep local cache in sync
            if isinstance(resp_data, list):
                LOCAL_RECORDS[record_type].extend(resp_data)
            elif isinstance(resp_data, dict):
                LOCAL_RECORDS[record_type].append(resp_data)
            else:
                LOCAL_RECORDS[record_type].append(data)
            return True
        except Exception:
            # On any exception, append locally so the UI still shows the record
            LOCAL_RECORDS[record_type].append(data)
            return False

    # No Supabase client: store locally only
    LOCAL_RECORDS[record_type].append(data)
    return False


def get_school_records(record_type: str):
    # If Supabase is configured, prefer fetching live records from the DB
    if record_type not in LOCAL_RECORDS:
        return []

    client = get_supabase_client()
    if client:
        try:
            response = client.table(record_type).select("*").execute()
            rows = getattr(response, "data", None)
            if isinstance(rows, list):
                # update local cache with the latest rows
                LOCAL_RECORDS[record_type] = rows
                return rows
        except Exception:
            # Fall back to local cache on any error
            pass

    return LOCAL_RECORDS.get(record_type, [])


def get_user_title(role: str):
    return {
        "teacher": "Teacher Dashboard",
        "principal": "Principal Dashboard",
        "accountant": "Accountant Dashboard",
        "student": "Student Dashboard",
        "library": "Library Dashboard",
    }.get((role or "").lower().strip(), "School Dashboard")


def normalize_email(email: str):
    return (email or "").strip().lower()


def normalize_password(password: str):
    return (password or "").strip()


def authenticate_user(email: str, password: str):
    if not email or not password:
        return None

    normalized_email = normalize_email(email)
    password_value = normalize_password(password)

    local_record = LOCAL_USERS.get(normalized_email)
    if isinstance(local_record, dict) and password_value == str(local_record.get("password_hash", "")).strip():
        role = str(local_record.get("role", "student")).lower().strip()
        return {"email": normalized_email, "role": role, "title": get_user_title(role)}

    client = get_supabase_client()
    if client:
        try:
            response = client.table("app_users").select("email, role, password_hash").eq("email", normalized_email).maybe_single().execute()
            record = getattr(response, "data", None)
            if isinstance(record, dict) and password_value == str(record.get("password_hash", "")).strip():
                role_value = record.get("role")
                if isinstance(role_value, str):
                    role = role_value.lower().strip()
                    return {"email": normalized_email, "role": role, "title": get_user_title(role)}
        except Exception:
            pass

    demo_users = {
        "teacher@example.com": ("teacher", "Teacher Dashboard", "password123"),
        "principal@example.com": ("principal", "Principal Dashboard", "password123"),
        "accountant@example.com": ("accountant", "Accountant Dashboard", "password123"),
        "student@example.com": ("student", "Student Dashboard", "password123"),
        "library@example.com": ("library", "Library Dashboard", "password123"),
        "teacher@school.com": ("teacher", "Teacher Dashboard", "teacher123"),
        "principal@school.com": ("principal", "Principal Dashboard", "principal123"),
        "accountant@school.com": ("accountant", "Accountant Dashboard", "accountant123"),
        "student@school.com": ("student", "Student Dashboard", "student123"),
        "library@school.com": ("library", "Library Dashboard", "library123"),
    }

    if normalized_email in demo_users and password_value == demo_users[normalized_email][2]:
        role, title, _ = demo_users[normalized_email]
        return {"email": normalized_email, "role": role, "title": title}
    return None


def register_user(full_name: str, email: str, password: str, role: str):
    if not full_name or not email or not password or not role:
        return False

    role = role.lower().strip()
    if role not in get_available_roles():
        return False

    normalized_email = normalize_email(email)
    normalized_full_name = full_name.strip()
    password_value = normalize_password(password)

    client = get_supabase_client()
    if client:
        try:
            response = client.table("app_users").insert(
                {
                    "full_name": normalized_full_name,
                    "email": normalized_email,
                    "password_hash": password_value,
                    "role": role,
                }
            ).execute()
            data = getattr(response, "data", None)
            error = getattr(response, "error", None)
            if data is not None and not error:
                return True
        except Exception:
            pass

    LOCAL_USERS[normalized_email] = {
        "full_name": normalized_full_name,
        "email": normalized_email,
        "password_hash": password_value,
        "role": role,
    }
    return True


def render_register():
    st.title("Register for Shree Janta Secondary School")
    st.subheader("Create a new account for teachers, principals, accountants, students, or library staff")

    with st.form("register_form"):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", get_available_roles())
        submitted = st.form_submit_button("Register")

    if submitted:
        if not full_name or not email or not password or not confirm_password:
            st.error("Please fill out all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif register_user(full_name, email, password, role):
            st.success("Registration successful. You can now log in.")
            st.info("Use the login tab to sign in with your new account.")
        else:
            st.error("Registration failed. Please check your details and try again.")


def render_login():
    if os.path.exists(BANNER_IMAGE_PATH):
        st.image(BANNER_IMAGE_PATH, width=900)
    st.title("Shree Janta Secondary School")
    st.subheader("Smart school management for teachers, principals, accountants, students, and library staff")

    action = st.radio("Choose an action", ["Login", "Register"], horizontal=True)

    if is_supabase_configured():
        success, message = get_supabase_status()
        if success:
            st.success(message)
        else:
            st.warning(message)
    else:
        st.warning("Supabase is not configured. Records will be saved locally only.")

    if action == "Login":
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        if submitted:
            user = authenticate_user(email, password)
            if user:
                st.session_state["user"] = user
                st.success(f"Welcome back, {user['title']}")
                st.rerun()
            else:
                st.error("Invalid credentials. Try the demo accounts below.")

        st.caption("Demo accounts: teacher@example.com, principal@example.com, accountant@example.com, student@example.com, library@example.com")
        st.caption("Supabase seeded passwords: principal123, teacher123, accountant123, student123, library123")
        st.caption("Fallback demo password (for example accounts): password123")
    else:
        render_register()


def render_dashboard(user):
    if os.path.exists(BANNER_IMAGE_PATH):
        st.image(BANNER_IMAGE_PATH, width=900)
    st.title(f"{user['title']}")
    st.caption(f"Signed in as {user['email']} • Role: {user['role']}")

    if is_supabase_configured():
        success, message = get_supabase_status()
        if success:
            st.success(message)
        else:
            st.warning(message)
    else:
        st.warning("Supabase is not configured. Records will be saved locally only.")

    if st.button("🧪 Test Supabase connection"):
        with st.spinner("Running Supabase live test..."):
            success, message = run_supabase_live_test()
        if success:
            st.success(message)
        else:
            st.error(message)

    school = get_school_details()
    metrics = get_dashboard_metrics(user["role"])

    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "Dashboard"

    # Render a premium-styled sidebar navigation
    render_premium_sidebar()

    page = st.session_state.get("active_page", "Dashboard")

    if page == "Dashboard":
        st.markdown("## Premium School Control Center")
    st.info(f"{school['name']} is running smoothly with {school['students']} students, {school['staff']} staff members, and {school['attendance']}% attendance.")

    dashboard_sections = get_dashboard_sections(user["role"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Students", f"{metrics['students']}")
    col2.metric("Staff", f"{metrics['staff']}")
    col3.metric("Attendance", f"{metrics['attendance']}%")
    col4.metric("Pending Issues", f"{metrics['pending_issues']}")

    if user["role"] == "principal":
        col5, col6 = st.columns(2)
        col5.metric("Classes", f"{metrics['classes']}")
        col6.metric("Fees Collected", f"NPR {metrics['fees_collected']:,}")
        # Show recent student admissions for principal
        recent_students = get_school_records("students")
        if recent_students:
            st.subheader("Recent Admissions")
            for s in recent_students[-5:][::-1]:
                name = s.get("name") or "Unnamed"
                grade = s.get("grade") or "-"
                adm = s.get("admission_date") or "-"
                roll = s.get("roll_number") or "-"
                avg = s.get("avg_grade")
                avg_text = f" • Avg: {avg}" if isinstance(avg, (int, float)) else ""
                st.write(f"- {name} • Grade: {grade} • Admission: {adm} • Roll: {roll}{avg_text}")
        else:
            st.info("No recent admissions to show.")

    st.subheader("School Details")
    school_col1, school_col2 = st.columns([1, 2])
    with school_col1:
        if os.path.exists(BANNER_IMAGE_PATH):
            st.image(BANNER_IMAGE_PATH, width=320)
    with school_col2:
        st.write(f"**School:** {school['name']}")
        st.write(f"**Address:** {school['address']}")
        st.write(f"**Phone:** {school['phone']}")
        st.write(f"**Principal:** {school['principal']}")

    if page == "Dashboard":
        st.subheader("Operations Suite")
        tabs = st.tabs(dashboard_sections)

        for section_name, tab in zip(dashboard_sections, tabs):
            with tab:
                if section_name == "Students":
                    st.success("Student records, admission tracking, and academic progress overview")
                    student_rows = get_school_records("students")

                    # Academic progress summary
                    avg_grades = [row.get("avg_grade") for row in student_rows if isinstance(row.get("avg_grade"), (int, float))]
                    overall_avg = round(sum(avg_grades) / len(avg_grades), 1) if avg_grades else None
                    at_risk = sum(1 for g in avg_grades if g < 50) if avg_grades else 0
                    st.markdown(f"**Total students:** {len(student_rows)}")
                    if overall_avg is not None:
                        st.markdown(f"**Average grade (students with grades):** {overall_avg}")
                    st.markdown(f"**Students at risk (avg < 50):** {at_risk}")

                    st.dataframe({
                        "Name": [row.get("name") for row in student_rows],
                        "Grade": [row.get("grade") for row in student_rows],
                        "Status": [row.get("status") for row in student_rows],
                        "Admission Date": [row.get("admission_date") for row in student_rows],
                        "Roll Number": [row.get("roll_number") for row in student_rows],
                        "Avg Grade": [row.get("avg_grade") for row in student_rows],
                    })
                elif section_name == "Teachers":
                    st.success("Teacher assignments, subjects, and performance dashboard")
                    teacher_rows = get_school_records("teachers")
                    st.dataframe({"Name": [row["name"] for row in teacher_rows], "Subject": [row["subject"] for row in teacher_rows], "Status": [row["status"] for row in teacher_rows]})
                elif section_name == "Fees":
                    st.success("Fee collection, dues, and reminders in one place")
                    fee_rows = get_school_records("fees")
                    st.dataframe({"Student": [row["student"] for row in fee_rows], "Fee": [row["fee"] for row in fee_rows], "Status": [row["status"] for row in fee_rows]})
                elif section_name == "Attendance":
                    st.success("Attendance monitoring for all grades and classes")
                    attendance_rows = get_school_records("attendance")
                    st.dataframe({"Class": [row["class_name"] for row in attendance_rows], "Present": [row["present"] for row in attendance_rows], "Attendance": [row["attendance"] for row in attendance_rows]})
                elif section_name == "Teacher Attendance":
                    st.success("Track teacher attendance and duty status")
                    teacher_attendance = get_school_records("teacher_attendance")
                    st.dataframe({"Teacher": [row["teacher"] for row in teacher_attendance], "Date": [row["date"] for row in teacher_attendance], "Status": [row["status"] for row in teacher_attendance]})
                elif section_name == "Student Attendance":
                    st.success("Track student attendance across classes")
                    student_attendance = get_school_records("student_attendance")
                    st.dataframe({"Student": [row["student"] for row in student_attendance], "Class": [row["class_name"] for row in student_attendance], "Status": [row["status"] for row in student_attendance]})
                elif section_name == "Reviews":
                    st.success("Premium review board for academic and admin performance")
                    st.write("- Principal review: Strong weekly execution")
                    st.write("- Teacher review: Good lesson completion")
                    st.write("- Finance review: Fee recovery on track")

    elif page == "Add Student":
        st.subheader("Add New Student")
        with st.form("student_form"):
            student_name = st.text_input("Student Name")
            student_grade = st.text_input("Grade (single value)")
            student_status = st.text_input("Status")
            admission_date = st.text_input("Admission Date (YYYY-MM-DD)")
            roll_number = st.text_input("Roll Number")
            grades_input = st.text_input("Grades (comma-separated, e.g. 85,90,78)")
            if st.form_submit_button("Add Student"):
                # parse grades input into list of floats where possible
                grades = []
                if grades_input:
                    for part in grades_input.split(","):
                        try:
                            grades.append(float(part.strip()))
                        except Exception:
                            continue

                avg_grade = None
                if grades:
                    try:
                        avg_grade = round(sum(grades) / len(grades), 1)
                    except Exception:
                        avg_grade = None

                student_record = {
                    "name": student_name,
                    "grade": student_grade,
                    "status": student_status,
                    "admission_date": admission_date,
                    "roll_number": roll_number,
                    "grades": grades,
                    "avg_grade": avg_grade,
                }
                saved = add_school_record("students", student_record)
                if saved:
                    st.success("Student saved to Supabase.")
                else:
                    st.warning("Student saved locally only. Supabase was unavailable or insert failed.")

        st.markdown("---")
        st.subheader("Bulk add students")
        with st.form("bulk_student_form"):
            bulk_students = st.text_area("Paste students (one per line): name,grade,status,admission_date,roll,grades(comma-separated)")
            if st.form_submit_button("Add Students"):
                added = 0
                for line in bulk_students.splitlines():
                    parts = [p.strip() for p in line.split(",")]
                    if not parts or len(parts) < 3:
                        continue
                    name = parts[0]
                    grade = parts[1] if len(parts) > 1 else ""
                    status = parts[2] if len(parts) > 2 else ""
                    admission = parts[3] if len(parts) > 3 else ""
                    roll = parts[4] if len(parts) > 4 else ""
                    grades_list = []
                    if len(parts) > 5:
                        for g in parts[5].split(";") if ";" in parts[5] else parts[5].split("|"):
                            try:
                                grades_list.append(float(g.strip()))
                            except Exception:
                                continue

                    avg_grade = round(sum(grades_list) / len(grades_list), 1) if grades_list else None
                    saved = add_school_record("students", {"name": name, "grade": grade, "status": status, "admission_date": admission, "roll_number": roll, "grades": grades_list, "avg_grade": avg_grade})
                    if saved:
                        added += 1
                st.success(f"Added {added} students")

    elif page == "Teachers":
        st.subheader("Teacher Management")
        with st.form("teacher_form"):
            teacher_name = st.text_input("Teacher Name", key="teacher_name")
            teacher_subject = st.text_input("Subject", key="teacher_subject")
            teacher_status = st.text_input("Status", key="teacher_status")
            if st.form_submit_button("Add Teacher"):
                saved = add_school_record("teachers", {"name": teacher_name, "subject": teacher_subject, "status": teacher_status})
                if saved:
                    st.success("Teacher saved to Supabase.")
                else:
                    st.warning("Teacher saved locally only. Supabase was unavailable or insert failed.")
        st.markdown("---")
        st.subheader("Bulk add teachers")
        with st.form("bulk_teacher_form"):
            bulk_teachers = st.text_area("Paste teachers (one per line): name,subject,status")
            if st.form_submit_button("Add Teachers"):
                added = 0
                for line in bulk_teachers.splitlines():
                    parts = [p.strip() for p in line.split(",")]
                    if not parts or len(parts) < 1:
                        continue
                    name = parts[0]
                    subject = parts[1] if len(parts) > 1 else ""
                    status = parts[2] if len(parts) > 2 else ""
                    saved = add_school_record("teachers", {"name": name, "subject": subject, "status": status})
                    if saved:
                        added += 1
                st.success(f"Added {added} teachers")

        teacher_rows = get_school_records("teachers")
        st.dataframe({"Name": [row.get("name") for row in teacher_rows], "Subject": [row.get("subject") for row in teacher_rows], "Status": [row.get("status") for row in teacher_rows]})

    elif page == "Fees":
        st.subheader("Fees Management")
        with st.form("fees_form"):
            fee_student = st.text_input("Student Name", key="fee_student")
            fee_amount = st.text_input("Fee", key="fee_amount")
            fee_status = st.text_input("Status", key="fee_status")
            if st.form_submit_button("Add Fee"):
                saved = add_school_record("fees", {"student": fee_student, "fee": fee_amount, "status": fee_status})
                if saved:
                    st.success("Fee record saved to Supabase.")
                else:
                    st.warning("Fee record saved locally only. Supabase was unavailable or insert failed.")
        st.markdown("---")
        st.subheader("Bulk add fees")
        with st.form("bulk_fee_form"):
            bulk_fees = st.text_area("Paste fees (one per line): student,fee,status")
            if st.form_submit_button("Add Fees"):
                added = 0
                for line in bulk_fees.splitlines():
                    parts = [p.strip() for p in line.split(",")]
                    if not parts or len(parts) < 2:
                        continue
                    student = parts[0]
                    fee = parts[1]
                    status = parts[2] if len(parts) > 2 else ""
                    saved = add_school_record("fees", {"student": student, "fee": fee, "status": status})
                    if saved:
                        added += 1
                st.success(f"Added {added} fee records")

        fee_rows = get_school_records("fees")
        st.dataframe({"Student": [row.get("student") for row in fee_rows], "Fee": [row.get("fee") for row in fee_rows], "Status": [row.get("status") for row in fee_rows]})

    elif page == "Attendance":
        st.subheader("Attendance Management")
        with st.form("attendance_form"):
            class_name = st.text_input("Class", key="class_name")
            present_count = st.text_input("Present", key="present_count")
            attendance_value = st.text_input("Attendance", key="attendance_value")
            if st.form_submit_button("Add Attendance"):
                saved = add_school_record("attendance", {"class_name": class_name, "present": present_count, "attendance": attendance_value})
                if saved:
                    st.success("Attendance saved to Supabase.")
                else:
                    st.warning("Attendance saved locally only. Supabase was unavailable or insert failed.")
        st.markdown("---")
        st.subheader("Bulk add attendance")
        with st.form("bulk_attendance_form"):
            bulk_att = st.text_area("Paste attendance (one per line): class_name,present,attendance")
            if st.form_submit_button("Add Attendance Batch"):
                added = 0
                for line in bulk_att.splitlines():
                    parts = [p.strip() for p in line.split(",")]
                    if not parts or len(parts) < 2:
                        continue
                    cname = parts[0]
                    present = parts[1]
                    att = parts[2] if len(parts) > 2 else ""
                    saved = add_school_record("attendance", {"class_name": cname, "present": present, "attendance": att})
                    if saved:
                        added += 1
                st.success(f"Added {added} attendance records")

        attendance_rows = get_school_records("attendance")
        st.dataframe({"Class": [row.get("class_name") for row in attendance_rows], "Present": [row.get("present") for row in attendance_rows], "Attendance": [row.get("attendance") for row in attendance_rows]})

    elif page == "Teacher Attendance":
        st.subheader("Teacher Attendance")
        with st.form("teacher_attendance_form"):
            teacher_name = st.text_input("Teacher Name", key="teacher_attendance_name")
            teacher_date = st.text_input("Date", key="teacher_attendance_date")
            teacher_status = st.selectbox("Status", ["Present", "Absent", "Leave"], key="teacher_attendance_status")
            if st.form_submit_button("Add Teacher Attendance"):
                saved = add_school_record("teacher_attendance", {"teacher": teacher_name, "date": teacher_date, "status": teacher_status})
                if saved:
                    st.success("Teacher attendance saved to Supabase.")
                else:
                    st.warning("Teacher attendance saved locally only. Supabase was unavailable or insert failed.")
        teacher_attendance_rows = get_school_records("teacher_attendance")
        st.dataframe({"Teacher": [row["teacher"] for row in teacher_attendance_rows], "Date": [row["date"] for row in teacher_attendance_rows], "Status": [row["status"] for row in teacher_attendance_rows]})

    elif page == "Student Attendance":
        st.subheader("Student Attendance")
        with st.form("student_attendance_form"):
            student_name = st.text_input("Student Name", key="student_attendance_name")
            student_class = st.text_input("Class", key="student_attendance_class")
            student_status = st.selectbox("Status", ["Present", "Absent", "Late"], key="student_attendance_status")
            if st.form_submit_button("Add Student Attendance"):
                saved = add_school_record("student_attendance", {"student": student_name, "class_name": student_class, "status": student_status})
                if saved:
                    st.success("Student attendance saved to Supabase.")
                else:
                    st.warning("Student attendance saved locally only. Supabase was unavailable or insert failed.")
        student_attendance_rows = get_school_records("student_attendance")
        st.dataframe({"Student": [row["student"] for row in student_attendance_rows], "Class": [row["class_name"] for row in student_attendance_rows], "Status": [row["status"] for row in student_attendance_rows]})

    elif page == "Review":
        st.subheader("Review")
        st.success("Review board for overall school performance")
        # Show counts and latest entries for key entities
        students = get_school_records("students")
        teachers = get_school_records("teachers")
        fees = get_school_records("fees")
        attendance = get_school_records("attendance")
        student_att = get_school_records("student_attendance")
        teacher_att = get_school_records("teacher_attendance")

        st.markdown(f"**Students:** {len(students)}  ")
        st.markdown(f"**Teachers:** {len(teachers)}  ")
        st.markdown(f"**Fees records:** {len(fees)}  ")
        st.markdown(f"**Attendance rows:** {len(attendance)}  ")

        st.markdown("---")
        st.markdown("### Recent Students")
        for s in students[-10:][::-1]:
            st.write(f"- {s.get('name')} • Grade: {s.get('grade')} • Avg: {s.get('avg_grade')}")

        st.markdown("### Recent Teachers")
        for t in teachers[-10:][::-1]:
            st.write(f"- {t.get('name')} • Subject: {t.get('subject')} • Status: {t.get('status')}")

        st.markdown("### Recent Fees")
        for f in fees[-10:][::-1]:
            st.write(f"- {f.get('student')} • Fee: {f.get('fee')} • Status: {f.get('status')}")

        st.markdown("### Recent Attendance")
        for a in attendance[-10:][::-1]:
            st.write(f"- {a.get('class_name')} • Present: {a.get('present')} • Attendance: {a.get('attendance')}")

    st.subheader("Available tasks")
    for task in get_role_tasks(user["role"]):
        st.checkbox(task, value=False, key=f"{user['role']}_{task}")

    if user["role"] == "principal":
        st.markdown("### Principal Tasks")
        st.markdown("- Review school reports")
        st.markdown("- Approve announcements")
        st.markdown("- Monitor staff activities")

    st.markdown("### Admin Requirements")
    st.markdown("- Monitor student attendance and academic progress")
    st.markdown("- Review staff and fee collection performance")
    st.markdown("- Track school operations, notices, and pending issues")

    st.markdown("### Quick actions")
    if user["role"] == "teacher":
        st.info("Upload lesson plans, review attendance, and manage class activities.")
    elif user["role"] == "principal":
        st.info("Review reports, approve announcements, and monitor school performance.")
    elif user["role"] == "accountant":
        st.info("Track fees, expenses, and payroll activities.")
    elif user["role"] == "student":
        st.info("View lessons, submit assignments, and check your attendance.")
    elif user["role"] == "library":
        st.info("Manage inventory, issue books, and monitor returns.")


def main():
    if "user" not in st.session_state:
        render_login()
    else:
        render_dashboard(st.session_state["user"])


if __name__ == "__main__":
    main()
