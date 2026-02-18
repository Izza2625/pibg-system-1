import streamlit as st
import pandas as pd
import gspread
import smtplib
from email.message import EmailMessage
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ======================================================
# KONFIG GOOGLE SHEET
# ======================================================
SHEET_ID = "1A8Mj32ct2wuhfwFBWmiV7CABfhGgXrLnCqX3uDPPhms"
CREDENTIAL_PATH = "credentials/service_account.json"

# ======================================================
# KONFIG EMAIL BENDAHARI
# ⚠️ GUNA APP PASSWORD GMAIL (16 HURUF, TANPA SPACE)
# ======================================================
EMAIL_BENDAHARI = "izzah2625@gmail.com"
EMAIL_PASSWORD = "jedvgkfcunlveezu"   # ❗️BUANG SPACE

# ======================================================
# LOAD DATA GOOGLE SHEET
# ======================================================
@st.cache_data(ttl=30)
def load_permohonan_data():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIAL_PATH, scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1

    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    df["_row"] = range(2, len(df) + 2)

    return df

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIAL_PATH, scope
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1

# ======================================================
# UPDATE STATUS DALAM GOOGLE SHEET
# ======================================================
def update_status(sheet, row_index, new_status):
    status_col = sheet.find("Status").col
    sheet.update_cell(row_index + 2, status_col, new_status)

def padam_permohonan(sheet, row_index):
    sheet.delete_rows(row_index + 2)

