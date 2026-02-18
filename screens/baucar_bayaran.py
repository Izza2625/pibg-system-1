# baucar_bayaran.py
import streamlit as st
import pandas as pd
import io
import base64
import streamlit.components.v1 as components
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

import os
import json

DATA_FILE = "baucar_db.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE).to_dict("records")
    return []

def save_data(data):
    pd.DataFrame(data).to_csv(DATA_FILE, index=False)

# ======================================================
# 🔹 FUNGSI TUKAR NOMBOR → PERKATAAN (BM)
# ======================================================
def number_to_words_bm(n):
    ones = ["", "SATU", "DUA", "TIGA", "EMPAT", "LIMA", "ENAM", "TUJUH", "LAPAN", "SEMBILAN"]
    tens = ["", "SEPULUH", "DUA PULUH", "TIGA PULUH", "EMPAT PULUH",
            "LIMA PULUH", "ENAM PULUH", "TUJUH PULUH", "LAPAN PULUH", "SEMBILAN PULUH"]

    if n == 0:
        return "KOSONG"

    if n < 10:
        return ones[n]

    if n == 10:
        return "SEPULUH"
    if n == 11:
        return "SEBELAS"
    if n < 20:
        return ones[n - 10] + " BELAS"

    if n < 100:
        return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")

    if n == 100:
        return "SERATUS"
    if n < 200:
        return "SERATUS " + number_to_words_bm(n - 100)

    if n < 1000:
        return ones[n // 100] + " RATUS" + (" " + number_to_words_bm(n % 100) if n % 100 != 0 else "")

    if n == 1000:
        return "SERIBU"
    if n < 2000:
        return "SERIBU " + number_to_words_bm(n - 1000)

    if n < 1000000:
        return number_to_words_bm(n // 1000) + " RIBU" + (" " + number_to_words_bm(n % 1000) if n % 1000 != 0 else "")

    return ""


# ======================================================
# 🔹 JUMLAH → RINGGIT DALAM PERKATAAN (ADA "DAN")
# ======================================================
def jumlah_ke_ringgit(jumlah):
    ringgit = int(jumlah)
    sen = int(round((jumlah - ringgit) * 100))

    ayat = number_to_words_bm(ringgit)

    if sen == 0:
        return f"{ayat} SAHAJA"
    else:
        return f"{ayat} RINGGIT DAN {number_to_words_bm(sen)} SEN SAHAJA"


# ----------------------------
# PDF GENERATOR
# ----------------------------
def generate_pdf(df_items, baucar_no, perkara, dibayar_kepada, cek_no,
                 ringgit, tarikh_baucar, nama_penerima):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=30, rightMargin=30,
        topMargin=30, bottomMargin=30
    )

    normal = ParagraphStyle("normal", fontName="Helvetica", fontSize=11, leading=16.5)
    title_style = ParagraphStyle("title_style", parent=normal, alignment=TA_CENTER, fontSize=14)
    center_style = ParagraphStyle("center", parent=normal, alignment=TA_CENTER)
    right_style = ParagraphStyle("right", parent=normal, alignment=TA_RIGHT)

    elements = []

    elements.append(Paragraph(f"Tahun-No.Baucar : <u>{baucar_no}</u>", right_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>BAUCAR BAYARAN</b>", title_style))
    elements.append(Paragraph("PIBG SEK.MEN.TEKNIK KUALA SELANGOR", center_style))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("<b>BAHAGIAN A</b>", normal))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Dibayar kepada : {dibayar_kepada}", normal))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"Perkara : {perkara}", normal))
    elements.append(Spacer(1, 12))

    table_data = [["BIL", "TARIKH", "PERKARA SURAT/KERTAS KERJA", "JUMLAH ( RM )"]]
    jumlah = 0.0

    for i, row in enumerate(df_items.to_dict("records"), start=1):
        Jumlah = float(row.get("Jumlah", 0.0))
        jumlah += Jumlah
        table_data.append([i, row.get("Tarikh", ""), row.get("Perkara", ""), f"{Jumlah:,.2f}"])

    while len(table_data) < 7:
        table_data.append(["", "", "", ""])

    table_data.append(["", "", "JUMLAH", f"{jumlah:,.2f}"])

    table = Table(table_data, colWidths=[40, 90, 280, 90])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
        ("FONTNAME", (2, -1), (3, -1), "Helvetica-Bold"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 14))

    elements.append(Paragraph(
        f"Disertakan bayaran cek ( No : {cek_no} ) / tunai bernilai RM {jumlah:,.2f}", normal))
    elements.append(Paragraph(f"( Ringgit : {ringgit} )", normal))
    elements.append(Spacer(1, 14))

    # DITERIMA DARI
    diterima = Table([
        [f"Tarikh : {tarikh_baucar}", "Diterima dari : ________________________________"],
        ["", Paragraph("<para align='center'>( AIZATUL ASYIKIN BINTI TAJUL ARIFFIN )</para>", normal)],
        ["", Paragraph("<para align='center'>BENDAHARI PIBG SMTKS</para>", normal)]
    ], colWidths=[240, 240])

    diterima.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    elements.append(diterima)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>BAHAGIAN B</b>", normal))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<u>Akuan Penerima</u>", normal))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(
        f"Diterima daripada Bendahari PIBG cek ( No : {cek_no} ) / tunai bernilai RM {jumlah:,.2f}", normal))
    elements.append(Paragraph(f"( Ringgit : {ringgit} )", normal))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(
        f"melalui baucar bayaran bernombor {baucar_no} dan bertarikh {tarikh_baucar} kerana butiran yang dinyatakan di atas.",
        normal))
    elements.append(Spacer(1, 16))

    nama_paragraph = f"( {nama_penerima} )" if nama_penerima else "(                                   )"
    ttd = Table([
        [f"Tarikh diterima : {tarikh_baucar}", "Tandatangan Penerima : ____________________"],
        ["", Paragraph(f"<para align='center'>{nama_paragraph}</para>", normal)]
    ], colWidths=[240, 240])

    elements.append(ttd)

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# ----------------------------
# STREAMLIT RENDER
# ----------------------------
def render():
    if "baucar_db" not in st.session_state:
        st.session_state.baucar_db = load_data()

    if "baucar_items" not in st.session_state:
        st.session_state.baucar_items = []

    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False

    st.markdown("## BAUCAR BAYARAN")
    # ===== PILIH TAHUN =====
    tahun_set = set()
    for d in st.session_state.baucar_db:
        baucar = str(d.get("Baucar",""))
        if "-" in baucar:
            try:
                tahun_set.add(int(baucar.split("-")[0]))
            except:
                pass

    if not tahun_set:
        tahun_set.add(datetime.now().year)

    tahun_list = sorted(tahun_set, reverse=True)
    tahun_pilih = st.selectbox("Pilih Tahun", tahun_list)

    sp1, col1, sp2, col2, sp3, col3, sp4, col4, sp5 = st.columns(
        [1, 2, 1, 2, 1, 2, 1, 2, 1]
    )

    with col1:
        if st.button("TAMBAH"):
            st.session_state.mode = "add"
            st.session_state.baucar_items = []

    with col2:
        if st.button("EDIT"):
            st.session_state.mode = "edit"

    with col3:
        if st.button("PADAM"):
            st.session_state.mode = "delete"

    with col4:
        if st.button("MENCETAK"):
            st.session_state.mode = "print"
    
    mode = st.session_state.get("mode", "")

    if mode in ["add", "edit"]:

        st.subheader("MAKLUMAT BAUCAR")

        selected_data = {}

        if mode == "edit":
            if "selected_index" in st.session_state and  st.session_state.selected_index is not None:
                selected_data = st.session_state.baucar_db[st.session_state.selected_index]
            else:
                st.warning("⚠️ Sila pilih rekod dalam jadual")
                st.stop()

        baucar_no = st.text_input("No Baucar", value=selected_data.get("Baucar",""))
        perkara = st.text_input("Perkara", value=selected_data.get("Perkara",""))
        dibayar_kepada = st.text_input("Dibayar Kepada", value=selected_data.get("Dibayar",""))

        if "Tarikh" in selected_data:
            tarikh_default = datetime.strptime(selected_data["Tarikh"], "%d-%b-%Y")
        else:
            tarikh_default = datetime.now()

        tarikh = st.date_input("Tarikh", value=tarikh_default)

        cek_no = st.text_input("No Cek", value=selected_data.get("Cek",""))
        nama_penerima = st.text_input("Nama Penerima", value=selected_data.get("Penerima",""))

        st.markdown("### PERKARA / SURAT KERJA")

        perkara_item = st.text_input("Perkara Surat/Kertas Kerja")
        jumlah_item = st.number_input("Jumlah (RM)", min_value=0.0, step=1.0, format="%.2f")

        if st.button("TAMBAH PERKARA"):
            if perkara_item and jumlah_item > 0:
                st.session_state.baucar_items.append({
                    "Tarikh": tarikh.strftime("%d-%b-%Y"),  # auto guna tarikh baucar
                    "Perkara": perkara_item,
                    "Jumlah": float(jumlah_item)
                })

        if st.session_state.baucar_items:
            df_items_preview = pd.DataFrame(st.session_state.baucar_items)
            df_items_preview.insert(0, "BIL", range(1, len(df_items_preview)+1))
            st.dataframe(df_items_preview, use_container_width=True)

        jumlah_total = sum(item["Jumlah"] for item in st.session_state.baucar_items)
        ringgit_auto = jumlah_ke_ringgit(jumlah_total)

        st.write(f"**Jumlah Keseluruhan: RM {jumlah_total:,.2f}**")
        st.write(f"**Ringgit: {ringgit_auto}**")
        st.checkbox(
            "TERUSKAN DENGAN BAUCAR SETERUSNYA",
            key="auto_next_baucar"
        )

        if st.button("SIMPAN"):

            jumlah_total = sum(item["Jumlah"] for item in st.session_state.baucar_items)

            data = {
                "Baucar": baucar_no,
                "Tarikh": tarikh.strftime("%d-%b-%Y"),
                "Dibayar": dibayar_kepada,
                "Perkara": perkara,
                "Cek": cek_no,
                "Jumlah": f"{jumlah_total:,.2f}",
                "Penerima": nama_penerima,
                "Items": json.dumps(st.session_state.baucar_items)
            }

            if mode == "add":
                st.session_state.baucar_db.append(data)

            elif mode == "edit":
                if "selected_index" in st.session_state:
                    index = st.session_state.selected_index
                    st.session_state.baucar_db[index] = data
                else:
                    st.warning("Sila pilih rekod dahulu")
                    st.stop()

            save_data(st.session_state.baucar_db)

            st.success("Data disimpan dalam sistem")

            # ===== AUTO NEXT BAUCAR =====
            if st.session_state.auto_next_baucar:
                st.session_state.mode = "add"
                st.session_state.selected_index = None
                st.session_state.baucar_items = []

                # reset input widget
                for key in [
                    "No Baucar",
                    "Perkara",
                    "Dibayar Kepada",
                    "No Cek",
                    "Nama Penerima"
                ]:
                    st.session_state.pop(key, None)

            else:
                st.session_state.mode = ""
                st.session_state.selected_index = None
                st.session_state.baucar_items = []

            st.rerun()

    st.divider()
    st.subheader("SENARAI BAUCAR")

    df = pd.DataFrame(st.session_state.baucar_db)

    if not df.empty:

        # ===== FILTER IKUT TAHUN DIPILIH =====
        df = df[df["Baucar"].astype(str).str.startswith(str(tahun_pilih))]

        def extract_tahun(x):
            try:
                return int(str(x).split("-")[0])
            except:
                return 0

        def extract_no(x):
            try:
                return int(str(x).split("-")[1])
            except:
                return 0

        df["tahun"] = df["Baucar"].apply(extract_tahun)
        df["no"] = df["Baucar"].apply(extract_no)

        df = df.sort_values(["tahun", "no"], ascending=[False, False])
        df = df.drop(columns=["tahun", "no"])

    if not df.empty:

        df = df[["Baucar", "Tarikh", "Dibayar", "Perkara", "Cek", "Jumlah"]]
        df = df.rename(columns={
            "Dibayar": "Dibayar Kepada"
        })

        selected = st.dataframe(
            df.reset_index(drop=True),
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        if selected.selection.rows:
            row_pos = selected.selection.rows[0]
            st.session_state.selected_index = df.iloc[row_pos].name

    if mode == "delete":
        if "selected_index" in st.session_state and st.session_state.selected_index is not None:
            st.session_state.confirm_delete = True
        else:
            st.warning("Sila pilih rekod dahulu")

    if mode == "print":

        if "selected_index" not in st.session_state or st.session_state.selected_index is None:
            st.warning("Sila pilih rekod dahulu")
        else:

            row = st.session_state.baucar_db[st.session_state.selected_index]

            items_text = row.get("Items", "[]")
            df_items = pd.DataFrame(json.loads(items_text))

            jumlah_total = sum(df_items["Jumlah"]) if not df_items.empty else 0
            ringgit_auto = jumlah_ke_ringgit(jumlah_total)

            pdf = generate_pdf(
                df_items,
                row["Baucar"],
                row["Perkara"],
                row["Dibayar"],
                row["Cek"],
                ringgit_auto,
                row["Tarikh"],
                row["Penerima"]
            )

            b64 = base64.b64encode(pdf).decode()
            file_name = f"baucar_{row['Baucar']}.pdf"

            components.html(f"""
            <script>
            var a = document.createElement('a');
            a.href = "data:application/pdf;base64,{b64}";
            a.download = "{file_name}";
            a.click();
            </script>
            """, height=0)

    # =========================
    # CONFIRM DELETE
    # =========================
    if st.session_state.confirm_delete:

        st.error("Anda pasti mahu padam rekod ini?")
        c1, c2 = st.columns(2)

        with c1:
            if st.button("YA, PADAM"):
                st.session_state.baucar_db.pop(st.session_state.selected_index)
                save_data(st.session_state.baucar_db)   # save selepas padam
                st.session_state.confirm_delete = False
                st.session_state.selected_index = None
                st.success("Rekod dipadam.")
                st.rerun()

        with c2:
            if st.button("BATAL"):
                st.session_state.confirm_delete = False
                st.rerun()


if __name__ == "__main__":
    render()
