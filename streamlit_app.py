import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import plotly.express as px

# Database connection parameters
DB_PARAMS = {
    'dbname': st.secrets["db_name"],
    'user': st.secrets["db_user"],
    'password': st.secrets["db_password"],
    'host': st.secrets["db_host"],
    'port': st.secrets["db_port"]
}

# Page configuration
st.set_page_config(
    page_title="Employee Management System",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to connect to PostgreSQL database
@st.cache_resource
def init_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Function to execute queries
@st.cache_data
def run_query(query, params=None):
    conn = init_connection()
    if conn is None:
        return None
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Query execution error: {e}")
        return None
    finally:
        conn.close()

# Authentication function
def authenticate(username, password):
    query = """
    SELECT id, username, is_superuser, is_staff 
    FROM auth_user 
    WHERE username = %s AND password = %s
    """
    result = run_query(query, (username, password))
    if result is not None and not result.empty:
        return result.iloc[0].to_dict()
    return None

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# Login function
def login():
    st.title("Employee Management System")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            user = authenticate(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user_data = user
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

# Function to get all employees
def get_employees():
    query = """
    SELECT e.id, e."eID", e."firstName", e."lastName", e.email, e.contact, 
           e."joinDate", e.salary, e.address, e.role, e.status
    FROM employee_employee e
    ORDER BY e."eID"
    """
    return run_query(query)

# Function to get all departments
def get_departments():
    query = """
    SELECT d.id, d.name, d.description
    FROM employee_department d
    ORDER BY d.name
    """
    return run_query(query)

# Function to get attendance data
def get_attendance(filter_date=None):
    if filter_date:
        query = """
        SELECT a.id, e."firstName" || ' ' || e."lastName" as employee_name, 
               a.date, a."timeIn", a."timeOut", a.status
        FROM employee_attendance a
        JOIN employee_employee e ON a.employee_id = e.id
        WHERE a.date = %s
        ORDER BY a.date DESC, e."firstName"
        """
        return run_query(query, (filter_date,))
    else:
        query = """
        SELECT a.id, e."firstName" || ' ' || e."lastName" as employee_name, 
               a.date, a."timeIn", a."timeOut", a.status
        FROM employee_attendance a
        JOIN employee_employee e ON a.employee_id = e.id
        ORDER BY a.date DESC, e."firstName"
        LIMIT 100
        """
        return run_query(query)

# Function to get notice data
def get_notices():
    query = """
    SELECT n.id, n.title, n.description, n.date
    FROM employee_notice n
    ORDER BY n.date DESC
    """
    return run_query(query)

# Function to get work assignments
def get_work_assignments(employee_id=None):
    if employee_id:
        query = """
        SELECT w.id, w.title, w.description, w.date, w.deadline, w.status,
               e."firstName" || ' ' || e."lastName" as employee_name
        FROM employee_work w
        JOIN employee_employee e ON w.employee_id = e.id
        WHERE w.employee_id = %s
        ORDER BY w.deadline
        """
        return run_query(query, (employee_id,))
    else:
        query = """
        SELECT w.id, w.title, w.description, w.date, w.deadline, w.status,
               e."firstName" || ' ' || e."lastName" as employee_name
        FROM employee_work w
        JOIN employee_employee e ON w.employee_id = e.id
        ORDER BY w.deadline
        """
        return run_query(query)

# Dashboard page
def dashboard():
    st.title("Dashboard")
    
    # Get data for dashboard
    employees_df = get_employees()
    departments_df = get_departments()
    attendance_df = get_attendance()
    notices_df = get_notices()
    
    if employees_df is None or departments_df is None or attendance_df is None or notices_df is None:
        st.warning("Some data could not be loaded. Please check database connection.")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Employees", len(employees_df))
    
    with col2:
        st.metric("Departments", len(departments_df))
    
    with col3:
        st.metric("Present Today", len(attendance_df[attendance_df['date'] == datetime.now().date()]) if 'date' in attendance_df.columns else 0)
    
    # Employee status distribution
    if 'status' in employees_df.columns:
        st.subheader("Employee Status Distribution")
        status_counts = employees_df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status', title='Employee Status')
        st.plotly_chart(fig)
    
    # Recent notices
    st.subheader("Recent Notices")
    if not notices_df.empty:
        st.dataframe(notices_df.head(5))
    else:
        st.info("No notices available")

# Employee page
def employees_page():
    st.title("Employees")
    
    # Get employees data
    employees_df = get_employees()
    
    if employees_df is None:
        st.warning("Employee data could not be loaded. Please check database connection.")
        return
    
    # Filters
    st.subheader("Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'role' in employees_df.columns:
            roles = employees_df['role'].unique()
            selected_role = st.selectbox("Filter by Role", ["All"] + list(roles))
    
    with col2:
        if 'status' in employees_df.columns:
            statuses = employees_df['status'].unique()
            selected_status = st.selectbox("Filter by Status", ["All"] + list(statuses))
    
    # Apply filters
    filtered_df = employees_df.copy()
    if 'role' in employees_df.columns and selected_role != "All":
        filtered_df = filtered_df[filtered_df['role'] == selected_role]
    
    if 'status' in employees_df.columns and selected_status != "All":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    # Display employees
    st.subheader("Employee List")
    st.dataframe(filtered_df)
    
    # Add employee form (only for admin)
    if st.session_state.user_data and (st.session_state.user_data['is_superuser'] or st.session_state.user_data['is_staff']):
        st.subheader("Add New Employee")
        with st.form("add_employee_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                eid = st.text_input("Employee ID")
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                email = st.text_input("Email")
                contact = st.text_input("Contact")
            
            with col2:
                join_date = st.date_input("Join Date")
                salary = st.number_input("Salary", min_value=0)
                address = st.text_area("Address")
                role = st.text_input("Role")
                status = st.selectbox("Status", ["Active", "Inactive"])
            
            submit = st.form_submit_button("Add Employee")
            
            if submit:
                st.info("This would add an employee to the database (functionality not implemented in this demo)")

# Attendance page
def attendance_page():
    st.title("Attendance")
    
    # Date filter
    selected_date = st.date_input("Select Date", datetime.now().date())
    
    # Get attendance data
    attendance_df = get_attendance(selected_date)
    
    if attendance_df is None:
        st.warning("Attendance data could not be loaded. Please check database connection.")
        return
    
    # Display attendance
    st.subheader(f"Attendance for {selected_date}")
    
    if attendance_df.empty:
        st.info(f"No attendance records for {selected_date}")
    else:
        st.dataframe(attendance_df)
    
    # Mark attendance form (only for admin)
    if st.session_state.user_data and (st.session_state.user_data['is_superuser'] or st.session_state.user_data['is_staff']):
        st.subheader("Mark Attendance")
        
        # Get employees data for dropdown
        employees_df = get_employees()
        
        if employees_df is not None:
            with st.form("mark_attendance_form"):
                employee = st.selectbox("Employee", 
                                       employees_df.apply(lambda row: f"{row['firstName']} {row['lastName']} ({row['eID']})", axis=1))
                date = st.date_input("Date", datetime.now().date())
                time_in = st.time_input("Time In", datetime.now().time())
                time_out = st.time_input("Time Out")
                status = st.selectbox("Status", ["Present", "Absent", "Half Day"])
                
                submit = st.form_submit_button("Mark Attendance")
                
                if submit:
                    st.info("This would mark attendance in the database (functionality not implemented in this demo)")

# Notices page
def notices_page():
    st.title("Notices")
    
    # Get notices data
    notices_df = get_notices()
    
    if notices_df is None:
        st.warning("Notice data could not be loaded. Please check database connection.")
        return
    
    # Display notices
    st.subheader("All Notices")
    
    if notices_df.empty:
        st.info("No notices available")
    else:
        for _, notice in notices_df.iterrows():
            with st.expander(f"{notice['title']} - {notice['date']}"):
                st.write(notice['description'])
    
    # Add notice form (only for admin)
    if st.session_state.user_data and (st.session_state.user_data['is_superuser'] or st.session_state.user_data['is_staff']):
        st.subheader("Publish New Notice")
        with st.form("add_notice_form"):
            title = st.text_input("Title")
            description = st.text_area("Description")
            date = st.date_input("Date", datetime.now().date())
            
            submit = st.form_submit_button("Publish Notice")
            
            if submit:
                st.info("This would publish a notice to the database (functionality not implemented in this demo)")

# Work page
def work_page():
    st.title("Work Assignments")
    
    # Get work data
    work_df = get_work_assignments()
    
    if work_df is None:
        st.warning("Work data could not be loaded. Please check database connection.")
        return
    
    # Display work assignments
    st.subheader("All Work Assignments")
    
    if work_df.empty:
        st.info("No work assignments available")
    else:
        st.dataframe(work_df)
    
    # Assign work form (only for admin)
    if st.session_state.user_data and (st.session_state.user_data['is_superuser'] or st.session_state.user_data['is_staff']):
        st.subheader("Assign New Work")
        
        # Get employees data for dropdown
        employees_df = get_employees()
        
        if employees_df is not None:
            with st.form("assign_work_form"):
                employee = st.selectbox("Employee", 
                                       employees_df.apply(lambda row: f"{row['firstName']} {row['lastName']} ({row['eID']})", axis=1))
                title = st.text_input("Title")
                description = st.text_area("Description")
                date = st.date_input("Date", datetime.now().date())
                deadline = st.date_input("Deadline")
                status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
                
                submit = st.form_submit_button("Assign Work")
                
                if submit:
                    st.info("This would assign work in the database (functionality not implemented in this demo)")

# Main app
def main():
    if not st.session_state.authenticated:
        login()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.user_data['username']}")
        
        # Navigation
        page = st.sidebar.selectbox(
            "Navigation",
            ["Dashboard", "Employees", "Attendance", "Notices", "Work Assignments"]
        )
        
        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
        
        # Display selected page
        if page == "Dashboard":
            dashboard()
        elif page == "Employees":
            employees_page()
        elif page == "Attendance":
            attendance_page()
        elif page == "Notices":
            notices_page()
        elif page == "Work Assignments":
            work_page()

if __name__ == "__main__":
    main()
