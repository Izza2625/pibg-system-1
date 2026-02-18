import streamlit as st
import pandas as pd
import os, io, base64
from datetime import date

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors

st.markdown("""
<style>

/* ===== SEMUA BUTTON DALAM FORM ===== */
div[data-testid="stForm"] button,
div.stButton > button,
button[kind="primaryFormSubmit"],
button[kind="secondaryFormSubmit"] {
    background-color: #c00000 !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 600 !important;
}

/* HOVER */
div[data-testid="stForm"] button:hover,
div.stButton > button:hover,
button[kind="primaryFormSubmit"]:hover,
button[kind="secondaryFormSubmit"]:hover {
    background-color: #8b0000 !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# KONFIGURASI
# ======================================================
DATA_DIR = "data/lain_lain_pendapatan"
TAHUN_OPTIONS = list(range(2025,2050))
KAEDAH_OPTIONS = ["SILA PILIH", "Tunai", "Bank"]

CSV_COLUMNS = ["Tarikh", "Perkara", "Jumlah", "Kaedah", "Catatan"]

# ======================================================
# UTILITI FAIL
# ======================================================
def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def csv_path(tahun):
    return os.path.join(DATA_DIR, f"pendapatan_{tahun}.csv")

def load_data(tahun):
    ensure_dir()

    if os.path.exists(csv_path(tahun)):
        df = pd.read_csv(csv_path(tahun))
    else:
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(csv_path(tahun), index=False)
        return df

    # =========================
    # AUTO BETULKAN KOLUMN LAMA
    # =========================
    if "Jumlah" in df.columns:
        df.rename(columns={"Jumlah": "Jumlah"}, inplace=True)

    # Pastikan semua kolum wujud
    for col in CSV_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df

def save_data(tahun, df):
    df.to_csv(csv_path(tahun), index=False)

# ======================================================
# PDF
# ======================================================
def generate_pdf(tahun, df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "title",
        fontSize=18,
        alignment=1,
        fontName="Helvetica-Bold",
        spaceAfter=14
    )

    header = ParagraphStyle(
        "header",
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=colors.white,
        alignment=1
    )

    cell = ParagraphStyle(
        "cell",
        fontSize=8
    )

    elements = []
    elements.append(Paragraph(f"LAIN-LAIN PENDAPATAN {tahun}", title))

    table_data = [[
        Paragraph("BIL", header),
        Paragraph("TARIKH", header),
        Paragraph("PERKARA", header),
        Paragraph("Jumlah", header),
        Paragraph("KAEDAH", header),
        Paragraph("CATATAN", header),
    ]]

    jumlah_akhir = df["Jumlah"].astype(float).sum()
    
    for i, r in df.iterrows():
        catatan_text = str(r["Catatan"]) if pd.notna(r["Catatan"]) else ""
        catatan_text = catatan_text.replace("\n", "<br/>")
        table_data.append([
            Paragraph(str(i + 1), cell),
            Paragraph(r["Tarikh"], cell),
            Paragraph(r["Perkara"], cell),
            Paragraph(f"{float(r['Jumlah']):,.2f}", cell),
            Paragraph(r["Kaedah"], cell),
            Paragraph(catatan_text, cell),
        ])

    table_data.append([
        "",
        "",
        Paragraph("<b>JUMLAH AKHIR</b>", cell),
        Paragraph(f"<b>RM {jumlah_akhir:,.2f}</b>", cell),
        "",
        ""
    ])
    
    table = Table(
        table_data,
        colWidths=[40, 80, 220, 80, 200],
        repeatRows=1
    )


    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("ALIGN", (0,0), (-1,0), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
    ]))

    elements.append(table)
    doc.build(elements)

    return buffer.getvalue()
    
# ======================================================
# MAIN
# ======================================================
def render():
    st.markdown("## LAIN-LAIN PENDAPATAN")
    if "mode" not in st.session_state:
        st.session_state.mode = "view"
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = None
    if "selected_index" not in st.session_state:
        st.session_state.selected_index = None

    tahun = st.selectbox("Pilih Tahun", TAHUN_OPTIONS)
    df = load_data(tahun)
    pilih = pd.DataFrame()
    
    # ================= BUTANG ATAS =================
    sp1, col1, sp2, col2, sp3, col3, sp4, col4, sp5 = st.columns(
        [1, 2, 1, 2, 1, 2, 1, 2, 1]
    )

    # TAMBAH
    if col1.button("TAMBAH"):
        st.session_state.mode = "add"
        st.session_state.edit_index = None

    # EDIT
    if col2.button("EDIT"):
        if st.session_state.selected_index is None:
            st.warning("Sila pilih SATU rekod untuk edit.")
        else:
            st.session_state.edit_index = st.session_state.selected_index
            st.session_state.mode = "edit"

    # PADAM
    if col3.button("PADAM"):
        if st.session_state.selected_index is None:
            st.warning("Sila pilih SATU rekod untuk padam.")
        else:
            st.session_state.confirm_delete = st.session_state.selected_index

    # CETAK
    if col4.button("MENCETAK"):
        pdf = generate_pdf(tahun, df)
        b64 = base64.b64encode(pdf).decode()
        st.components.v1.html(f"""
        <script>
        var a=document.createElement("a");
        a.href="data:application/pdf;base64,{b64}";
        a.download="lain_lain_pendapatan_{tahun}.pdf";
        a.click();
        </script>
        """, height=0)

    # ================= PAPAR JADUAL =================
    df_view = df.copy()
    if "Jumlah" in df_view.columns:
        df_view["Jumlah"] = (
            pd.to_numeric(df_view["Jumlah"], errors="coerce")
            .fillna(0)
            .apply(lambda x: f"RM {x:,.2f}")
        )
    df_view.insert(0, "Pilih", False)

    edited = st.data_editor(
        df_view,
        hide_index=True,
        disabled=[c for c in df_view.columns if c != "Pilih"]
    )

    pilih = edited[edited["Pilih"] == True]
    st.session_state.selected_index = pilih.index[0] if len(pilih) == 1 else None



    edit_index = st.session_state.get("edit_index")
    tarikh_d, perkara_d, Jumlah_d, kaedah_d, catatan_d = date.today(), "", 0.0, "SILA PILIH", ""

    if edit_index is not None and edit_index < len(df):
        r = df.loc[edit_index]
        tarikh_d = pd.to_datetime(r["Tarikh"]).date()
        perkara_d = r["Perkara"]
        Jumlah_d = float(r["Jumlah"])
        kaedah_d = r["Kaedah"]
        catatan_d = r["Catatan"]

    # ================= CONFIRM PADAM =================
    if "confirm_delete" in st.session_state:
        st.warning("Anda pasti mahu padam rekod ini?")
        y, n = st.columns(2)
        if y.button("YA, PADAM"):
            df = df.drop(st.session_state.confirm_delete).reset_index(drop=True)
            save_data(tahun, df)
            del st.session_state.confirm_delete
            st.rerun()
        if n.button("BATAL"):
            del st.session_state.confirm_delete

    # ================= FORM TAMBAH / EDIT =================
    if st.session_state.mode in ["add", "edit"]:

        # nilai default
        tarikh_d, perkara_d, Jumlah_d, kaedah_d, catatan_d = (
            date.today(), "", 0.0, "SILA PILIH", ""
        )

        # kalau edit, ambil data asal
        if st.session_state.edit_index is not None:
            r = df.loc[st.session_state.edit_index]
            tarikh_d = pd.to_datetime(r["Tarikh"]).date()
            perkara_d = r["Perkara"]
            Jumlah_d = float(r["Jumlah"])
            kaedah_d = r["Kaedah"]
            catatan_d = r["Catatan"]

        with st.form("form_pendapatan"):

            tarikh = st.date_input("Tarikh", value=tarikh_d)
            perkara = st.text_input("Perkara", value=perkara_d)
            Jumlah = st.number_input(
                "Jumlah (RM)",
                min_value=0.0,
                value=Jumlah_d,
                format="%.2f"
            )
            kaedah = st.selectbox(
                "Kaedah Penerimaan",
                KAEDAH_OPTIONS,
                index=KAEDAH_OPTIONS.index(kaedah_d)
            )
            catatan = st.text_area("Catatan", value=catatan_d)
            
            st.checkbox(
                "TERUSKAN DENGAN TRANSAKSI SETERUSNYA",
                key="auto_next_lain"
            )

            col_simpan, col_batal = st.columns(2)

            with col_simpan:
                submit = st.form_submit_button("SIMPAN", type="primary")

            with col_batal:
                cancel = st.form_submit_button("BATAL", type="primary")

            # ===== SIMPAN =====
            if submit:
                if not perkara or kaedah == "SILA PILIH" or Jumlah <= 0:
                    st.error("Sila lengkapkan semua maklumat.")
                    st.stop()

                row = [
                    tarikh.strftime("%Y-%m-%d"),
                    perkara.upper(),
                    Jumlah,
                    kaedah,
                    catatan
                ]

                if st.session_state.mode == "edit":
                    df.loc[st.session_state.edit_index] = row
                else:
                    df.loc[len(df)] = row

                save_data(tahun, df)

                # ===== AUTO NEXT =====
                if st.session_state.auto_next_lain:
                    st.session_state.mode = "add"
                    st.session_state.edit_index = None
                else:
                    st.session_state.mode = "view"
                    st.session_state.edit_index = None

                st.rerun()

            # ===== BATAL =====
            if cancel:
                st.session_state.mode = "view"
                st.session_state.edit_index = None
                st.rerun()
    
    # ================= JUMLAH AKHIR =================
    if "Jumlah" in df.columns:
        jumlah_akhir = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0).sum()
    else:
        jumlah_akhir = 0
    st.markdown(f"#### Jumlah Akhir: RM {jumlah_akhir:,.2f}")

        