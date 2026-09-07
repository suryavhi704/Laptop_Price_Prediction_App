import streamlit as st
import pickle
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Laptop Price Estimator",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Styling — matches the spec-sheet / blueprint look, layered on top of the
# .streamlit/config.toml theme. Pure CSS, no behaviour changes.
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
}

#MainMenu, footer, header {visibility: hidden;}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1180px;
}

.app-header h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 2.1rem;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}

.app-header p {
    color: #8b93a3;
    font-size: 0.92rem;
    margin-top: 0;
}

.panel-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    margin: 0 0 0.6rem 2px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #161a22;
    border: 1px solid #2a3140 !important;
    border-radius: 10px !important;
}

label, .stMarkdown p {
    font-size: 0.78rem !important;
    color: #8b93a3 !important;
}

.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input {
    background-color: #1b202b !important;
    border: 1px solid #2a3140 !important;
    border-radius: 7px !important;
    color: #e7eaf0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.86rem !important;
}

div[role="radiogroup"] {
    gap: 6px;
}

div[role="radiogroup"] label {
    background: #1b202b;
    border: 1px solid #2a3140;
    border-radius: 7px;
    padding: 6px 14px !important;
    margin: 0 !important;
}

.stSlider [data-baseweb="slider"] {
    padding-top: 6px;
}

.stButton > button {
    width: 100%;
    background: #5b8def;
    color: #0c0e13;
    border: none;
    border-radius: 7px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    padding: 0.65rem 0;
    transition: background 0.15s ease;
}

.stButton > button:hover {
    background: #6f9bf3;
    color: #0c0e13;
}

.spec-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #232a37;
    font-size: 0.8rem;
}

.spec-row span:first-child { color: #545e70; }
.spec-row span:last-child { color: #e7eaf0; }

.price-label {
    font-size: 0.72rem;
    color: #8b93a3;
    margin-top: 18px;
    margin-bottom: 6px;
    display: block;
}

.price-value {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 2.3rem;
    color: #ffb454;
}

.price-placeholder {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 400;
    font-size: 1.4rem;
    color: #545e70;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Model + data — unchanged from the original app
# ---------------------------------------------------------------------------
pipe = pickle.load(open('pipe.pkl', 'rb'))
df = pickle.load(open('df.pkl', 'rb'))

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="app-header"><h1>Laptop price estimator</h1>'
    '<p>Configure a build below and get a price estimate from the trained model.</p></div>',
    unsafe_allow_html=True,
)

left, right = st.columns([1.15, 0.85], gap="large")

# ---------------------------------------------------------------------------
# LEFT — configure panel (same widgets, same variable names as the original)
# ---------------------------------------------------------------------------
with left:
    st.markdown('<div class="panel-title">Configure</div>', unsafe_allow_html=True)
    with st.container(border=True):

        c1, c2 = st.columns(2)
        with c1:
            company = st.selectbox('Brand', df['Company'].unique())
        with c2:
            type = st.selectbox('Type', df['TypeName'].unique())

        c3, c4 = st.columns(2)
        with c3:
            ram = st.selectbox('RAM(in GB)', [2, 4, 6, 8, 12, 16, 24, 32, 64])
        with c4:
            weight = st.number_input('Weight of the Laptop', min_value=0.0, value=2.1, step=0.1)

        c5, c6 = st.columns(2)
        with c5:
            touchscreen = st.radio('Touchscreen', ['No', 'Yes'], horizontal=True)
        with c6:
            ips = st.radio('IPS', ['No', 'Yes'], horizontal=True)

        screen_size = st.slider(
            'Screen size in inches',
            min_value=10.0,
            max_value=18.0,
            value=13.0,
            step=0.1,
            format="%.1f"
        )

        resolution = st.selectbox(
            'Screen Resolution',
            ['1920x1080', '1366x768', '1600x900', '3840x2160', '3200x1800',
             '2880x1800', '2560x1600', '2560x1440', '2304x1440']
        )

        c7, c8 = st.columns(2)
        with c7:
            cpu = st.selectbox('CPU', df['Cpu brand'].unique())
        with c8:
            gpu = st.selectbox('GPU', df['Gpu brand'].unique())

        c9, c10 = st.columns(2)
        with c9:
            hdd = st.selectbox('HDD(in GB)', [0, 128, 256, 512, 1024, 2048])
        with c10:
            ssd = st.selectbox('SSD(in GB)', [0, 8, 128, 256, 512, 1024])

        os = st.selectbox('OS', df['os'].unique())

        predict_clicked = st.button('Predict Price', use_container_width=True)

# ---------------------------------------------------------------------------
# RIGHT — live spec sheet + price (Streamlit reruns on every widget change,
# so this reflects the current selections automatically, no extra JS needed)
# ---------------------------------------------------------------------------
with right:
    st.markdown('<div class="panel-title">Spec sheet</div>', unsafe_allow_html=True)
    with st.container(border=True):

        x_res, y_res = int(resolution.split('x')[0]), int(resolution.split('x')[1])
        ppi_preview = ((x_res ** 2) + (y_res ** 2)) ** 0.5 / screen_size

        storage_bits = []
        if ssd > 0:
            storage_bits.append(f"{ssd} GB SSD")
        if hdd > 0:
            storage_bits.append(f"{hdd} GB HDD")
        storage_text = " + ".join(storage_bits) if storage_bits else "None"

        rows = [
            ("Brand", company),
            ("Type", type),
            ("RAM", f"{ram} GB"),
            ("Weight", f"{weight:.2f} kg"),
            ("Touchscreen", touchscreen),
            ("IPS panel", ips),
            ("Display", f'{screen_size:.1f}" · {resolution}'),
            ("Pixel density", f"{ppi_preview:.1f} ppi"),
            ("CPU", cpu),
            ("GPU", gpu),
            ("Storage", storage_text),
            ("OS", os),
        ]
        rows_html = "".join(
            f'<div class="spec-row"><span>{label}</span><span>{value}</span></div>'
            for label, value in rows
        )
        st.markdown(rows_html, unsafe_allow_html=True)

        st.markdown('<span class="price-label">Estimated price</span>', unsafe_allow_html=True)

        if predict_clicked:
            # ---- prediction logic, unchanged from the original app ----
            touchscreen_val = 1 if touchscreen == 'Yes' else 0
            ips_val = 1 if ips == 'Yes' else 0

            X_res = int(resolution.split('x')[0])
            Y_res = int(resolution.split('x')[1])
            ppi = ((X_res ** 2) + (Y_res ** 2)) ** 0.5 / screen_size # PPI= pixels per inch

            query = pd.DataFrame({
                'Company': [company],
                'TypeName': [type],
                'Ram': [ram],
                'Weight': [weight],
                'Touchscreen': [touchscreen_val],
                'Ips': [ips_val],
                'ppi': [ppi],
                'Cpu brand': [cpu],
                'HDD': [hdd],
                'SSD': [ssd],
                'Gpu brand': [gpu],
                'os': [os]
            })

            prediction = pipe.predict(query)[0]
            st.session_state['last_price'] = int(prediction)

        if 'last_price' in st.session_state:
            price_str = f"{st.session_state['last_price']:,}"
            st.markdown(f'<div class="price-value">&#8377;{price_str}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="price-placeholder">— — —</div>', unsafe_allow_html=True)