from datetime import datetime
from pathlib import Path
import re

import requests
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"
GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"


st.set_page_config(
    page_title="Enterprise Resume Generator",
    page_icon="",
    layout="wide",
)


SESSION_DEFAULTS = {
    "page": "login",
    "token": None,
    "token_type": None,
    "user_email": None,
    "generated_pdf": None,
    "generated_pdf_name": "generated_resume.pdf",
    "generated_resumes": [],
}

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

if st.session_state.page not in {"login", "signup"} and not st.session_state.token:
    st.session_state.page = "login"


st.markdown(
    """
    <style>
        .block-container {
            max-width: 1160px;
            padding-top: 1.5rem;
        }

        div[data-testid="stHorizontalBlock"] {
            align-items: center;
        }

        .app-title {
            font-size: 1.8rem;
            font-weight: 750;
            margin: 0 0 0.15rem;
        }

        .app-subtitle {
            color: #64748b;
            margin-bottom: 1.25rem;
        }

        .metric-panel {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            background: #ffffff;
        }

        .muted {
            color: #64748b;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def auth_headers():
    if not st.session_state.token:
        return {}

    token_type = st.session_state.token_type or "bearer"
    return {"Authorization": f"{token_type.title()} {st.session_state.token}"}


def auth_request(endpoint, payload):
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=10,
        )
    except requests.RequestException:
        return None, "Could not connect to the backend. Start FastAPI on port 8000."

    if response.ok:
        return response.json(), None

    return None, extract_error(response)


def extract_error(response):
    try:
        detail = response.json().get("detail")
    except ValueError:
        detail = response.text

    if isinstance(detail, list):
        messages = []
        for item in detail:
            field = item.get("loc", ["field"])[-1]
            message = item.get("msg", "Invalid value")
            messages.append(f"{field}: {message}")
        detail = "\n".join(messages)

    return detail or "Request failed"


def go_to(page):
    st.session_state.page = page
    st.rerun()


def logout():
    for key, value in SESSION_DEFAULTS.items():
        st.session_state[key] = value
    st.rerun()


def render_header():
    st.markdown('<h1 class="app-title">Enterprise Resume Generator</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Generate tailored resumes and track generated files by company.</div>',
        unsafe_allow_html=True,
    )


def render_navbar():
    nav_left, nav_right = st.columns([0.72, 0.28])

    with nav_left:
        dashboard_tab, generate_tab = st.columns(2)
        with dashboard_tab:
            if st.button("Dashboard", use_container_width=True, type="primary" if st.session_state.page == "dashboard" else "secondary"):
                go_to("dashboard")
        with generate_tab:
            if st.button("Generate Resume", use_container_width=True, type="primary" if st.session_state.page == "generate_resume" else "secondary"):
                go_to("generate_resume")

    with nav_right:
        st.caption(f"Signed in as {st.session_state.user_email}")
        if st.button("Logout", use_container_width=True):
            logout()

    st.divider()


def get_generated_resumes():
    resumes = list(st.session_state.generated_resumes)

    if not GENERATED_DIR.exists():
        return resumes

    for file_path in sorted(GENERATED_DIR.glob("*.pdf"), key=lambda path: path.stat().st_mtime, reverse=True):
        stat = file_path.stat()
        resumes.append(
            {
                "company": "Company not provided",
                "file_name": file_path.name,
                "date": datetime.fromtimestamp(stat.st_mtime).strftime("%d %b %Y"),
                "time": datetime.fromtimestamp(stat.st_mtime).strftime("%I:%M %p"),
                "path": file_path,
                "pdf_bytes": None,
                "size_kb": max(1, round(stat.st_size / 1024)),
            }
        )

    return resumes


def show_login():
    render_header()

    left, center, right = st.columns([0.25, 0.5, 0.25])
    with center:
        st.subheader("Welcome Back")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login", use_container_width=True, type="primary"):
            email = email.strip()

            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                result, error = auth_request(
                    "/auth/login",
                    {
                        "email": email,
                        "password": password,
                    },
                )

                if error:
                    st.error(error)
                else:
                    st.session_state.token = result["access_token"]
                    st.session_state.token_type = result["token_type"]
                    st.session_state.user_email = email
                    st.session_state.page = "dashboard"
                    st.rerun()

        st.divider()
        st.write("Don't have an account?")

        if st.button("Create an account", use_container_width=True):
            go_to("signup")


def show_signup():
    render_header()

    left, center, right = st.columns([0.25, 0.5, 0.25])
    with center:
        st.subheader("Create your account")
        name = st.text_input("Name", placeholder="Your name")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")

        if st.button("Create Account", use_container_width=True, type="primary"):
            name = name.strip()
            email = email.strip()

            if not name or not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                _, error = auth_request(
                    "/auth/register",
                    {
                        "name": name,
                        "email": email,
                        "password": password,
                    },
                )

                if error:
                    st.error(error)
                else:
                    st.success("Account created. You can log in now.")
                    st.session_state.page = "login"
                    st.rerun()

        st.divider()
        st.write("Already have an account?")

        if st.button("Back to Login", use_container_width=True):
            go_to("login")


def show_dashboard():
    render_header()
    render_navbar()

    resumes = get_generated_resumes()
    company_count = len({resume["company"] for resume in resumes})

    total_col, company_col, latest_col = st.columns(3)
    with total_col:
        st.metric("Generated resumes", len(resumes))
    with company_col:
        st.metric("Companies", company_count)
    with latest_col:
        st.metric("Latest generated", resumes[0]["date"] if resumes else "No files")

    st.subheader("Generated Resume History")

    if not resumes:
        st.info("No generated resumes found yet. Generated PDF files will appear here from the generated folder.")
        if st.button("Generate Resume", type="primary"):
            go_to("generate_resume")
        return

    grouped = {}
    for resume in resumes:
        grouped.setdefault(resume["company"], []).append(resume)

    for company, company_resumes in grouped.items():
        with st.expander(f"{company} ({len(company_resumes)})", expanded=True):
            for resume in company_resumes:
                name_col, date_col, size_col, action_col = st.columns([0.44, 0.22, 0.14, 0.20])
                with name_col:
                    st.write(resume["file_name"])
                with date_col:
                    st.write(f'{resume["date"]} at {resume["time"]}')
                with size_col:
                    st.write(f'{resume["size_kb"]} KB')
                with action_col:
                    pdf_data = resume["pdf_bytes"] if resume["pdf_bytes"] else resume["path"].read_bytes()
                    st.download_button(
                        "Download",
                        data=pdf_data,
                        file_name=resume["file_name"],
                        mime="application/pdf",
                        use_container_width=True,
                        key=f'download-{resume["file_name"]}-{resume["date"]}-{resume["time"]}',
                    )


def show_generate_resume():
    render_header()
    render_navbar()

    st.subheader("Generate Resume")

    jd_col, resume_col = st.columns(2)
    with jd_col:
        jd_file = st.file_uploader("Upload Company JD", type=["pdf", "docx", "txt"], key="jd-upload")
    with resume_col:
        resume_file = st.file_uploader("Upload Person Resume", type=["pdf", "docx", "txt"], key="resume-upload")

    st.divider()
    st.markdown("#### Candidate Details")

    name_col, email_col = st.columns(2)
    with name_col:
        candidate_name = st.text_input("Name", placeholder="Example: Surya Kandimalla")
    with email_col:
        candidate_email = st.text_input("Email", placeholder="Example: surya@example.com")

    phone_col, location_col = st.columns(2)
    with phone_col:
        candidate_phone = st.text_input("Phone", placeholder="Example: +91 98765 43210")
    with location_col:
        candidate_location = st.text_input("Location", placeholder="Example: Hyderabad, India")

    linkedin_col, portfolio_col = st.columns(2)
    with linkedin_col:
        linkedin_url = st.text_input("LinkedIn", placeholder="https://linkedin.com/in/username")
    with portfolio_col:
        portfolio_url = st.text_input("Portfolio / GitHub", placeholder="https://github.com/username")

    st.markdown("#### Job Target")

    company_col, role_col = st.columns(2)
    with company_col:
        company_name = st.text_input("Company Name", placeholder="Example: Acme Corp")
    with role_col:
        role_name = st.text_input("Role / Job Title", placeholder="Example: Backend Engineer")

    experience_col, domain_col = st.columns(2)
    with experience_col:
        years_experience = st.text_input("Years of Experience", placeholder="Example: 3")
    with domain_col:
        primary_domain = st.text_input("Primary Domain", placeholder="Example: Data Analytics")

    st.markdown("#### Profile Inputs")

    skills = st.text_area(
        "Skills",
        placeholder="Example: Python, FastAPI, SQL, Streamlit, Power BI",
        height=95,
    )
    projects = st.text_area(
        "Projects",
        placeholder="Mention important projects, tools used, and measurable outcomes.",
        height=110,
    )
    education = st.text_area(
        "Education",
        placeholder="Example: B.Tech in Computer Science, University name, graduation year.",
        height=85,
    )
    certifications = st.text_area(
        "Certifications",
        placeholder="Example: AWS Cloud Practitioner, Google Data Analytics Certificate.",
        height=85,
    )
    notes = st.text_area(
        "Additional Instructions",
        placeholder="Add achievements, resume tone, preferred format, or anything the agents should emphasize.",
        height=100,
    )

    required_fields = [
        resume_file,
        jd_file,
        candidate_name.strip(),
        company_name.strip(),
        role_name.strip(),
        skills.strip(),
    ]
    can_submit = all(required_fields)

    if st.button("Generate Resume PDF", type="primary", use_container_width=True, disabled=not can_submit):
        profile_data = {
            "candidate_name": candidate_name.strip(),
            "candidate_email": candidate_email.strip(),
            "candidate_phone": candidate_phone.strip(),
            "candidate_location": candidate_location.strip(),
            "linkedin_url": linkedin_url.strip(),
            "portfolio_url": portfolio_url.strip(),
            "company_name": company_name.strip(),
            "role_name": role_name.strip(),
            "years_experience": years_experience.strip(),
            "primary_domain": primary_domain.strip(),
            "skills": skills.strip(),
            "projects": projects.strip(),
            "education": education.strip(),
            "certifications": certifications.strip(),
            "notes": notes.strip(),
        }
        generate_resume(profile_data, resume_file, jd_file)

    if not can_submit:
        st.caption("Resume file, JD file, name, company name, role, and skills are required.")

    if st.session_state.generated_pdf:
        st.success("Resume PDF is ready.")
        st.download_button(
            "Download Generated Resume",
            data=st.session_state.generated_pdf,
            file_name=st.session_state.generated_pdf_name,
            mime="application/pdf",
            use_container_width=True,
        )


def generate_resume(profile_data, resume_file, jd_file):
    resume_file.seek(0)
    jd_file.seek(0)

    files = {
        "resume_file": (resume_file.name, resume_file.getvalue(), resume_file.type or "application/octet-stream"),
        "jd_file": (jd_file.name, jd_file.getvalue(), jd_file.type or "application/octet-stream"),
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/resume/generate",
            headers=auth_headers(),
            data=profile_data,
            files=files,
            timeout=60,
        )
    except requests.RequestException:
        st.error("Could not connect to the resume generation API. The frontend is ready, but the backend endpoint is not available.")
        return

    if not response.ok:
        st.error(extract_error(response))
        return

    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = response.json()
        pdf_url = payload.get("pdf_url") or payload.get("download_url")
        st.success("Resume generated successfully.")
        if pdf_url:
            st.link_button("Open Generated PDF", pdf_url, use_container_width=True)
        return

    st.session_state.generated_pdf = response.content
    safe_company = re.sub(r"[^A-Za-z0-9]+", "_", profile_data["company_name"]).strip("_").lower()
    safe_role = re.sub(r"[^A-Za-z0-9]+", "_", profile_data["role_name"]).strip("_").lower()
    st.session_state.generated_pdf_name = f"{safe_company}_{safe_role}_resume.pdf"
    generated_at = datetime.now()
    st.session_state.generated_resumes.insert(
        0,
        {
            "company": profile_data["company_name"],
            "file_name": st.session_state.generated_pdf_name,
            "date": generated_at.strftime("%d %b %Y"),
            "time": generated_at.strftime("%I:%M %p"),
            "path": None,
            "pdf_bytes": response.content,
            "size_kb": max(1, round(len(response.content) / 1024)),
        },
    )
    st.rerun()


if st.session_state.page == "login":
    show_login()
elif st.session_state.page == "signup":
    show_signup()
elif st.session_state.page == "generate_resume":
    show_generate_resume()
else:
    show_dashboard()
