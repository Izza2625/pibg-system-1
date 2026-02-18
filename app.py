import streamlit as st
import base64
from datetime import datetime
import pytz

def set_bg_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                linear-gradient(rgba(60,0,0,0.45), rgba(60,0,0,0.45)),
                url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        /* Blur gelap supaya teks jelas */
        .login-box {{
            background: rgba(43, 0, 0, 0.75);
            padding: 40px;
            border-radius: 15px;
            max-width: 450px;
            margin: auto;
            box-shadow: 0px 0px 30px rgba(0,0,0,0.7);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ===============================
# IMPORT SCREEN
# ===============================
from screens import (
    halaman_utama,
    senarai_perbelanjaan,
    baucar_bayaran,
    senarai_nama, 
    lain_lain_pendapatan,         
    penyata,
    permohonan,
)

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="MyPIBGkvks",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================
# MASA MALAYSIA (BM)
# ===============================
tz = pytz.timezone("Asia/Kuala_Lumpur")
now = datetime.now(tz)

hari_map = {
    "Monday": "Isnin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Khamis", "Friday": "Jumaat",
    "Saturday": "Sabtu", "Sunday": "Ahad"
}

bulan_map = {
    "January": "Januari", "February": "Februari", "March": "Mac",
    "April": "April", "May": "Mei", "June": "Jun", "July": "Julai",
    "August": "Ogos", "September": "September",
    "October": "Oktober", "November": "November", "December": "Disember"
}

papar_masa = (
    f"{hari_map[now.strftime('%A')]}, "
    f"{now.strftime('%d')} "
    f"{bulan_map[now.strftime('%B')]} "
    f"{now.strftime('%Y')} | "
    f"{now.strftime('%I:%M %p')}"
)

# ===============================
# SESSION STATE
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "Halaman Utama"

# ===============================
# LOGIN PAGE
# ===============================
if not st.session_state.logged_in:
    set_bg_image("assets/bg.jpg")
    st.markdown("""
    <style>

    /* Semua teks login putih */
    h1, h2, h3, h4, h5, h6,
    label, p, span {
        color: white !important;
    }

    /* Teks yang ditaip dalam input = HITAM */
    .stTextInput input {
        color: #000000 !important;
    }

    /* Placeholder kelabu */
    .stTextInput input::placeholder {
        color: #555 !important;
    }

    /* Icon mata putih */
    [data-testid="stPasswordInput"] svg {
        fill: white !important;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>

    /* BUTANG LOG MASUK - MERAH SAMA LOGIN BOX */
    div.stButton > button {
        background: rgba(43, 0, 0, 0.85) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
    }

    /* Hover effect */
    div.stButton > button:hover {
        background: rgba(60, 0, 0, 0.95) !important;
    }

    </style>
    """, unsafe_allow_html=True)
   
    st.markdown("""
    <style>

    /* Tulisan yang ditaip dalam kotak = HITAM */
    input {
        color: #000000 !important;
    }

    /* Placeholder (contoh: Nama Pengguna) */
    input::placeholder {
        color: #555555 !important;
    }

    /* Warna icon mata sahaja (tak duplicate) */
    [data-testid="stPasswordInput"] button svg {
        fill: white !important;
    }

    /* Jangan duplicate icon */
    button[data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="login-box">
        <h1 style="text-align:center;">MyPIBGkvks</h1>
        <h3 style="
            text-align:center;
            white-space: nowrap;
            font-size: 22px;
            margin-top: 5px;
        ">
            Kolej Vokasional Kuala Selangor
        </h3>        
        <p style="text-align:center;">{papar_masa}</p>
        <br>
        """, unsafe_allow_html=True)

        user = st.text_input("Nama Pengguna")
        pwd = st.text_input("Kata Laluan", type="password")

        if st.button("Log Masuk"):
            if user == "AIZATUL ASYIKIN BINTI TAJUL ARIFFIN" and pwd == "Pibg#123":
                st.session_state.logged_in = True
                st.session_state.current_page = "Halaman Utama"
                st.rerun()
            else:
                st.error("Nama pengguna atau kata laluan salah.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ===============================
# THEME DALAM SISTEM (PUTIH + MERAH)
# ===============================
st.markdown("""
<style>

/* ================= BACKGROUND DALAM ================= */
.stApp {
    background-color: #FFFFFF;
}

/* ================= SIDEBAR ================= */
section[data-testid="stSidebar"] {
    background-color: #F6EFEF;
}

/* ================= BUTTON ================= */
.stButton>button {
    background: linear-gradient(180deg, #B30000, #7A0000);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
}
.stButton>button:hover {
    background: linear-gradient(180deg, #D00000, #8B0000);
}

/* Expander header jadi merah */
details summary {
    background-color: #8B0000 !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 8px 12px !important;
}

/* Hover expander */
details summary:hover {
    background-color: #6E0000 !important;
}

/* Semua jenis button merah */
button[kind="secondary"],
button[kind="primary"],
.stButton>button,
.stDownloadButton>button {
    background-color: #8B0000 !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
}

button:hover {
    background-color: #6E0000 !important;
}

/* ================= INPUT / FORM ================= */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
textarea {
    background: #F3DCDC !important;   /* merah lembut */
    color: #4A0000 !important;
    border-radius: 10px !important;
    border: 1px solid #C99999 !important;
}

/* ================= SELECTBOX ================= */
.stSelectbox div[data-baseweb="select"] {
    background: #F3DCDC !important;
    border-radius: 10px !important;
}

/* ================= EXPANDER ================= */
.streamlit-expanderHeader {
    background: #8B0000;
    color: white;
    border-radius: 10px;
}

/* ================= CARD MERAH ================= */
.red-card {
    background: linear-gradient(180deg, #B30000, #7A0000);
    color: white;
    border-radius: 14px;
    padding: 15px;
}

/* ================= TAJUK ================= */
h1, h2, h3 {
    color: #5B0F0F;
}

</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR MENU
# ===============================
with st.sidebar:
    st.markdown("## MyPIBGkvks")

    if st.button("Halaman Utama"):
        st.session_state.current_page = "Halaman Utama"

    with st.expander("Perbelanjaan"):
        if st.button("Senarai Perbelanjaan"):
            st.session_state.current_page = "Senarai Perbelanjaan"
        if st.button("Baucar Bayaran"):
            st.session_state.current_page = "Baucar Bayaran"

    with st.expander("Pendapatan"):
        if st.button("Senarai Nama"):
            st.session_state.current_page = "Senarai Nama"
        if st.button("Lain-Lain Pendapatan"):
            st.session_state.current_page = "Lain-Lain Pendapatan"

    if st.button("Penyata Pendapatan & Perbelanjaan"):
        st.session_state.current_page = "Penyata"

    if st.button("Maklumat Permohonan"):
        st.session_state.current_page = "Maklumat Permohonan"

# ===============================
# PAPAR HALAMAN
# ===============================
page = st.session_state.current_page

if page == "Halaman Utama":
    halaman_utama.render()

elif page == "Senarai Perbelanjaan":
    senarai_perbelanjaan.render()

elif page == "Baucar Bayaran":
    baucar_bayaran.render()

elif page == "Senarai Nama":
    senarai_nama.render()      # ✅ INI YANG PENTING

elif page == "Lain-Lain Pendapatan":
    lain_lain_pendapatan.render()

elif page == "Penyata":
    penyata.render()

elif page == "Maklumat Permohonan":
    permohonan.render()
