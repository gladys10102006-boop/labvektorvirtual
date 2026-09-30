import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import html
import streamlit.components.v1 as components

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================

st.set_page_config(
    page_title="Virtual Lab Vektor Gaya",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(59,130,246,.10), transparent 25%),
        radial-gradient(circle at 90% 20%, rgba(139,92,246,.10), transparent 25%),
        #f8fafc;
}

/* Header */

.hero {
    padding: 35px 40px;
    border-radius: 24px;
    background:
        linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #312e81 100%);
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 15px 35px rgba(15,23,42,.18);
}

.hero h1 {
    font-size: 38px;
    margin-bottom: 8px;
    font-weight: 800;
}

.hero p {
    font-size: 16px;
    color: #dbeafe;
    line-height: 1.7;
}

/* Card */

.card {
    background: white;
    border-radius: 18px;
    padding: 22px;
    margin: 10px 0;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 24px rgba(15,23,42,.06);
}

.card h3 {
    margin-top: 0;
    color: #0f172a;
}

.info-card {
    background: #eff6ff;
    border-left: 5px solid #2563eb;
    border-radius: 12px;
    padding: 18px;
    margin: 12px 0;
}

.warning-card {
    background: #fff7ed;
    border-left: 5px solid #f97316;
    border-radius: 12px;
    padding: 18px;
    margin: 12px 0;
}

.success-card {
    background: #f0fdf4;
    border-left: 5px solid #16a34a;
    border-radius: 12px;
    padding: 18px;
    margin: 12px 0;
}

/* Metric */

.metric {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(15,23,42,.05);
}

.metric-title {
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
}

.metric-value {
    color: #0f172a;
    font-size: 28px;
    font-weight: 800;
    margin-top: 7px;
}

/* Navigation */

.nav-title {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 5px;
}

.section-title {
    font-size: 27px;
    font-weight: 800;
    color: #0f172a;
    margin-top: 15px;
    margin-bottom: 8px;
}

.section-subtitle {
    color: #64748b;
    margin-bottom: 25px;
}

/* Experiment */

.lab-panel {
    background: #0f172a;
    border-radius: 22px;
    padding: 10px;
    box-shadow: 0 15px 35px rgba(15,23,42,.18);
}

.lab-caption {
    color: #cbd5e1;
    text-align: center;
    padding: 5px;
    font-size: 13px;
}

/* Footer */

.footer {
    margin-top: 50px;
    padding: 25px;
    text-align: center;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
}