# ======================================================
# GENERATE SURAT PERMOHONAN (PDF)
# ======================================================
def generate_jadual_pdf(df):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=15,
        leftMargin=15,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()

    cell_style = styles["Normal"]
    cell_style.fontSize = 6.5
    cell_style.leading = 8

    title_style = styles["Title"]
    title_style.fontSize = 13

    elements = []

    # TAJUK
    elements.append(
        Paragraph("<b>SENARAI PERMOHONAN PIBG</b>", title_style)
    )

    elements.append(Paragraph("<br/>", cell_style))

    # ======================
    # HEADER
    # ======================
    data = [[
        "Tarikh",
        "Nama Pemohon",
        "Program",
        "Tujuan Permohonan",
        "Jumlah (RM)",
        "Nama Bank",
        "Nombor Akaun Bank",
        "E-mel",
        "Status"
    ]]

    # ======================
    # DATA
    # ======================
    for _, row in df.iterrows():
        data.append([
            row["Tarikh"].strftime("%d-%m-%Y") if pd.notna(row["Tarikh"]) else "",
            Paragraph(str(row["Nama Pemohon"]), cell_style),
            Paragraph(str(row["Program"]), cell_style),
            Paragraph(str(row["Tujuan Permohonan"]), cell_style),
            f"RM {row['Jumlah Permohonan (RM)']:,.2f}",
            Paragraph(str(row.get("Nama Bank", "")), cell_style),
            Paragraph(str(row.get("Nombor Akaun Bank", "")), cell_style),
            Paragraph(str(row["E-mail Pemohon"]), cell_style),
            Paragraph(str(row["Status"]), cell_style),
        ])

    # ======================
    # AUTO-FIT LEBAR PAGE
    # ======================
    page_width = doc.width

    col_ratios = [1, 2.5, 2, 4, 1.5, 2.5, 2, 3, 1.5]
    total = sum(col_ratios)

    col_widths = [(page_width * r / total) for r in col_ratios]

    table = Table(data, colWidths=col_widths, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6.5),

        ("ALIGN", (4, 1), (4, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# ======================================================
# HANTAR EMAIL + PDF KEPADA PEMOHON
# ======================================================
def hantar_email_pemohon(data, status, sebab=None):
    email_pemohon = str(data["E-mail Pemohon"]).strip()

    if "@" not in email_pemohon:
        st.error(f"Alamat e-mel tidak sah: {email_pemohon}")
        st.stop()

    msg = EmailMessage()
    msg["From"] = EMAIL_BENDAHARI
    msg["To"] = email_pemohon

    if status == "Lulus":
        subject = "Kelulusan Permohonan PIBG KVKS"
        body = f"""

Assalamualaikum / Salam Sejahtera,

Merujuk kepada permohonan penggunaan dana PIBG yang telah dikemukakan,
sukacita dimaklumkan bahawa permohonan berikut telah DILULUSKAN.

Butiran Permohonan:
Nama Pemohon : {data['Nama Pemohon']}
Program      : {data['Program']}
Jumlah       : RM {data['Jumlah Permohonan (RM)']}
Nama Bank    : {data.get('Nama Bank', '')}
No Akaun     : {data.get('Nombor Akaun Bank', '')}

Dimaklumkan bahawa pihak PIBG akan membuat kemasukan dana ke dalam akaun
yang dinyatakan di atas dalam tempoh tiga (3) hari bekerja dari tarikh
emel ini dihantar.

Sekian, terima kasih.

Yang menjalankan amanah,

Bendahari PIBG  
Kolej Vokasional Kuala Selangor
"""
    else:
        subject = "Keputusan Permohonan PIBG KVKS"
        body = f"""
Assalamualaikum / Salam Sejahtera,

Merujuk kepada permohonan penggunaan dana PIBG yang telah dikemukakan,
dukacita dimaklumkan bahawa permohonan berikut TIDAK DILULUSKAN.

Butiran Permohonan:
Nama Pemohon : {data['Nama Pemohon']}
Program      : {data['Program']}
Jumlah       : RM {data['Jumlah Permohonan (RM)']}

Sebab tidak dapat diluluskan: {sebab}

Sekian, terima kasih.

Yang menjalankan amanah,

Bendahari PIBG
Kolej Vokasional Kuala Selangor
"""

    msg["Subject"] = subject    
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_BENDAHARI, EMAIL_PASSWORD)
        server.send_message(msg)

# ======================================================
# HALAMAN MAKLUMAT PERMOHONAN
# ======================================================
def render():
    st.markdown("## MAKLUMAT PERMOHONAN PIBG")

    if "selected_index" not in st.session_state:
        st.session_state.selected_index = None
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False
    if "show_reject_form" not in st.session_state:
        st.session_state.show_reject_form = False
    if "sebab_tolak" not in st.session_state:
        st.session_state.sebab_tolak = ""


    try:
        # ======================
        # LOAD DATA
        # ======================
        df = load_permohonan_data()
        sheet = get_sheet()

        # ======================
        # BERSIHKAN FORMAT RM
        # ======================
        df["Jumlah Permohonan (RM)"] = (
            df["Jumlah Permohonan (RM)"]
            .astype(str)
            .str.replace("RM", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
        )

        df["Tarikh"] = pd.to_datetime(df["Tarikh"], errors="coerce")
        df["Tahun"] = df["Tarikh"].dt.year

        # ======================
        # PILIH TAHUN
        # ======================
        st.markdown("Pilih Tahun")
        tahun_list = sorted(df["Tahun"].dropna().unique().astype(int))
        tahun = st.selectbox("Tahun", tahun_list)
        df = df[df["Tahun"] == tahun]

        st.divider()

        # ======================
        # BUTANG ATAS
        # ======================
        sp1, col1, sp2, col2, sp3, col3, sp4, col4, sp5 = st.columns(
            [1, 2, 1, 2, 1, 2, 1, 2, 1]
        )

        with col1:
            if st.button("LULUS"):
                if st.session_state.selected_index is not None:
                    selected = df.loc[st.session_state.selected_index]
                    row = int(selected["_row"])
                    update_status(sheet, row - 2, "Lulus")
                    st.cache_data.clear()
                    hantar_email_pemohon(selected, "Lulus")
                    st.success("Permohonan diluluskan & email dihantar")
                    st.rerun()
                else:
                    st.warning("Sila tick satu permohonan dahulu")
        with col2:
            if st.button("TIDAK LULUS"):
                if st.session_state.selected_index is not None:
                    st.session_state.show_reject_form = True
                else:
                    st.warning("Sila tick satu permohonan dahulu")

        with col3:
            if st.button("PADAM"):
                if st.session_state.selected_index is not None:
                    st.session_state.confirm_delete = True
                else:
                    st.warning("Sila tick satu permohonan")

        with col4:
            st.download_button(
                "MENCETAK",
                generate_jadual_pdf(df),
                f"Senarai_Permohonan_{tahun}.pdf",
                "application/pdf"
            )

        if st.session_state.show_reject_form:
            st.divider()
            st.subheader("Sebab Permohonan Tidak Dapat Diluluskan")

            sebab = st.text_area(
                "Nyatakan sebab tidak diluluskan",
                height=120,
                placeholder="Contoh: Permohonan tidak diluluskan kerana peruntukan PIBG tidak mencukupi bagi tahun semasa."
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button("HANTAR KEPUTUSAN"):
                    if sebab.strip() == "":
                        st.error("Sila isi sebab tidak lulus.")
                        st.stop()

                    selected = df.loc[st.session_state.selected_index]
                    row = int(selected["_row"])

                    update_status(sheet, row - 2, "Tidak Lulus")
                    st.cache_data.clear()
                    hantar_email_pemohon(selected, "Tidak Lulus", sebab)

                    st.session_state.show_reject_form = False
                    st.session_state.selected_index = None

                    st.success("Keputusan penolakan berjaya dihantar kepada pemohon.")
                    st.rerun()

            with c2:
                if st.button("BATAL"):
                    st.session_state.show_reject_form = False
                    st.rerun()

        # ======================
        # CONFIRM PADAM
        # ======================
        if st.session_state.confirm_delete:
            st.error("Anda pasti mahu padam permohonan ini?")
            c1, c2 = st.columns(2)

            with c1:
                if st.button("YA, PADAM"):
                    row = int(df.loc[st.session_state.selected_index]["_row"])
                    sheet.delete_rows(row)
                    st.cache_data.clear()
                    st.session_state.confirm_delete = False
                    st.session_state.selected_index = None
                    st.success("Permohonan dipadam")
                    st.rerun()

            with c2:
                if st.button("BATAL"):
                    st.session_state.confirm_delete = False
                    st.rerun()

        # ======================
        # CARIAN
        # ======================
        st.divider()
        carian = st.text_input("Cari Nama Pemohon / Program")

        if carian:
            df = df[
                df["Nama Pemohon"].str.contains(carian, case=False, na=False) |
                df["Program"].str.contains(carian, case=False, na=False)
            ]

        # ======================
        # JADUAL + TICK
        # ======================
        st.divider()

        df_view = df[
            [
                "Tarikh",
                "Nama Pemohon",
                "Program",
                "Tujuan Permohonan",
                "Jumlah Permohonan (RM)",
                "Nama Bank",
                "Nombor Akaun Bank",
                "E-mail Pemohon",
                "Status",
            ]
        ].copy()

        df_view["Tarikh"] = df_view["Tarikh"].dt.strftime("%d-%m-%Y")
        df_view["Jumlah Permohonan (RM)"] = df_view["Jumlah Permohonan (RM)"].apply(
            lambda x: f"RM {x:,.2f}"
        )

        df_view.insert(0, "Pilih", False)

        edited_df = st.data_editor(
            df_view,
            hide_index=True,
            disabled=[c for c in df_view.columns if c != "Pilih"],
            use_container_width=True,
            key="editor_permohonan"
        )

        pilih = edited_df[edited_df["Pilih"] == True]

        if len(pilih) == 1:
            st.session_state.selected_index = pilih.index[0]
        else:
            st.session_state.selected_index = None
     
        # ======================
        # PAPAR MAKLUMAT BAWAH
        # ======================
        if st.session_state.selected_index is not None:
            selected = df.loc[st.session_state.selected_index]
            st.divider()
            st.markdown("### Butiran Permohonan")
            st.write(f"**Nama Pemohon:** {selected['Nama Pemohon']}")
            tarikh_str = pd.to_datetime(selected["Tarikh"], errors="coerce").strftime("%d-%m-%Y")
            st.write(f"**Tarikh:** {tarikh_str}")
            st.write(f"**Program:** {selected['Program']}")
            st.write(f"**Tujuan:** {selected['Tujuan Permohonan']}")
            st.write(f"**Jumlah:** RM {selected['Jumlah Permohonan (RM)']:,.2f}")
            st.write(f"**Nama Bank:** {selected['Nama Bank']}")
            st.write(f"**No Akaun:** {selected['Nombor Akaun Bank']}")
            st.write(f"**E-mel:** {selected['E-mail Pemohon']}")
            st.write(f"**Status:** {selected['Status']}")

    except Exception as e:
        st.error("Ralat sistem")
        st.code(str(e))
