import streamlit as st
import sqlite3
from sqlite3 import Error
import boto3

# Configure S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id='AKIA5QK5MFS4WKOESOW6',
    aws_secret_access_key='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')


# Database initialization
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    try:
        query = '''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            domain TEXT NOT NULL,
            resume_path TEXT,
            interview_date TEXT NOT NULL,
            panel_name TEXT NOT NULL
        );
        '''
        conn.execute(query)
    except Error as e:
        print(e)

def insert_candidate(conn, candidate):
    query = '''
    INSERT INTO candidates (name, domain, resume_path, interview_date, panel_name)
    VALUES (?, ?, ?, ?, ?);
    '''
    conn.execute(query, candidate)
    conn.commit()

def main():
    conn = create_connection('database.db')
    create_table(conn)

    st.title("Interview Management System")

    # Initialize session state for user type
    if 'user_type' not in st.session_state:
        st.session_state.user_type = "Regular User"

    # Login Page
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        # For demonstration purposes, use a simple hardcoded username and password
        if username == "admin" and password == "adminpassword":
            st.success("Logged in as Admin")
            st.session_state.user_type = "Admin"
        else:
            st.error("Invalid credentials")
            st.session_state.user_type = "Regular User"

    # Main App
    if st.session_state.user_type == "Admin":
        st.header("Admin Page")
        name = st.text_input("Candidate Name")
        domain = st.selectbox("Domain", ["Java", "QA", "Python", "Web Development", "Data Science", "DevOps"])
        domain = ','.join(domain)
        interview_date = st.date_input("Interview Start Date")
        panel_name = st.selectbox("Interview Panel Name", ["Vishal Ingale", "Amit Saharana" ] )
        panel_name=','.join(panel_name)
        resume = st.file_uploader("Upload Resume", type=["pdf", "docx"])

        if st.button("Submit"):
            if name and domain and interview_date and panel_name:
                
                if resume:
                    s3_path = f'resumes/{name}_{resume.name}'
                    s3.upload_fileobj(resume, '100ms-ims', s3_path)
                    candidate = (name, domain, s3_path, interview_date, panel_name)
                else:
                    candidate = (name, domain, s3_path, interview_date, panel_name)
                insert_candidate(conn, candidate)
                st.success("Candidate added successfully!")
    elif st.session_state.user_type == "Regular User":
        st.header("Regular User Page")
        candidates = conn.execute("SELECT name, domain, resume_path, interview_date, panel_name FROM candidates").fetchall()

        if candidates:
            st.write("List of Candidates:")
            for candidate in candidates:
                formatted_domain = candidate[1]
                resume_path = candidate[2]
                resume_icon = "📄" if resume_path else ""
                st.write(f"- {candidate[0]} ({formatted_domain}) {resume_icon} - Interview Date: {candidate[3]} [Download Resume]({resume_path})")


if __name__ == "__main__":
    main()