.small {
    font-size: 13px;
    color: #64748b;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "page": "Beranda",
    "nama": "",
    "kelas": "",
    "pretest_score": 0,
    "posttest_score": 0,
    "hots_score": 0,
    "experiment_score": 0,
    "trials": [],
    "lab_completed": False,
    "pretest_done": False,
    "hots_done": False,
    "posttest_done": False,
    "last_measurement": 0
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# FUNGSI PERHITUNGAN
# ============================================================

G = 9.8


def force_from_mass(mass_gram):
    """
    Mengubah massa gram menjadi gaya Newton.
    F = m g
    """
    mass_kg = mass_gram / 1000
    return mass_kg * G


def calculate_resultant(forces, angles):
    """
    Menghitung komponen dan resultan beberapa vektor.
    """
    rx = 0
    ry = 0

    for force, angle in zip(forces, angles):
        rad = math.radians(angle)
        rx += force * math.cos(rad)
        ry += force * math.sin(rad)

    magnitude = math.sqrt(rx**2 + ry**2)

    angle_resultant = math.degrees(math.atan2(ry, rx))

    if angle_resultant < 0:
        angle_resultant += 360

    return rx, ry, magnitude, angle_resultant


def calculate_experiment_score():
    n = len(st.session_state.trials)

    if n == 0:
        return 0
    elif n == 1:
        return 60
    elif n == 2:
        return 70
    elif n == 3:
        return 80
    elif n == 4:
        return 90
    else:
        return 100


# ============================================================
# FUNGSI SVG LAB
# ============================================================

def create_lab_svg(
    masses,
    angles,
    forces,
    resultant,
    resultant_angle,
    animate=True
):
    """
    Membuat visualisasi SVG interaktif.
    SVG dirender menggunakan st.components.v1.html agar browser
    benar-benar menampilkan gambar, bukan source code SVG.
    """
    width = 900
    height = 560
    cx = 450
    cy = 310

    max_force = max(max(forces), 1)

    colors = ["#38bdf8", "#a78bfa", "#34d399"]
    marker_ids = ["arrowBlue", "arrowPurple", "arrowGreen"]

    animation_css = """
    <style>
        .vector-line {
            stroke-dasharray: 900;
            stroke-dashoffset: 900;
            animation: drawVector 1s ease-out forwards;
        }

        .result-line {
            stroke-dasharray: 500;
            stroke-dashoffset: 500;
            animation: drawResult 1.2s .35s ease-out forwards;
        }

        .instrument {
            transform-box: fill-box;
            transform-origin: center;
            animation: instrumentIn .7s ease-out both;
        }

        .ring {
            animation: pulseRing 1.4s ease-in-out infinite;
        }

        .measure-text {
            animation: fadeUp .7s .25s ease-out both;
        }

        @keyframes drawVector {
            to { stroke-dashoffset: 0; }
        }

        @keyframes drawResult {
            to { stroke-dashoffset: 0; }
        }

        @keyframes instrumentIn {
            from { opacity: 0; transform: scale(.75); }
            to { opacity: 1; transform: scale(1); }
        }

        @keyframes pulseRing {
            0%, 100% { opacity: 1; }
            50% { opacity: .55; }
        }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    """ if animate else "<style></style>"

    svg = f"""
    <svg width="100%" viewBox="0 0 {width} {height}"
         xmlns="http://www.w3.org/2000/svg">

        {animation_css}

        <defs>
            <linearGradient id="bgLab" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#111827"/>
                <stop offset="100%" stop-color="#020617"/>
            </linearGradient>

            <marker id="arrowBlue" markerWidth="10" markerHeight="10"
                    refX="7" refY="3" orient="auto">
                <path d="M0,0 L0,6 L8,3 z" fill="#38bdf8"/>
            </marker>

            <marker id="arrowPurple" markerWidth="10" markerHeight="10"
                    refX="7" refY="3" orient="auto">
                <path d="M0,0 L0,6 L8,3 z" fill="#a78bfa"/>
            </marker>

            <marker id="arrowGreen" markerWidth="10" markerHeight="10"
                    refX="7" refY="3" orient="auto">
                <path d="M0,0 L0,6 L8,3 z" fill="#34d399"/>
            </marker>

            <marker id="arrowResult" markerWidth="10" markerHeight="10"
                    refX="7" refY="3" orient="auto">
                <path d="M0,0 L0,6 L8,3 z" fill="#facc15"/>
            </marker>
        </defs>

        <rect width="900" height="560" rx="20" fill="url(#bgLab)"/>

        <!-- GRID -->
        <g opacity=".12" stroke="#94a3b8">
            <line x1="50" y1="310" x2="850" y2="310"/>
            <line x1="450" y1="60" x2="450" y2="510"/>
            <line x1="150" y1="60" x2="150" y2="510"/>
            <line x1="250" y1="60" x2="250" y2="510"/>
            <line x1="350" y1="60" x2="350" y2="510"/>
            <line x1="550" y1="60" x2="550" y2="510"/>
            <line x1="650" y1="60" x2="650" y2="510"/>
            <line x1="750" y1="60" x2="750" y2="510"/>
            <line x1="50" y1="210" x2="850" y2="210"/>
            <line x1="50" y1="410" x2="850" y2="410"/>
        </g>

        <!-- STATIF -->
        <line x1="100" y1="475" x2="100" y2="100"
              stroke="#94a3b8" stroke-width="10"/>
        <line x1="45" y1="475" x2="155" y2="475"
              stroke="#cbd5e1" stroke-width="14"/>
        <rect x="75" y="105" width="50" height="18" rx="5"
              fill="#64748b"/>

        <!-- CLAMP -->
        <line x1="100" y1="135" x2="210" y2="135"
              stroke="#cbd5e1" stroke-width="7"/>
        <circle cx="100" cy="135" r="14"
                fill="#475569" stroke="#e2e8f0" stroke-width="3"/>

        <!-- TITLE -->
        <text x="450" y="45" fill="#e2e8f0"
              text-anchor="middle" font-size="21" font-weight="700">
            VIRTUAL LAB — PENGUKURAN RESULTAN VEKTOR
        </text>

        <!-- BUSUR -->
        <path d="M 325 310 A 125 125 0 0 1 575 310"
              fill="none" stroke="#475569" stroke-width="2"/>
        <path d="M 350 310 A 100 100 0 0 1 550 310"
              fill="none" stroke="#334155" stroke-width="1"/>

        <line x1="450" y1="310" x2="450" y2="185"
              stroke="#64748b" stroke-width="1"/>

        <text x="450" y="174" fill="#94a3b8"
              text-anchor="middle" font-size="13">90°</text>
        <text x="585" y="320" fill="#94a3b8" font-size="13">0°</text>
        <text x="315" y="320" fill="#94a3b8" font-size="13">180°</text>

        <!-- VEKTOR DAN DINAMOMETER -->
    """

    for i, (mass, angle, force) in enumerate(zip(masses, angles, forces)):
        rad = math.radians(angle)
        visual_length = 95 + (force / max_force) * 95

        x2 = cx + visual_length * math.cos(rad)
        y2 = cy - visual_length * math.sin(rad)

        color = colors[i]
        marker = marker_ids[i]

        svg += f"""
        <g>
            <!-- tali -->
            <line x1="{cx}" y1="{cy}"
                  x2="{x2:.1f}" y2="{y2:.1f}"
                  stroke="#e2e8f0" stroke-width="2"
                  opacity=".75"/>

            <!-- vektor -->
            <line class="vector-line"
                  x1="{cx}" y1="{cy}"
                  x2="{x2:.1f}" y2="{y2:.1f}"
                  stroke="{color}" stroke-width="5"
                  marker-end="url(#{marker})"/>

            <!-- dinamometer -->
            <g class="instrument"
               transform="translate({x2:.1f},{y2:.1f}) rotate({-angle:.1f})">
                <rect x="-17" y="-42" width="34" height="65" rx="7"
                      fill="#f8fafc" stroke="{color}" stroke-width="3"/>
                <line x1="0" y1="-42" x2="0" y2="-70"
                      stroke="#cbd5e1" stroke-width="3"/>
                <circle cx="0" cy="-72" r="7" fill="none"
                        stroke="#cbd5e1" stroke-width="3"/>

                <line x1="-10" y1="-25" x2="10" y2="-25"
                      stroke="#64748b" stroke-width="2"/>
                <line x1="-10" y1="-10" x2="5" y2="-10"
                      stroke="#64748b" stroke-width="2"/>
                <line x1="-10" y1="5" x2="10" y2="5"
                      stroke="#64748b" stroke-width="2"/>
            </g>

            <!-- beban -->
            <rect x="{x2-23:.1f}" y="{y2+50:.1f}"
                  width="46" height="42" rx="7"
                  fill="#475569" stroke="#cbd5e1" stroke-width="2"/>

            <text x="{x2:.1f}" y="{y2+76:.1f}"
                  fill="white" text-anchor="middle"
                  font-size="12" font-weight="700">
                {mass:.0f} g
            </text>

            <text class="measure-text"
                  x="{x2 + 25:.1f}" y="{y2 - 12:.1f}"
                  fill="{color}" font-size="14" font-weight="700">
                F{i+1} = {force:.3f} N
            </text>

            <text class="measure-text"
                  x="{x2 + 25:.1f}" y="{y2 + 7:.1f}"
                  fill="#cbd5e1" font-size="12">
                θ = {angle:.0f}°
            </text>
        </g>
        """

    svg += f"""
        <!-- CINCIN -->
        <circle class="ring" cx="{cx}" cy="{cy}" r="25"
                fill="#f8fafc" stroke="#facc15" stroke-width="5"/>
        <circle cx="{cx}" cy="{cy}" r="9" fill="#334155"/>

        <text x="{cx}" y="{cy + 48}" fill="#facc15"
              text-anchor="middle" font-size="13" font-weight="700">
            TITIK RESULTAN
        </text>
    """

    if resultant > 0:
        rad_r = math.radians(resultant_angle)
        result_length = 145
        rx2 = cx + result_length * math.cos(rad_r)
        ry2 = cy - result_length * math.sin(rad_r)

        svg += f"""
        <!-- RESULTAN -->
        <line class="result-line"
              x1="{cx}" y1="{cy}"
              x2="{rx2:.1f}" y2="{ry2:.1f}"
              stroke="#facc15" stroke-width="6"
              marker-end="url(#arrowResult)"/>

        <text class="measure-text"
              x="{rx2:.1f}" y="{ry2-20:.1f}"
              fill="#facc15" text-anchor="middle"
              font-size="15" font-weight="800">
            R = {resultant:.3f} N
        </text>

        <text class="measure-text"
              x="{rx2:.1f}" y="{ry2+2:.1f}"
              fill="#facc15" text-anchor="middle"
              font-size="13">
            θR = {resultant_angle:.1f}°
        </text>
        """

    svg += f"""
        <!-- INFO PANEL -->
        <rect x="650" y="430" width="220" height="90" rx="14"
              fill="#111827" stroke="#334155"/>

        <text x="670" y="455" fill="#94a3b8" font-size="12">
            HASIL PENGUKURAN
        </text>

        <text x="670" y="478" fill="#f8fafc"
              font-size="20" font-weight="800">
            {resultant:.3f} N
        </text>

        <text x="670" y="501" fill="#facc15" font-size="13">
            arah {resultant_angle:.1f}°
        </text>

    </svg>
    """

    # Perbaiki marker-end yang terbentuk dari f-string di atas.
    svg = svg.replace('url(#arrowBlue)', 'url(#arrowBlue)')
    svg = svg.replace('url(#arrowPurple)', 'url(#arrowPurple)')
    svg = svg.replace('url(#arrowGreen)', 'url(#arrowGreen)')

    return svg

# ============================================================
# FUNGSI NAVIGASI
# ============================================================

def navigation():

    st.markdown(
        '<div class="nav-title">MENU VIRTUAL LAB</div>',
        unsafe_allow_html=True
    )

    pages = [
        "Beranda",
        "Identitas",
        "Petunjuk",
        "Pretest",
        "Virtual Lab",
        "Data & Grafik",
        "HOTS",
        "Posttest",
        "Hasil",
        "Hubungi Kami"
    ]

    selected = st.selectbox(
        "Pilih halaman",
        pages,
        index=pages.index(st.session_state.page)
    )

    if selected != st.session_state.page:
        st.session_state.page = selected
        st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚛️ Virtual Lab")

    navigation()

    st.divider()

    if st.session_state.nama:
        st.markdown(
            f"""
            **Peserta:**  
            {html.escape(st.session_state.nama)}
            """
        )

    st.markdown(
        """
        <div class="small">
        Praktikum Penentuan Besaran dan Arah Resultan Vektor Gaya
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# BERANDA
# ============================================================

if st.session_state.page == "Beranda":

    st.markdown(
        """
        <div class="hero">

        <h1>Virtual Lab Vektor Gaya</h1>

        <p>
        Laboratorium virtual interaktif untuk mempelajari besaran,
        arah, komponen, dan resultan dari dua atau lebih vektor gaya
        melalui simulasi praktikum.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="card">
            <h3>🔬 Eksperimen</h3>
            <p>
            Manipulasikan massa dan sudut gaya seperti pada
            praktikum menggunakan statif, dinamometer, tali,
            dan beban.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="card">
            <h3>📊 Analisis Data</h3>
            <p>
            Data percobaan dicatat otomatis dan disajikan
            dalam tabel serta grafik hubungan sudut dan
            resultan.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="card">
            <h3>🧠 HOTS</h3>
            <p>
            Peserta didik menganalisis data, mengevaluasi
            hasil eksperimen, dan merancang konfigurasi gaya.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("## Alur Praktikum")

    steps = [
        ("01", "Identitas", "Masukkan identitas peserta didik."),
        ("02", "Pretest", "Mengidentifikasi pemahaman awal."),
        ("03", "Prediksi", "Membuat dugaan sebelum eksperimen."),
        ("04", "Eksperimen", "Memanipulasi gaya dan sudut."),
        ("05", "Data", "Mengamati tabel dan grafik."),
        ("06", "HOTS", "Menganalisis dan mengevaluasi hasil."),
        ("07", "Posttest", "Mengukur pemahaman setelah eksperimen."),
        ("08", "Hasil", "Melihat hasil dan nilai praktikum.")
    ]

    cols = st.columns(4)

    for i, (number, title, desc) in enumerate(steps):

        with cols[i % 4]:

            st.markdown(
                f"""
                <div class="card">
                <b>{number} — {title}</b>
                <p class="small">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <div class="info-card">

        <b>Tujuan utama praktikum:</b>

        Peserta didik diharapkan mampu menentukan besar dan arah
        resultan dua atau lebih vektor gaya, menjelaskan pengaruh
        besar gaya dan sudut terhadap resultan, serta menggunakan
        data eksperimen untuk membuat kesimpulan.

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Mulai Praktikum →",
        type="primary",
        use_container_width=True
    ):
        st.session_state.page = "Identitas"
        st.rerun()


# ============================================================
# IDENTITAS
# ============================================================

elif st.session_state.page == "Identitas":

    st.markdown(
        '<div class="section-title">Identitas Peserta Didik</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Isi identitas sebelum memulai aktivitas praktikum.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        nama = st.text_input(
            "Nama lengkap",
            value=st.session_state.nama,
            placeholder="Masukkan nama lengkap"
        )

    with col2:

        kelas = st.text_input(
            "Kelas",
            value=st.session_state.kelas,
            placeholder="Contoh: XI IPA 1"
        )

    st.markdown(
        """
        <div class="info-card">
        Identitas digunakan untuk menampilkan hasil praktikum
        dan rekap aktivitas pada halaman hasil.
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Simpan Identitas & Lanjut →",
        type="primary"
    ):

        if nama.strip() == "" or kelas.strip() == "":
            st.error("Nama dan kelas harus diisi.")

        else:

            st.session_state.nama = nama.strip()
            st.session_state.kelas = kelas.strip()
            st.session_state.page = "Petunjuk"
            st.rerun()


# ============================================================
# PETUNJUK
# ============================================================

elif st.session_state.page == "Petunjuk":

    st.markdown(
        '<div class="section-title">Petunjuk Praktikum</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">

        <h3>Alat dan bahan virtual</h3>

        <ul>
        <li>Statif dan penjepit</li>
        <li>Dinamometer/neraca pegas 0–1,5 N</li>
        <li>Beban gantung 50 g dan 100 g</li>
        <li>Benang/tali</li>
        <li>Cincin sebagai titik pertemuan gaya</li>
        <li>Busur derajat</li>
        </ul>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">

        <h3>Konsep dasar</h3>

        Besar gaya akibat beban ditentukan menggunakan:

        <br><br>

        <b>F = m g</b>

        <br><br>

        dengan:

        <br>

        <b>F</b> = gaya (N)<br>
        <b>m</b> = massa (kg)<br>
        <b>g</b> = percepatan gravitasi (9,8 m/s²)

        <br><br>

        Komponen gaya:

        <br><br>

        <b>Fx = F cos θ</b>

        <br>

        <b>Fy = F sin θ</b>

        <br><br>

        Kemudian:

        <br><br>

        <b>Rx = ΣFx</b>

        <br>

        <b>Ry = ΣFy</b>

        <br>

        <b>R = √(Rx² + Ry²)</b>

        <br>

        <b>θR = tan⁻¹(Ry/Rx)</b>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="warning-card">

        <b>Perhatian:</b>

        Dalam simulasi, sudut diukur terhadap sumbu x positif
        dan arah berlawanan jarum jam dianggap positif.

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Lanjut ke Pretest →",
        type="primary"
    ):

        st.session_state.page = "Pretest"
        st.rerun()


# ============================================================
# PRETEST
# ============================================================

elif st.session_state.page == "Pretest":

    st.markdown(
        '<div class="section-title">Pretest</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Jawab berdasarkan pemahaman awal sebelum melakukan eksperimen.'
        '</div>',
        unsafe_allow_html=True
    )

    questions = [

        (
            "1. Besaran berikut yang termasuk besaran vektor adalah ...",
            [
                "Massa",
                "Waktu",
                "Gaya",
                "Suhu"
            ],
            2
        ),

        (
            "2. Dua gaya 2 N dan 3 N bekerja searah. Besar resultannya adalah ...",
            [
                "1 N",
                "5 N",
                "6 N",
                "0,5 N"
            ],
            1
        ),

        (
            "3. Dua gaya 5 N dan 2 N bekerja berlawanan arah. Besar resultannya adalah ...",
            [
                "7 N",
                "3 N",
                "10 N",
                "2,5 N"
            ],
            1
        ),

        (
            "4. Dua gaya masing-masing 3 N dan 4 N saling tegak lurus. Resultannya adalah ...",
            [
                "1 N",
                "5 N",
                "7 N",
                "12 N"
            ],
            1
        ),

        (
            "5. Sebuah gaya membentuk sudut 90° terhadap sumbu x positif. Arahnya berada pada ...",
            [
                "Sumbu x positif",
                "Sumbu x negatif",
                "Sumbu y positif",
                "Sumbu y negatif"
            ],
            2
        )
    ]

    answers = []

    for i, (question, options, correct) in enumerate(questions):

        answer = st.radio(
            question,
            options,
            key=f"pre_{i}"
        )

        answers.append(options.index(answer))

    if st.button(
        "Periksa Jawaban Pretest",
        type="primary"
    ):

        score = sum(
            answers[i] == questions[i][2]
            for i in range(len(questions))
        )

        st.session_state.pretest_score = round(
            score / len(questions) * 100
        )

        st.session_state.pretest_done = True

        st.success(
            f"Skor pretest: {st.session_state.pretest_score}/100"
        )

    if st.session_state.pretest_done:

        st.markdown(
            """
            <div class="info-card">

            Pretest digunakan sebagai gambaran pemahaman awal.
            Nilai pretest tidak menjadi komponen utama nilai akhir.

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Masuk ke Virtual Lab →"):

            st.session_state.page = "Virtual Lab"
            st.rerun()


# ============================================================
# VIRTUAL LAB
# ============================================================

elif st.session_state.page == "Virtual Lab":

    st.markdown(
        '<div class="section-title">Virtual Laboratory</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Manipulasikan gaya dan sudut, kemudian amati perubahan resultan.'
        '</div>',
        unsafe_allow_html=True
    )

    # ========================================================
    # PENGATURAN
    # ========================================================

    col1, col2 = st.columns([1, 2])

    with col1:

        st.markdown(
            '<div class="card"><h3>Pengaturan Percobaan</h3>',
            unsafe_allow_html=True
        )

        number_vectors = st.radio(
            "Jumlah vektor gaya",
            [2, 3],
            horizontal=True
        )

        st.markdown("#### Gaya 1")

        mass1 = st.slider(
            "Massa 1 (g)",
            50,
            150,
            100,
            step=50
        )

        angle1 = st.slider(
            "Sudut 1 (°)",
            0,
            359,
            0
        )

        st.markdown("#### Gaya 2")

        mass2 = st.slider(
            "Massa 2 (g)",
            50,
            150,
            100,
            step=50
        )

        angle2 = st.slider(
            "Sudut 2 (°)",
            0,
            359,
            90
        )

        mass3 = 50
        angle3 = 180

        if number_vectors == 3:

            st.markdown("#### Gaya 3")

            mass3 = st.slider(
                "Massa 3 (g)",
                50,
                150,
                50,
                step=50
            )

            angle3 = st.slider(
                "Sudut 3 (°)",
                0,
                359,
                180
            )

        run_experiment = st.button(
            "▶ Jalankan Percobaan",
            type="primary",
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # ========================================================
    # DATA GAYA
    # ========================================================

    forces = [
        force_from_mass(mass1),
        force_from_mass(mass2)
    ]

    angles = [
        angle1,
        angle2
    ]

    masses = [
        mass1,
        mass2
    ]

    if number_vectors == 3:

        forces.append(force_from_mass(mass3))
        angles.append(angle3)
        masses.append(mass3)

    rx, ry, resultant, resultant_angle = calculate_resultant(
        forces,
        angles
    )

    # ========================================================
    # LAB
    # ========================================================

    with col2:

        st.markdown(
            '<div class="lab-panel">',
            unsafe_allow_html=True
        )

        svg = create_lab_svg(
            masses,
            angles,
            forces,
            resultant,
            resultant_angle
        )

        # Jangan gunakan st.markdown untuk SVG mentah.
        # Streamlit dapat menampilkan source SVG sebagai teks.
        # components.html membuat browser merender SVG sebagai gambar/animasi.
        components.html(
            svg,
            height=590,
            scrolling=False
        )

        st.markdown(
            '<div class="lab-caption">'
            'Simulasi statif — dinamometer — tali — beban — '
            'cincin — busur derajat'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # ========================================================
    # HASIL SAAT INI
    # ========================================================

    st.markdown("### Hasil Perhitungan Percobaan")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Rx", f"{rx:.3f} N")

    with c2:
        st.metric("Ry", f"{ry:.3f} N")

    with c3:
        st.metric("Resultan", f"{resultant:.3f} N")

    with c4:
        st.metric("Arah Resultan", f"{resultant_angle:.1f}°")

    st.markdown(
        f"""
        <div class="info-card">
        <b>Perhitungan otomatis:</b><br>
        F = m × g → setiap massa dikonversi menjadi gaya Newton.
        Komponen dijumlahkan menjadi
        <b>Rx = {rx:.3f} N</b> dan <b>Ry = {ry:.3f} N</b>,
        kemudian diperoleh <b>R = {resultant:.3f} N</b>
        pada arah <b>{resultant_angle:.1f}°</b>.
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # TABEL GAYA
    # ========================================================

    data_force = []

    for i in range(number_vectors):

        fx = forces[i] * math.cos(
            math.radians(angles[i])
        )

        fy = forces[i] * math.sin(
            math.radians(angles[i])
        )

        data_force.append({
            "Vektor": f"F{i+1}",
            "Massa (g)": masses[i],
            "Gaya (N)": round(forces[i], 3),
            "Sudut (°)": angles[i],
            "Fx (N)": round(fx, 3),
            "Fy (N)": round(fy, 3)
        })

    df_force = pd.DataFrame(data_force)

    st.dataframe(
        df_force,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # SIMPAN PERCOBAAN
    # ========================================================

    if run_experiment:

        trial = {
            "Percobaan": len(st.session_state.trials) + 1,
            "F1 (N)": round(forces[0], 3),
            "θ1 (°)": angles[0],
            "F2 (N)": round(forces[1], 3),
            "θ2 (°)": angles[1],
            "F3 (N)": round(forces[2], 3)
            if number_vectors == 3 else 0,
            "θ3 (°)": angles[2]
            if number_vectors == 3 else 0,
            "Rx (N)": round(rx, 3),
            "Ry (N)": round(ry, 3),
            "R (N)": round(resultant, 3),
            "θR (°)": round(resultant_angle, 1)
        }

        st.session_state.trials.append(trial)
        st.session_state.last_measurement = trial["Percobaan"]

        st.session_state.experiment_score = calculate_experiment_score()

        st.success(
            f"Percobaan {trial['Percobaan']} berhasil disimpan."
        )

    # ========================================================
    # GRAFIK LIVE DI HALAMAN PRAKTIKUM
    # ========================================================
    if len(st.session_state.trials) > 0:
        st.markdown("### 📈 Grafik Live Hasil Pengukuran")
        df_live = pd.DataFrame(st.session_state.trials)

        chart_data = df_live.set_index("Percobaan")[["R (N)"]]
        st.line_chart(
            chart_data,
            use_container_width=True,
            height=280
        )

        st.caption(
            "Grafik akan bertambah setiap kali tombol "
            "'Jalankan Percobaan' ditekan."
        )

    # ========================================================
    # PETUNJUK INVESTIGASI
    # ========================================================

    st.markdown(
        """
        <div class="info-card">

        <b>Tantangan investigasi:</b>

        Lakukan minimal 5 percobaan dengan mengubah sudut antara
        gaya. Usahakan massa kedua gaya tetap sama pada beberapa
        percobaan agar pengaruh sudut terhadap resultan dapat
        dianalisis dengan lebih jelas.

        <br><br>

        Setelah data terkumpul, buka menu <b>Data & Grafik</b>.

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DATA DAN GRAFIK
# ============================================================

elif st.session_state.page == "Data & Grafik":

    st.markdown(
        '<div class="section-title">Data dan Analisis Grafik</div>',
        unsafe_allow_html=True
    )

    if len(st.session_state.trials) == 0:

        st.warning(
            "Belum ada data percobaan. Lakukan percobaan terlebih dahulu."
        )

    else:

        df = pd.DataFrame(st.session_state.trials)

        st.markdown("### Tabel Data Percobaan")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Grafik Hasil")

        fig1, ax1 = plt.subplots(figsize=(9, 4))

        ax1.plot(
            df["Percobaan"],
            df["R (N)"],
            marker="o",
            linewidth=2
        )

        ax1.set_title(
            "Hubungan Percobaan dengan Besar Resultan"
        )

        ax1.set_xlabel("Percobaan")
        ax1.set_ylabel("Resultan (N)")
        ax1.grid(True, alpha=.25)

        st.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(9, 4))

        ax2.plot(
            df["Percobaan"],
            df["Rx (N)"],
            marker="o",
            label="Rx"
        )

        ax2.plot(
            df["Percobaan"],
            df["Ry (N)"],
            marker="s",
            label="Ry"
        )

        ax2.set_title(
            "Komponen Resultan pada Setiap Percobaan"
        )

        ax2.set_xlabel("Percobaan")
        ax2.set_ylabel("Komponen gaya (N)")
        ax2.legend()
        ax2.grid(True, alpha=.25)

        st.pyplot(fig2)

        # Download

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download Data Percobaan",
            data=csv,
            file_name="data_praktikum_vektor.csv",
            mime="text/csv"
        )

        st.markdown(
            """
            <div class="info-card">

            <b>Arahkan analisis:</b>

            Perhatikan bagaimana perubahan sudut atau besar gaya
            menyebabkan perubahan nilai Rx, Ry, besar resultan,
            dan arah resultan.

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Lanjut ke Pertanyaan HOTS →",
            type="primary"
        ):

            st.session_state.page = "HOTS"
            st.rerun()


# ============================================================
# HOTS
# ============================================================

elif st.session_state.page == "HOTS":

    st.markdown(
        '<div class="section-title">Analisis HOTS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Gunakan data hasil eksperimen sebagai dasar jawaban.'
        '</div>',
        unsafe_allow_html=True
    )

    if len(st.session_state.trials) < 1:

        st.warning(
            "Lakukan minimal satu percobaan sebelum menjawab HOTS."
        )

    else:

        df = pd.DataFrame(st.session_state.trials)

        min_resultant = df["R (N)"].min()
        max_resultant = df["R (N)"].max()

        questions = [

            (
                "C4 — Analisis",
                f"""
                Berdasarkan data percobaan yang diperoleh,
                resultan terkecil yang tercatat adalah
                {min_resultant:.3f} N dan resultan terbesar
                {max_resultant:.3f} N.

                Faktor apa yang paling mungkin menyebabkan
                perubahan besar resultan tersebut?
                """,
                [
                    "Perubahan warna alat",
                    "Perubahan sudut atau besar gaya",
                    "Perubahan nama percobaan",
                    "Perubahan satuan waktu"
                ],
                1
            ),

            (
                "C4 — Analisis",
                """
                Jika dua gaya memiliki besar yang sama dan
                sudut antara keduanya semakin mendekati 180°,
                bagaimana kecenderungan besar resultannya?
                """,
                [
                    "Semakin besar",
                    "Cenderung semakin kecil",
                    "Selalu tetap",
                    "Tidak dapat berubah"
                ],
                1
            ),

            (
                "C5 — Evaluasi",
                """
                Dalam percobaan nyata, hasil pengukuran dapat
                berbeda sedikit dari hasil perhitungan teoritis.
                Penyebab yang paling masuk akal adalah ...
                """,
                [
                    "Kesalahan pembacaan alat dan ketidakidealan tali",
                    "Resultan tidak memiliki arah",
                    "Gaya tidak dapat dijumlahkan",
                    "Sudut tidak berpengaruh terhadap gaya"
                ],
                0
            ),

            (
                "C5 — Evaluasi",
                """
                Seorang siswa mengatakan bahwa dua gaya selalu
                menghasilkan resultan yang lebih besar daripada
                masing-masing gaya. Apakah pernyataan tersebut benar?
                """,
                [
                    "Benar untuk semua sudut",
                    "Benar hanya jika gaya tegak lurus",
                    "Tidak selalu; bergantung pada besar dan arah gaya",
                    "Tidak ada hubungan antara gaya dan resultan"
                ],
                2
            ),

            (
                "C6 — Kreasi",
                """
                Jika kamu diminta membuat konfigurasi gaya dengan
                resultan mendekati nol, konfigurasi yang paling
                tepat adalah ...
                """,
                [
                    "Gaya-gaya sama besar dan arahnya berlawanan",
                    "Semua gaya searah",
                    "Semua gaya membentuk sudut 90°",
                    "Hanya menggunakan satu gaya"
                ],
                0
            )
        ]

        user_answers = []

        for i, (level, question, options, correct) in enumerate(
            questions
        ):

            st.markdown(
                f"### {level}"
            )

            st.write(question)

            answer = st.radio(
                f"Jawaban {i+1}",
                options,
                key=f"hots_{i}"
            )

            user_answers.append(
                options.index(answer)
            )

        if st.button(
            "Periksa Jawaban HOTS",
            type="primary"
        ):

            correct_count = sum(
                user_answers[i] == questions[i][3]
                for i in range(len(questions))
            )

            st.session_state.hots_score = round(
                correct_count / len(questions) * 100
            )

            st.session_state.hots_done = True

            st.success(
                f"Skor HOTS: {st.session_state.hots_score}/100"
            )

        if st.session_state.hots_done:

            if st.button("Lanjut ke Posttest →"):

                st.session_state.page = "Posttest"
                st.rerun()


# ============================================================
# POSTTEST
# ============================================================

elif st.session_state.page == "Posttest":

    st.markdown(
        '<div class="section-title">Posttest</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Kerjakan setelah menyelesaikan aktivitas virtual lab.'
        '</div>',
        unsafe_allow_html=True
    )

    questions = [

        (
            "1. Dua gaya 0,98 N dan 0,98 N saling tegak lurus. "
            "Besar resultannya mendekati ...",
            [
                "0,98 N",
                "1,39 N",
                "1,96 N",
                "0 N"
            ],
            1
        ),

        (
            "2. Dua gaya sama besar bekerja berlawanan arah. "
            "Resultannya adalah ...",
            [
                "Dua kali gaya",
                "Setengah gaya",
                "Nol",
                "Tidak dapat ditentukan"
            ],
            2
        ),

        (
            "3. Gaya 1 N pada 30° dan gaya 1 N pada 150° bekerja "
            "bersamaan. Arah resultannya adalah ...",
            [
                "0°",
                "45°",
                "90°",
                "180°"
            ],
            2
        ),

        (
            "4. Gaya 0,98 N pada 0° dan gaya 0,49 N pada 180°. "
            "Besar resultannya adalah ...",
            [
                "0,49 N",
                "1,47 N",
                "0,98 N",
                "0 N"
            ],
            0
        ),

        (
            "5. Dua gaya yang sama besar dapat menghasilkan resultan "
            "yang arahnya 45° jika kedua gaya berada pada arah ...",
            [
                "0° dan 90°",
                "0° dan 180°",
                "90° dan 180°",
                "180° dan 270°"
            ],
            0
        )
    ]

    answers = []

    for i, (question, options, correct) in enumerate(questions):

        answer = st.radio(
            question,
            options,
            key=f"post_{i}"
        )

        answers.append(
            options.index(answer)
        )

    if st.button(
        "Periksa Posttest",
        type="primary"
    ):

        correct_count = sum(
            answers[i] == questions[i][2]
            for i in range(len(questions))
        )

        st.session_state.posttest_score = round(
            correct_count / len(questions) * 100
        )

        st.session_state.posttest_done = True

        st.success(
            f"Skor posttest: {st.session_state.posttest_score}/100"
        )

    if st.session_state.posttest_done:

        if st.button(
            "Lihat Hasil Praktikum →",
            type="primary"
        ):

            st.session_state.page = "Hasil"
            st.rerun()


# ============================================================
# HASIL
# ============================================================

elif st.session_state.page == "Hasil":

    st.markdown(
        """
        <div class="hero">

        <h1>Hasil Praktikum</h1>

        <p>
        Rekapitulasi aktivitas Virtual Lab Vektor Gaya
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    experiment_score = calculate_experiment_score()

    final_score = round(
        0.35 * experiment_score
        + 0.35 * st.session_state.hots_score
        + 0.30 * st.session_state.posttest_score
    )

    st.session_state.experiment_score = experiment_score

    # ========================================================
    # IDENTITAS
    # ========================================================

    st.markdown(
        f"""
        <div class="card">

        <h3>Peserta Didik</h3>

        <b>Nama:</b> {html.escape(st.session_state.nama)}<br>
        <b>Kelas:</b> {html.escape(st.session_state.kelas)}<br>
        <b>Jumlah percobaan:</b> {len(st.session_state.trials)}

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # NILAI
    # ========================================================

    c1, c2, c3, c4, c5 = st.columns(5)

    metrics = [
        ("Pretest", st.session_state.pretest_score),
        ("Eksperimen", experiment_score),
        ("HOTS", st.session_state.hots_score),
        ("Posttest", st.session_state.posttest_score),
        ("Nilai Akhir", final_score)
    ]

    for col, (title, value) in zip(
        [c1, c2, c3, c4, c5],
        metrics
    ):

        with col:

            st.markdown(
                f"""
                <div class="metric">

                <div class="metric-title">
                {title}
                </div>

                <div class="metric-value">
                {value}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    # ========================================================
    # STATUS
    # ========================================================

    if final_score >= 80:

        status = "Sangat Baik"

    elif final_score >= 70:

        status = "Baik"

    elif final_score >= 60:

        status = "Cukup"

    else:

        status = "Perlu Penguatan"

    st.markdown(
        f"""
        <div class="success-card">

        <h3>Status Pembelajaran: {status}</h3>

        Nilai akhir diperoleh dari:

        <br><br>

        Eksperimen 35% + HOTS 35% + Posttest 30%.

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # GRAFIK
    # ========================================================

    if len(st.session_state.trials) > 0:

        df = pd.DataFrame(
            st.session_state.trials
        )

        st.markdown("### Perkembangan Hasil Eksperimen")

        fig, ax = plt.subplots(
            figsize=(10, 4)
        )

        ax.plot(
            df["Percobaan"],
            df["R (N)"],
            marker="o",
            linewidth=2
        )

        ax.set_xlabel("Percobaan")
        ax.set_ylabel("Resultan (N)")
        ax.set_title(
            "Perubahan Besar Resultan"
        )

        ax.grid(True, alpha=.25)

        st.pyplot(fig)

        # ====================================================
        # KESIMPULAN OTOMATIS
        # ====================================================

        average_resultant = df["R (N)"].mean()

        st.markdown(
            f"""
            <div class="card">

            <h3>Kesimpulan Otomatis</h3>

            Berdasarkan {len(df)} percobaan yang dilakukan,
            diperoleh rata-rata besar resultan sebesar
            <b>{average_resultant:.3f} N</b>.

            Hasil eksperimen menunjukkan bahwa resultan vektor
            tidak hanya ditentukan oleh besar gaya, tetapi juga
            oleh arah dan sudut antara gaya-gaya yang bekerja.
            Ketika arah gaya berubah, komponen pada sumbu x
            dan y juga berubah sehingga besar serta arah resultan
            dapat berubah.

            </div>
            """,
            unsafe_allow_html=True
        )

    # ========================================================
    # DOWNLOAD REKAP
    # ========================================================

    recap = pd.DataFrame({

        "Komponen Penilaian": [
            "Pretest",
            "Eksperimen",
            "HOTS",
            "Posttest",
            "Nilai Akhir"
        ],

        "Nilai": [
            st.session_state.pretest_score,
            experiment_score,
            st.session_state.hots_score,
            st.session_state.posttest_score,
            final_score
        ]
    })

    csv_recap = recap.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇ Simpan Rekap Nilai",
        data=csv_recap,
        file_name="rekap_virtual_lab_vektor.csv",
        mime="text/csv"
    )

    if st.button(
        "🔬 Kembali ke Virtual Lab"
    ):

        st.session_state.page = "Virtual Lab"
        st.rerun()


# ============================================================
# HUBUNGI KAMI
# ============================================================

elif st.session_state.page == "Hubungi Kami":

    st.markdown(
        '<div class="section-title">Hubungi Kami</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
        Tim pengembang Virtual Lab Vektor Gaya
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    names = [
        "Gladys Putri Ferica",
        "Nurmaretta Tambunan",
        "Sazkia Amrina Haurissa"
    ]

    for col, name in zip(
        [col1, col2, col3],
        names
    ):

        with col:

            st.markdown(
                f"""
                <div class="card" style="text-align:center;">

                <div style="font-size:40px;">
                👩‍🔬
                </div>

                <h3>{name}</h3>

                <p class="small">
                Tim Pengembang Virtual Lab
                </p>

                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <div class="info-card">

        <b>Tentang aplikasi</b>

        <br><br>

        Virtual Lab Vektor Gaya dikembangkan sebagai media
        pembelajaran fisika yang memungkinkan peserta didik
        melakukan investigasi terhadap hubungan antara besar
        gaya, arah gaya, komponen vektor, dan resultan melalui
        lingkungan eksperimen virtual.

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

    <b>Virtual Lab Vektor Gaya</b><br>

    Media pembelajaran fisika berbasis eksperimen virtual<br>

    <span class="small">
    Inkuiri Terbimbing • HOTS • Analisis Data
    </span>

    </div>
    """,
    unsafe_allow_html=True
)