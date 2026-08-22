
import os
import re
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv(
    "RESUME_API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

st.set_page_config(
    page_title="Resume Studio",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "page": "login",
    "token": None,
    "token_type": "bearer",
    "user_email": None,
    "user_name": None,
    "generation_result": None,
    "history": [],
    "backend_status": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

if st.session_state.token is None and st.session_state.page not in {
    "login",
    "signup",
}:
    st.session_state.page = "login"


# ============================================================
# DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>
        :root {
            --bg: #0b1020;
            --panel: #111827;
            --panel-2: #172033;
            --border: #263247;
            --text: #f8fafc;
            --muted: #94a3b8;
            --accent: #7c3aed;
            --accent-2: #8b5cf6;
            --success: #22c55e;
            --danger: #ef4444;
            --warning: #f59e0b;
        }

        .stApp {
            background:
                radial-gradient(circle at 80% 0%, rgba(124,58,237,.14), transparent 28rem),
                radial-gradient(circle at 0% 20%, rgba(59,130,246,.08), transparent 24rem),
                #0b1020;
            color: var(--text);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 1.4rem;
            padding-bottom: 4rem;
        }

        section[data-testid="stSidebar"] {
            background: #0a0f1c;
            border-right: 1px solid #1f2937;
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.4rem;
        }

        h1, h2, h3, h4, p, label {
            color: var(--text);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: .8rem;
            margin-bottom: 1.8rem;
        }

        .brand-mark {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #7c3aed, #2563eb);
            color: white;
            font-weight: 800;
            font-size: 1.1rem;
            box-shadow: 0 10px 30px rgba(124,58,237,.25);
        }

        .brand-title {
            font-size: 1.05rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .brand-subtitle {
            color: var(--muted);
            font-size: .75rem;
            margin-top: .15rem;
        }

        .hero {
            padding: 2.1rem 2.2rem;
            border: 1px solid var(--border);
            border-radius: 22px;
            background:
                linear-gradient(135deg, rgba(124,58,237,.16), rgba(37,99,235,.08)),
                rgba(17,24,39,.82);
            box-shadow: 0 24px 70px rgba(0,0,0,.22);
            margin-bottom: 1.5rem;
        }

        .eyebrow {
            color: #a78bfa;
            text-transform: uppercase;
            letter-spacing: .12em;
            font-size: .72rem;
            font-weight: 800;
            margin-bottom: .5rem;
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(2rem, 4vw, 3.4rem);
            line-height: 1.02;
        }

        .hero p {
            color: #cbd5e1;
            max-width: 760px;
            margin-top: .8rem;
            font-size: 1rem;
        }

        .card {
            border: 1px solid var(--border);
            border-radius: 18px;
            background: rgba(17,24,39,.82);
            padding: 1.25rem;
            box-shadow: 0 14px 40px rgba(0,0,0,.16);
        }

        .card-title {
            font-size: 1rem;
            font-weight: 750;
            margin-bottom: .25rem;
        }

        .card-subtitle {
            color: var(--muted);
            font-size: .85rem;
            margin-bottom: 1rem;
        }

        .stat {
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem 1.1rem;
            background: rgba(17,24,39,.72);
        }

        .stat-label {
            color: var(--muted);
            font-size: .78rem;
        }

        .stat-value {
            color: white;
            font-size: 1.7rem;
            font-weight: 800;
            margin-top: .15rem;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            padding: .38rem .7rem;
            border-radius: 999px;
            font-size: .75rem;
            font-weight: 700;
            border: 1px solid #334155;
            background: #111827;
        }

        .dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            display: inline-block;
        }

        .dot-green { background: #22c55e; }
        .dot-red { background: #ef4444; }

        .step {
            display: flex;
            align-items: center;
            gap: .8rem;
            padding: .7rem .8rem;
            border: 1px solid var(--border);
            border-radius: 12px;
            background: rgba(15,23,42,.65);
            margin-bottom: .55rem;
        }

        .step-number {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #1e293b;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: .75rem;
            font-weight: 800;
            color: #c4b5fd;
        }

        .step-title {
            font-weight: 700;
            font-size: .85rem;
        }

        .step-copy {
            color: var(--muted);
            font-size: .72rem;
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.1rem;
            border: 1px solid var(--border);
            border-radius: 16px;
            background: rgba(17,24,39,.82);
        }

        .result-title {
            font-size: 1.15rem;
            font-weight: 800;
        }

        .result-meta {
            color: var(--muted);
            font-size: .78rem;
        }

        .resume-preview {
            border: 1px solid #d1d5db;
            border-radius: 12px;
            background: white;
            color: #111827;
            padding: 2rem;
            min-height: 400px;
        }

        .resume-preview h2,
        .resume-preview h3,
        .resume-preview p,
        .resume-preview li {
            color: #111827;
        }

        .empty-state {
            text-align: center;
            padding: 4rem 2rem;
            border: 1px dashed #334155;
            border-radius: 18px;
            background: rgba(15,23,42,.45);
        }

        div[data-testid="stFileUploader"] {
            border-radius: 14px;
        }

        .small-muted {
            color: #94a3b8;
            font-size: .78rem;
        }

        /* Improve Streamlit button hierarchy */
        .stButton > button,
        .stDownloadButton > button {
            border-radius: 10px;
            font-weight: 700;
            min-height: 42px;
        }

        /* Hide Streamlit menu/footer chrome */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API
# ============================================================

def auth_headers():
    token = st.session_state.get("token")
    if not token:
        return {}

    token_type = st.session_state.get("token_type") or "bearer"
    return {
        "Authorization": f"{token_type.title()} {token}",
    }


def extract_error(response):
    try:
        payload = response.json()
        detail = payload.get("detail")
    except ValueError:
        detail = response.text

    if isinstance(detail, list):
        messages = []
        for item in detail:
            if isinstance(item, dict):
                location = item.get("loc", ["field"])
                field = location[-1] if location else "field"
                message = item.get("msg", "Invalid value")
                messages.append(f"{field}: {message}")
        return "\n".join(messages) or "Request failed."

    if isinstance(detail, dict):
        return (
            detail.get("message")
            or detail.get("error")
            or "Request failed."
        )

    return detail or "Request failed."


def api_request(
    method,
    endpoint,
    *,
    data=None,
    json=None,
    files=None,
    timeout=15,
):
    try:
        response = requests.request(
            method=method,
            url=f"{API_BASE_URL}{endpoint}",
            headers=auth_headers(),
            data=data,
            json=json,
            files=files,
            timeout=timeout,
        )
    except requests.Timeout:
        return None, (
            "The backend did not respond within the allowed time. "
            "The operation may still be processing."
        )
    except requests.ConnectionError:
        return None, (
            f"Could not reach FastAPI at {API_BASE_URL}. "
            "Make sure the backend is running."
        )
    except requests.RequestException as exc:
        return None, f"Backend request failed: {exc}"

    if response.ok:
        return response, None

    if response.status_code == 401:
        clear_session()
        return response, "Your session expired. Please sign in again."

    if response.status_code == 429:
        return response, (
            "The AI service quota or rate limit has been reached. "
            "Please try again later."
        )

    if response.status_code >= 500:
        return response, (
            f"The backend returned an error ({response.status_code}). "
            f"{extract_error(response)}"
        )

    return response, extract_error(response)


def backend_health():
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=5,
        )
        return response.ok
    except requests.RequestException:
        return False


# ============================================================
# SESSION / NAVIGATION
# ============================================================

def clear_session():
    for key, value in DEFAULTS.items():
        if isinstance(value, list):
            st.session_state[key] = []
        else:
            st.session_state[key] = value


def logout():
    clear_session()
    st.rerun()


def go_to(page):
    st.session_state.page = page
    st.rerun()


# ============================================================
# SHARED UI
# ============================================================


def sidebar():
    with st.sidebar:

        if st.session_state.token:
            st.caption(
                f"Signed in as {st.session_state.user_email or 'User'}"
            )

            if st.button(
                "Dashboard",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.page == "dashboard"
                    else "secondary"
                ),
            ):
                go_to("dashboard")

            if st.button(
                "Create Resume",
                use_container_width=True,
                type=(
                    "primary"
                    if st.session_state.page == "generate"
                    else "secondary"
                ),
            ):
                go_to("generate")

            st.divider()

            online = backend_health()
            if online:
                st.markdown(
                    '<div class="status-pill">'
                    '<span class="dot dot-green"></span>'
                    'Backend online'
                    '</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="status-pill">'
                    '<span class="dot dot-red"></span>'
                    'Backend offline'
                    '</div>',
                    unsafe_allow_html=True,
                )

            st.caption(API_BASE_URL)

            st.divider()

            if st.button("Sign out", use_container_width=True):
                logout()

        else:
            st.markdown(
                """
                <div class="small-muted">
                    Build a tailored resume from your experience,
                    target role, and job description.
                </div>
                """,
                unsafe_allow_html=True,
            )


def page_heading(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# AUTH
# ============================================================

def show_login():
    sidebar()

    _, center, _ = st.columns([0.18, 0.64, 0.18])

    with center:
        page_heading(
            "Welcome back",
            "Build a resume that gets noticed.",
            "Sign in to your workspace and create a job-specific resume "
            "with profile analysis, ATS optimization, generation, and review.",
        )

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True,
        )

        st.subheader("Sign in")

        email = st.text_input(
            "Email",
            placeholder="you@example.com",
            key="login_email",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
        )

        if st.button(
            "Sign in",
            use_container_width=True,
            type="primary",
        ):
            email = email.strip()

            if not email or not password:
                st.error("Enter your email and password.")
            else:
                response, error = api_request(
                    "POST",
                    "/auth/login",
                    json={
                        "email": email,
                        "password": password,
                    },
                    timeout=10,
                )

                if error:
                    st.error(error)
                else:
                    payload = response.json()

                    st.session_state.token = payload["access_token"]
                    st.session_state.token_type = payload.get(
                        "token_type",
                        "bearer",
                    )
                    st.session_state.user_email = email
                    st.session_state.page = "dashboard"

                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")

        if st.button(
            "Create an account",
            use_container_width=True,
        ):
            go_to("signup")


def show_signup():
    sidebar()

    _, center, _ = st.columns([0.18, 0.64, 0.18])

    with center:
        page_heading(
            "Get started",
            "Create your workspace.",
            "Set up your account and start generating tailored resumes.",
        )

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Create account")

        name = st.text_input(
            "Name",
            placeholder="Your name",
            key="signup_name",
        )

        email = st.text_input(
            "Email",
            placeholder="you@example.com",
            key="signup_email",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="At least 8 characters",
            key="signup_password",
        )

        confirm = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Repeat your password",
            key="signup_confirm",
        )

        if st.button(
            "Create account",
            use_container_width=True,
            type="primary",
        ):
            name = name.strip()
            email = email.strip()

            if not all([name, email, password, confirm]):
                st.error("Complete all fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                response, error = api_request(
                    "POST",
                    "/auth/register",
                    json={
                        "name": name,
                        "email": email,
                        "password": password,
                    },
                    timeout=10,
                )

                if error:
                    st.error(error)
                else:
                    st.success(
                        "Account created. You can sign in now."
                    )
                    go_to("login")

        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")

        if st.button(
            "Back to sign in",
            use_container_width=True,
        ):
            go_to("login")


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():
    sidebar()

    history = st.session_state.history

    page_heading(
        "Workspace",
        "Your resume command center.",
        "Create, review, and download tailored resumes from one workspace.",
    )

    total = len(history)
    companies = len(
        {
            item.get("company", "Unknown")
            for item in history
        }
    )
    latest = history[0]["date"] if history else "—"

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-label">Generated resumes</div>
                <div class="stat-value">{total}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-label">Companies targeted</div>
                <div class="stat-value">{companies}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-label">Latest generation</div>
                <div class="stat-value">{latest}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    left, right = st.columns([0.7, 0.3])

    with left:
        st.markdown("### Recent resumes")

    with right:
        if st.button(
            "＋ New resume",
            use_container_width=True,
            type="primary",
        ):
            go_to("generate")

    if not history:
        st.markdown(
            """
            <div class="empty-state">
                <h3>Nothing here yet</h3>
                <p>
                    Create your first tailored resume and it will
                    appear in this workspace.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for index, item in enumerate(history):
        with st.container(border=True):
            col1, col2, col3 = st.columns([0.5, 0.28, 0.22])

            with col1:
                st.markdown(
                    f"**{item['file_name']}**"
                )
                st.caption(
                    f"{item.get('company', 'Unknown company')} · "
                    f"{item.get('role', 'Target role')}"
                )

            with col2:
                st.caption(
                    f"{item['date']} at {item['time']}"
                )
                st.caption(
                    f"{item['size_kb']} KB"
                )

            with col3:
                st.download_button(
                    "Download",
                    data=item["pdf_bytes"],
                    file_name=item["file_name"],
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"history-download-{index}",
                )


# ============================================================
# GENERATION
# ============================================================

def generate_resume(
    target_data,
    resume_file,
    jd_file,
):
    files = {
        "resume_file": (
            resume_file.name,
            resume_file.getvalue(),
            resume_file.type or "application/octet-stream",
        ),
        "jd_file": (
            jd_file.name,
            jd_file.getvalue(),
            jd_file.type or "application/octet-stream",
        ),
    }

    with st.status(
        "Running the AI resume pipeline...",
        expanded=True,
    ) as status:
        st.write("Uploading your documents...")
        st.write("Analyzing your existing resume...")
        st.write("Matching your profile against the target job...")
        st.write("Writing and reviewing the tailored resume...")
        st.write("This can take a few minutes. Keep this tab open.")

        response, error = api_request(
            "POST",
            "/resume/generate",
            data=target_data,
            files=files,
            timeout=300,
        )

        if error:
            status.update(
                label="Resume generation failed",
                state="error",
                expanded=True,
            )
            st.error(error)
            return

        status.update(
            label="Resume generated successfully",
            state="complete",
            expanded=False,
        )

    content_type = (
        response.headers.get("content-type", "")
        .lower()
    )

    if "application/json" in content_type:
        payload = response.json()

        st.session_state.generation_result = payload
        render_results(payload)
        return

    if "application/pdf" in content_type:
        pdf_bytes = response.content

        safe_company = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            target_data["company_name"],
        ).strip("_").lower()

        safe_role = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            target_data["role_name"],
        ).strip("_").lower()

        filename = (
            f"{safe_company}_{safe_role}_resume.pdf"
        )

        generated_at = datetime.now()

        item = {
            "company": target_data["company_name"],
            "role": target_data["role_name"],
            "file_name": filename,
            "date": generated_at.strftime("%d %b %Y"),
            "time": generated_at.strftime("%I:%M %p"),
            "pdf_bytes": pdf_bytes,
            "size_kb": max(1, round(len(pdf_bytes) / 1024)),
        }

        st.session_state.history.insert(0, item)
        st.session_state.generation_result = None

        st.success("Your tailored resume is ready.")

        st.download_button(
            "Download generated resume",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
        return

    st.error(
        "The backend returned an unsupported response format."
    )


def render_results(payload):
    resume = (
        payload.get("resume")
        or payload.get("generated_resume")
    )

    ats = (
        payload.get("ats")
        or payload.get("ats_analysis")
    )

    review = (
        payload.get("review")
        or payload.get("review_result")
    )

    st.divider()
    st.markdown("### Generation results")

    # ============================================================
    # ATS ANALYSIS
    # ============================================================

    if ats:
        score = ats.get("ats_score")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "ATS score",
                f"{score}/100" if score is not None else "—",
            )

        with col2:
            keywords = ats.get("matching_keywords", [])
            st.metric(
                "Matched keywords",
                len(keywords),
            )

        with col3:
            missing = ats.get("missing_keywords", [])
            st.metric(
                "Missing keywords",
                len(missing),
            )

        with st.expander(
            "ATS analysis",
            expanded=True,
        ):
            if ats.get("matching_keywords"):
                st.write(
                    "Matched:",
                    ", ".join(
                        ats["matching_keywords"]
                    ),
                )

            if ats.get("missing_keywords"):
                st.write(
                    "Missing:",
                    ", ".join(
                        ats["missing_keywords"]
                    ),
                )

            if ats.get("formatting_suggestions"):
                st.write("Formatting suggestions:")

                for suggestion in ats[
                    "formatting_suggestions"
                ]:
                    st.markdown(
                        f"- {suggestion}"
                    )

    # ============================================================
    # REVIEWER
    # ============================================================

    if review:
        with st.expander(
            "Reviewer result",
            expanded=True,
        ):
            if review.get("approved"):
                st.success(
                    "Approved by the reviewer agent."
                )
            else:
                st.warning(
                    "Reviewer found issues."
                )

            issues = review.get("issues", [])

            if issues:
                st.write("Issues:")

                for issue in issues:
                    st.markdown(
                        f"- {issue}"
                    )

            recommendations = review.get(
                "recommendations",
                [],
            )

            if recommendations:
                st.write(
                    "Recommendations:"
                )

                for recommendation in recommendations:
                    st.markdown(
                        f"- {recommendation}"
                    )

    # ============================================================
    # GENERATED RESUME
    # ============================================================

    if not resume:
        return

    with st.expander(
        "Generated resume data",
        expanded=True,
    ):

        # ========================================================
        # PROFESSIONAL SUMMARY
        # ========================================================

        summary = resume.get(
            "professional_summary"
        )

        if summary:
            st.markdown(
                "#### Professional summary"
            )

            st.write(summary)

        # ========================================================
        # SKILLS
        # ========================================================

        skills = resume.get(
            "skills",
            [],
        )

        if skills:
            st.markdown("#### Skills")

            st.write(
                ", ".join(skills)
            )

        # ========================================================
        # EXPERIENCE
        # ========================================================

        experience = resume.get(
            "experience",
            [],
        )

        if experience:
            st.markdown(
                "#### Experience"
            )

            for job in experience:

                title = " — ".join(
                    filter(
                        None,
                        [
                            job.get("role"),
                            job.get("company"),
                        ],
                    )
                )

                st.markdown(
                    f"**{title or 'Experience'}**"
                )

                duration = job.get(
                    "duration"
                )

                if duration:
                    st.caption(duration)

                bullets = job.get(
                    "bullets",
                    [],
                )

                for bullet in bullets:
                    st.markdown(
                        f"- {bullet}"
                    )

        # ========================================================
        # PROJECTS
        # ========================================================

        projects = resume.get(
            "projects",
            [],
        )

        if projects:
            st.markdown(
                "#### Projects"
            )

            for project in projects:

                project_name = project.get(
                    "name",
                    "Project",
                )

                st.markdown(
                    f"**{project_name}**"
                )

                # Technologies
                technologies = project.get(
                    "technologies",
                    [],
                )

                if technologies:
                    st.caption(
                        " · ".join(
                            technologies
                        )
                    )

                # Project bullets
                bullets = project.get(
                    "bullets",
                    [],
                )

                for bullet in bullets:
                    st.markdown(
                        f"- {bullet}"
                    )

                # Backwards compatibility:
                # If an older backend still sends description
                description = project.get(
                    "description"
                )

                if not bullets and description:

                    if isinstance(
                        description,
                        list,
                    ):
                        for bullet in description:
                            st.markdown(
                                f"- {bullet}"
                            )
                    else:
                        st.write(
                            description
                        )

                # Project URL
                url = project.get(
                    "url"
                )

                if url:
                    st.markdown(
                        f"[View project / GitHub]({url})"
                    )

        # ========================================================
        # PUBLICATIONS
        # ========================================================

        publications = resume.get(
            "publications",
            [],
        )

        if publications:
            st.markdown(
                "#### Research Publications"
            )

            for publication in publications:

                title = publication.get(
                    "title",
                    "Untitled publication",
                )

                st.markdown(
                    f"**{title}**"
                )

                meta = []

                authors = publication.get(
                    "authors"
                )

                if authors:
                    meta.append(
                        authors
                    )

                venue = publication.get(
                    "venue"
                )

                if venue:
                    meta.append(
                        venue
                    )

                year = publication.get(
                    "year"
                )

                if year:
                    meta.append(
                        str(year)
                    )

                if meta:
                    st.caption(
                        " · ".join(meta)
                    )

                status = publication.get(
                    "status"
                )

                if status:
                    st.write(
                        f"**Status:** {status}"
                    )

                description = publication.get(
                    "description"
                )

                if description:
                    st.write(
                        description
                    )

                url = publication.get(
                    "url"
                )

                if url:
                    st.markdown(
                        f"[Publication link]({url})"
                    )

        # ========================================================
        # EDUCATION
        # ========================================================

        education = resume.get(
            "education",
            [],
        )

        if education:
            st.markdown(
                "#### Education"
            )

            for item in education:

                degree = item.get(
                    "degree"
                )

                field = item.get(
                    "field"
                )

                institution = item.get(
                    "institution"
                )

                duration = item.get(
                    "duration"
                )

                cgpa = item.get(
                    "cgpa"
                )

                if degree and field:
                    heading = (
                        f"{degree} in {field}"
                    )
                else:
                    heading = (
                        degree
                        or field
                        or "Education"
                    )

                st.markdown(
                    f"**{heading}**"
                )

                if institution:
                    st.write(
                        institution
                    )

                education_meta = []

                if duration:
                    education_meta.append(
                        duration
                    )

                if cgpa:
                    education_meta.append(
                        f"CGPA: {cgpa}"
                    )

                if education_meta:
                    st.caption(
                        " · ".join(
                            education_meta
                        )
                    )

        # ========================================================
        # CERTIFICATIONS
        # ========================================================

        certifications = resume.get(
            "certifications",
            [],
        )

        if certifications:
            st.markdown(
                "#### Certifications"
            )

            for certification in certifications:
                st.markdown(
                    f"- {certification}"
                )

        # ========================================================
        # ACHIEVEMENTS
        # ========================================================

        achievements = resume.get(
            "achievements",
            [],
        )

        if achievements:
            st.markdown(
                "#### Achievements"
            )

            for achievement in achievements:
                st.markdown(
                    f"- {achievement}"
                )


def show_generate():
    sidebar()

    page_heading(
        "Create",
        "Generate a job-specific resume.",
        "Upload your current resume and the target job description. "
        "Tell us the role you're targeting and the rest comes from "
        "your source documents.",
    )

    left, right = st.columns([0.68, 0.32])

    with right:
        st.markdown("### Pipeline")

        steps = [
            ("1", "Profile analysis", "Extract facts from your resume"),
            ("2", "ATS analysis", "Compare your profile with the job"),
            ("3", "Resume writer", "Tailor the content without fabrication"),
            ("4", "Reviewer", "Check accuracy and quality"),
        ]

        for number, title, copy in steps:
            st.markdown(
                f"""
                <div class="step">
                    <div class="step-number">{number}</div>
                    <div>
                        <div class="step-title">{title}</div>
                        <div class="step-copy">{copy}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.info(
            "Your uploaded resume is the source of truth for "
            "experience, skills, projects, education, and certifications."
        )

        st.markdown(
            """
            <div class="card">
                <div class="card-title">Privacy by design</div>
                <div class="card-subtitle">
                    We don't ask you to re-enter information already
                    contained in your resume.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with left:
        st.markdown("### 01 · Source documents")

        resume_file = st.file_uploader(
            "Current resume *",
            type=["pdf", "docx", "txt"],
            help="Upload the resume you want the AI to tailor.",
            key="resume_upload_new",
        )

        jd_file = st.file_uploader(
            "Target job description *",
            type=["pdf", "docx", "txt"],
            help="Upload the job description for the role you want.",
            key="jd_upload_new",
        )

        if resume_file:
            st.success(
                f"Resume ready · {resume_file.name}"
            )

        if jd_file:
            st.success(
                f"Job description ready · {jd_file.name}"
            )

        st.markdown("### 02 · Target role")

        company_name = st.text_input(
            "Company *",
            placeholder="Acme Corp",
            help="The company you are applying to.",
        )

        role_name = st.text_input(
            "Role / job title *",
            placeholder="Python Backend Engineer",
            help="The exact role you are targeting.",
        )

        st.markdown("### 03 · Tailoring instructions")

        notes = st.text_area(
            "Optional instructions",
            placeholder=(
                "Example: Emphasize backend engineering, "
                "highlight API work, keep the resume concise, "
                "prioritize skills relevant to this role."
            ),
            height=130,
            help=(
                "Optional guidance for tailoring. It does not override "
                "facts in your uploaded resume."
            ),
        )

        st.caption(
            "Your resume remains the source of truth. "
            "The AI must not invent skills, experience, metrics, "
            "technologies, or achievements."
        )

        target_data = {
            "company_name": company_name.strip(),
            "role_name": role_name.strip(),
            "notes": notes.strip(),
        }

        required = [
            resume_file,
            jd_file,
            target_data["company_name"],
            target_data["role_name"],
        ]

        st.divider()

        if not all(required):
            st.caption(
                "Required: current resume, job description, "
                "company, and target role."
            )

        if st.button(
            "Generate tailored resume",
            type="primary",
            use_container_width=True,
            disabled=not all(required),
        ):
            generate_resume(
                target_data,
                resume_file,
                jd_file,
            )

    if st.session_state.generation_result:
        render_results(
            st.session_state.generation_result
        )


# ============================================================
# ROUTER
# ============================================================

if st.session_state.page == "login":
    show_login()
elif st.session_state.page == "signup":
    show_signup()
elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "generate":
    show_generate()
else:
    st.session_state.page = "login"
    st.rerun()

