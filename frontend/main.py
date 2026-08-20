import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("RESUME_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

ENDPOINTS = {
    "health": "/health",
    "login": "/auth/login",
    "register": "/auth/register",
}

ROUTES = {
    "login": "login",
    "signup": "signup",
    "home": "home",
}


st.set_page_config(
    page_title="Enterprise Resume Generator",
    page_icon="",
    layout="wide",
)


SESSION_DEFAULTS = {
    "page": ROUTES["login"],
    "token": None,
    "token_type": "bearer",
    "user_email": None,
}

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

if st.session_state.page == ROUTES["home"] and not st.session_state.token:
    st.session_state.page = ROUTES["login"]


st.markdown(
    """
    <style>
        .block-container {
            max-width: 960px;
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
    </style>
    """,
    unsafe_allow_html=True,
)


def api_url(endpoint_name):
    return f"{API_BASE_URL}{ENDPOINTS[endpoint_name]}"


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


def post_to_backend(endpoint_name, payload):
    try:
        response = requests.post(
            api_url(endpoint_name),
            json=payload,
            timeout=10,
        )
    except requests.RequestException:
        return None, "Could not connect to the backend. Start FastAPI on port 8000."

    if response.ok:
        return response.json(), None

    return None, extract_error(response)


@st.cache_data(ttl=10)
def backend_is_connected():
    try:
        response = requests.get(api_url("health"), timeout=5)
    except requests.RequestException:
        return False

    return response.ok


def go_to(route_name):
    st.session_state.page = ROUTES[route_name]
    st.rerun()


def logout():
    for key, value in SESSION_DEFAULTS.items():
        st.session_state[key] = value
    st.rerun()


def render_header():
    st.markdown('<h1 class="app-title">Enterprise Resume Generator</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Sign in or create an account to continue.</div>',
        unsafe_allow_html=True,
    )


def render_backend_status():
    if backend_is_connected():
        st.caption(f"Backend connected: {API_BASE_URL}")
    else:
        st.warning(f"Backend unavailable at {API_BASE_URL}.")


def render_navbar():
    home_col, spacer_col, account_col, logout_col = st.columns([0.2, 0.42, 0.25, 0.13])

    with home_col:
        if st.button("Home", use_container_width=True, type="primary"):
            go_to("home")
    with account_col:
        st.caption(f"Signed in as {st.session_state.user_email}")
    with logout_col:
        if st.button("Logout", use_container_width=True):
            logout()

    st.divider()


def show_login():
    render_header()
    render_backend_status()

    _, center, _ = st.columns([0.25, 0.5, 0.25])
    with center:
        st.subheader("Welcome Back")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login", use_container_width=True, type="primary"):
            email = email.strip()

            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                result, error = post_to_backend(
                    "login",
                    {
                        "email": email,
                        "password": password,
                    },
                )

                if error:
                    st.error(error)
                else:
                    st.session_state.token = result["access_token"]
                    st.session_state.token_type = result.get("token_type", "bearer")
                    st.session_state.user_email = email
                    st.session_state.page = ROUTES["home"]
                    st.rerun()

        st.divider()
        st.write("Don't have an account?")

        if st.button("Create an account", use_container_width=True):
            go_to("signup")


def show_signup():
    render_header()
    render_backend_status()

    _, center, _ = st.columns([0.25, 0.5, 0.25])
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
                _, error = post_to_backend(
                    "register",
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
                    st.session_state.page = ROUTES["login"]
                    st.rerun()

        st.divider()
        st.write("Already have an account?")

        if st.button("Back to Login", use_container_width=True):
            go_to("login")


def show_home():
    render_header()
    render_navbar()
    render_backend_status()

    st.subheader("Account")
    st.write("You are logged in.")


if st.session_state.page == ROUTES["signup"]:
    show_signup()
elif st.session_state.page == ROUTES["home"]:
    show_home()
else:
    show_login()
