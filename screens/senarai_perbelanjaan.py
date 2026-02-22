import streamlit as st
import pandas as pd
import os
import io
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_ID = "11O-b8ZvpqK0uYhARIzQ4uINdYfoYkPjyl7JRGQ5TDts"
# =============== IMPORT UNTUK PDF ===============
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# =========================
# KONFIG FAIL SIMPAN DATA
# =========================
DATA_DIR = "data"
FILE_PATH = os.path.join(DATA_DIR, "senarai_perbelanjaan.csv")

KLUSTER_OPTIONS = [
    "SILA PILIH",
    "SUMBANGAN TABUNG PIBG (RM20) ANAK KEDUA - (RM0)",
    "AKTIVITI KECEMERLANGAN AKADEMIK (RM70)",
    "AKTIVITI KOKURIKULUM (RM25)",
    "AKTIVITI PEMBANGUNAN SAHSIAH (RM25)",
    "PEMBANGUNAN FIZIKAL DAN KECERIAN KOLEJ (RM30)",
    "TABUNG KONVOKESYEN DIPLOMA (RM50)",
    "TABUNG GRADUASI DAN APRESIASI (RM30)",
    "SUMBANGAN SUKOV DAN KV SKILL (RM30)",
]

def load_data():
    """Load CSV dan automatik betulkan kolum lama."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)

        if "Jumlah" in df.columns:
            df.rename(columns={"Jumlah": "Jumlah"}, inplace=True)

        # Rename Program → Bayaran (jika fail lama)
        if "Program" in df.columns:
            df.rename(columns={"Program": "Bayaran"}, inplace=True)

        # Remove Tahun-No Baucar
        if "Tahun-No Baucar" in df.columns:
            df.drop(columns=["Tahun-No Baucar"], inplace=True)

        if "Bayaran" not in df.columns:
            df["Bayaran"] = ""

        return df

    else:
        return pd.DataFrame(
            columns=[
                "Tarikh",
                "Kluster",
                "Bayaran",
                "Kaedah Pembayaran",
                "Jumlah",
            ]
        )


def save_data(df):
    df.to_csv(FILE_PATH, index=False)

    try:
        save_data_to_google(df)
    except:
        st.warning("Google gagal, tapi CSV selamat.")
        
def save_data_to_google(df):

    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], scope
        )

        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1

        sheet.clear()

        data = [df.columns.tolist()] + df.astype(str).values.tolist()
        sheet.update("A1", data)   # <<< HANTAR SEKALI (NO QUOTA)

        st.success("Google Sheet updated")

    except Exception as e:
        st.error(f"Google save gagal: {e}")
# =========================
# PDF GENERATOR LANDSCAPE
# =========================
def generate_pdf(df: pd.DataFrame) -> bytes:

    buffer = io.BytesIO()

    # LANDSCAPE A4
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom style for wrapping text
    wrap_style = ParagraphStyle(
        "wrap",
        fontName="Helvetica",
        fontSize=10,
        leading=12,
    )

    title = Paragraph("<b>SENARAI PERBELANJAAN MyPIBGkvks</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 18))

    df_pdf = df.copy()
    df_pdf["Tarikh"] = pd.to_datetime(df_pdf["Tarikh"]).dt.strftime("%d-%b-%Y")
    df_pdf["Jumlah"] = df_pdf["Jumlah"].astype(float)

    if "Bayaran" not in df_pdf.columns:
        st.error("Tiada kolum Bayaran ditemui.")
        return b""

    # TABLE HEADER (tanpa Tahun-No Baucar)
    data_table = [
        ["Tarikh", "Kluster", "Bayaran", "Kaedah Pembayaran", "Jumlah (RM)"]
    ]

    # ROWS (WRAP TEXT)
    for _, row in df_pdf.iterrows():
        data_table.append(
            [
                row["Tarikh"],
                Paragraph(str(row["Kluster"]), wrap_style),
                Paragraph(str(row["Bayaran"]), wrap_style),
                row["Kaedah Pembayaran"],
                f"{row['Jumlah']:,.2f}",
            ]
        )

    jumlah = df_pdf["Jumlah"].sum()

    data_table.append([
        "",
        "",
        "",
        "Jumlah Akhir",
        f"{jumlah:,.2f}"
    ])

    # Column widths (lebih luas supaya table muat)
    col_widths = [80, 200, 250, 130, 100]

    table = Table(data_table, repeatRows=1, colWidths=col_widths)

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -2), colors.whitesmoke),
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
            ]
        )
    )

    elements.append(table)
    doc.build(elements)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# =========================
# MAIN RENDER
# =========================
def render():

    st.markdown("## SENARAI PERBELANJAAN")
    TAHUN_OPTIONS = list(range(2025, 2050))

    tahun = st.selectbox("Pilih Tahun", TAHUN_OPTIONS)
    st.divider()

    if "data_perbelanjaan" not in st.session_state:
        st.session_state.data_perbelanjaan = load_data()
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    if "mode" not in st.session_state:
        st.session_state.mode = "TAMBAH"
    if "selected_index" not in st.session_state:
        st.session_state.selected_index = None
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False
    if "auto_next" not in st.session_state:
        st.session_state.auto_next = False
 
    df = st.session_state.data_perbelanjaan.copy()

    # =========================
    # FILTER IKUT TAHUN
    # =========================
    if not df.empty:
        df["Tarikh"] = pd.to_datetime(
            df["Tarikh"],
            errors="coerce",
            infer_datetime_format=True
        )

        df = df[
            (df["Tarikh"].notna()) &
            (df["Tarikh"].dt.year == tahun)
        ]
        df = df.sort_values(by="Tarikh", ascending=False)

    # =========================
    # BUTANG ATAS
    # =========================
    sp1, col1, sp2, col2, sp3, col3, sp4, col4, sp5 = st.columns(
        [1, 2, 1, 2, 1, 2, 1, 2, 1]
    )

    with col1:
        if st.button("TAMBAH"):
            st.session_state.show_form = True
            st.session_state.mode = "TAMBAH"
            st.session_state.selected_index = None

    with col2:
        if st.button("EDIT"):
            if st.session_state.selected_index is not None:
                st.session_state.show_form = True
                st.session_state.mode = "EDIT"
            else:
                st.warning("Sila pilih satu rekod.")

    with col3:
        if st.button("PADAM"):
            if st.session_state.selected_index is not None:
                st.session_state.confirm_delete = True
            else:
                st.warning("Sila pilih satu rekod.")

    with col4:
        st.download_button(
            "MENCETAK",
            generate_pdf(df),
            file_name=f"senarai_perbelanjaan_{tahun}.pdf",
            mime="application/pdf",
        )
        
    # =========================
    # CONFIRM DELETE
    # =========================
    if st.session_state.confirm_delete:
        st.error("Anda pasti mahu padam rekod ini?")
        c1, c2 = st.columns(2)

        with c1:
            if st.button("YA, PADAM"):

                real_index = st.session_state.selected_index
                df_full = st.session_state.data_perbelanjaan.copy()

                if real_index is not None and real_index < len(df_full):
                    df_full = df_full.drop(real_index).reset_index(drop=True)

                st.session_state.data_perbelanjaan = df_full
                save_data(df_full)

                st.session_state.confirm_delete = False
                st.session_state.selected_index = None
                st.success("Rekod dipadam.")
                st.rerun()

        with c2:
            if st.button("BATAL"):
                st.session_state.confirm_delete = False
                st.rerun()
    # =========================
    # JADUAL PAPARAN
    # =========================
    if not df.empty:

        df_view = df.copy()

        df_view = df.copy()

        if df_view.empty:
            df_view = pd.DataFrame(
                columns=["Tarikh", "Kluster", "Bayaran", "Kaedah Pembayaran", "Jumlah"]
            )

        df_view["Tarikh"] = pd.to_datetime(df_view["Tarikh"]).dt.strftime("%d-%b-%Y")
        df_view["Jumlah"] = df_view["Jumlah"].astype(float).apply(lambda x: f"RM {x:,.2f}")

        df_view.insert(0, "Pilih", False)

        edited_df = st.data_editor(
            df_view,
            hide_index=True,
            disabled=[c for c in df_view.columns if c != "Pilih"],
        )

        pilih = edited_df[edited_df["Pilih"] == True]

        if len(pilih) == 1:
            selected_row = pilih.iloc[0]

            df_full_real = st.session_state.data_perbelanjaan.copy()
            df_full_real["Tarikh"] = pd.to_datetime(
                df_full_real["Tarikh"],
                errors="coerce",
                format="mixed",
                dayfirst=True
            ).dt.strftime("%d-%b-%Y")

            real_match = df_full_real[
                (df_full_real["Tarikh"] == selected_row["Tarikh"]) &
                (df_full_real["Bayaran"].astype(str) == str(selected_row["Bayaran"]))
            ]

            if not real_match.empty:
                st.session_state.selected_index = real_match.index[0]
            else:
                st.session_state.selected_index = None
        else:
            st.session_state.selected_index = None
    # =========================
    # JUMLAH AKHIR
    # =========================
    if not df.empty:
        jumlah = df["Jumlah"].astype(float).sum()
        st.markdown(f"### Jumlah Akhir: RM {jumlah:,.2f}")

    # =========================
    # BORANG TAMBAH / EDIT
    # =========================
    if st.session_state.show_form:

        if st.session_state.mode == "EDIT":
            data = df.loc[st.session_state.selected_index]

            tarikh = st.date_input("TARIKH", pd.to_datetime(data["Tarikh"]))
            kluster = st.selectbox(
    		"KLUSTER",
    		KLUSTER_OPTIONS,
    		index=KLUSTER_OPTIONS.index(data["Kluster"])
    		if data["Kluster"] in KLUSTER_OPTIONS
    		else 0
	    )

            bayaran = st.text_input("BAYARAN", data["Bayaran"])
            kaedah = st.selectbox(
                "KAEDAH PEMBAYARAN",
                ["SILA PILIH", "Tunai", "Bank"],
                index=["SILA PILIH", "Tunai", "Bank"].index(data["Kaedah Pembayaran"]),
            )
            jumlah = st.number_input("JUMLAH", value=float(data["Jumlah"]))

        else:
            tarikh = st.date_input("TARIKH")
            kluster = st.selectbox("KLUSTER", KLUSTER_OPTIONS)
            bayaran = st.text_input("BAYARAN")
            kaedah = st.selectbox("KAEDAH PEMBAYARAN", ["SILA PILIH", "Tunai", "Bank"])
            jumlah = st.number_input("JUMLAH")
            
        st.checkbox(
            "TERUSKAN DENGAN TRANSAKSI SETERUSNYA",
            key="auto_next"
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button("SIMPAN"):

                if (
                    kaedah == "SILA PILIH"
                    or kluster == "SILA PILIH"
                    or bayaran.strip() == ""
                    or jumlah <= 0
                ):
                    st.error("Semua maklumat WAJIB diisi.")
                    st.stop()

                data_baru = {
                    "Tarikh": tarikh.strftime("%Y-%m-%d"),
                    "Kluster": kluster,
                    "Bayaran": bayaran,
                    "Kaedah Pembayaran": kaedah,
                    "Jumlah": float(jumlah),
                }

                df_full = st.session_state.data_perbelanjaan.copy()

                if st.session_state.mode == "TAMBAH":
                    df_full = pd.concat([df_full, pd.DataFrame([data_baru])], ignore_index=True)
                else:
                    idx = st.session_state.selected_index
                    if idx is not None and idx < len(df_full):
                        df_full.loc[idx] = data_baru

                st.session_state.data_perbelanjaan = df_full

                save_data(df_full)

                # REFRESH DATA DARI GOOGLE SAHAJA
                st.session_state.data_perbelanjaan = df_full

                st.success("Rekod berjaya disimpan.")

                st.session_state.show_form = False
                st.session_state.selected_index = None

                st.rerun()

                # ===== AUTO NEXT =====
                if st.session_state.auto_next:
                    st.session_state.show_form = True
                    st.session_state.selected_index = None

                    # reset widget (supaya kosong)
                    st.session_state.pop("Tarikh", None)
                    st.session_state.pop("Kluster", None)
                    st.session_state.pop("Bayaran", None)
                    st.session_state.pop("Kaedah Pembayaran", None)
                    st.session_state.pop("Jumlah", None)

                else:
                    st.session_state.show_form = False
                    st.session_state.selected_index = None

                st.rerun()

        with c2:
            if st.button("BATAL"):
                st.session_state.show_form = False
                st.rerun()