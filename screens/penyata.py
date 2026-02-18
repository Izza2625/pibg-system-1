import streamlit as st
import pandas as pd
import os, json, base64
import streamlit.components.v1 as components
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
HEADER_BLUE = colors.HexColor("#0b1c8c")
ROW_GREY = colors.HexColor("#d9d9d9")

# ======================================================
# KONFIG
# ======================================================
DATA_DIR_NAMA = "data/senarai_nama"
DATA_DIR_LAIN = "data/lain_lain_pendapatan"
DATA_PERBELANJAAN = "data/senarai_perbelanjaan.csv"
DATA_BAKI = "data/baki_tahunan.json"
DATA_BAKI_SUMBER = "data/baki_sumber.json"
TAHUN_OPTIONS = list(range(2025,2050))

def load_baki():
    if not os.path.exists(DATA_BAKI):
        return {}
    with open(DATA_BAKI, "r") as f:
        return json.load(f)

def save_baki(data):
    with open(DATA_BAKI, "w") as f:
        json.dump(data, f, indent=2)
        
def load_baki_sumber():
    if not os.path.exists(DATA_BAKI_SUMBER):
        return {}
    with open(DATA_BAKI_SUMBER, "r") as f:
        return json.load(f)

def save_baki_sumber(data):
    with open(DATA_BAKI_SUMBER, "w") as f:
        json.dump(data, f, indent=2)

# ======================================================
# LOAD KUTIPAN PIBG
# ======================================================
def load_kutipan_pibg(tahun):
    total = bank = tunai = 0.0

    if not os.path.exists(DATA_DIR_NAMA):
        return 0.0, 0.0, 0.0

    for f in os.listdir(DATA_DIR_NAMA):
        if not f.endswith("_meta.json"):
            continue

        with open(os.path.join(DATA_DIR_NAMA, f)) as meta_file:
            meta = json.load(meta_file)

        if meta.get("kohort") != tahun:
            continue

        kelas = f.replace("_meta.json", "")
        csv_file = os.path.join(DATA_DIR_NAMA, f"{kelas}.csv")

        if not os.path.exists(csv_file):
            continue

        df = pd.read_csv(csv_file)

        df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)

        total += df["Jumlah"].sum()
        bank += df[df["Kaedah"] == "Bank"]["Jumlah"].sum()
        tunai += df[df["Kaedah"] == "Tunai"]["Jumlah"].sum()

    return total, bank, tunai

# ======================================================
# LOAD LAIN-LAIN PENDAPATAN
# ======================================================
def load_lain_lain_pendapatan(tahun):
    file = os.path.join(DATA_DIR_LAIN, f"pendapatan_{tahun}.csv")

    if not os.path.exists(file):
        return 0.0, 0.0, 0.0

    df = pd.read_csv(file)
    df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)

    total = df["Jumlah"].sum()
    bank = df[df["Kaedah"] == "Bank"]["Jumlah"].sum()
    tunai = df[df["Kaedah"] == "Tunai"]["Jumlah"].sum()

    return total, bank, tunai

# ======================================================
# PDF
# ======================================================
def generate_pdf(tahun, pendapatan, belanja_df, baki_bank, baki_tunai):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    bold = ParagraphStyle("bold", parent=normal, fontName="Helvetica-Bold")

    elements = []

    # ===== TAJUK =====
    elements.append(
        Paragraph(
            f"<b>PENYATA PENDAPATAN & PERBELANJAAN {tahun}</b>",
            ParagraphStyle("title", alignment=1, fontSize=14),
        )
    )
    elements.append(Spacer(1, 20))

    data = [["KETERANGAN", "RM", "RM"]]

    style = [
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("ALIGN", (1,0), (-1,-1), "RIGHT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BACKGROUND", (0,0), (-1,0), HEADER_BLUE),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ]

    # ================= PENDAPATAN =================
    data.append([Paragraph("<b>PENDAPATAN</b>", bold), "", ""])

    # ===== BAKI BAWA KE HADAPAN =====
    data.append([
        Paragraph(f"BAKI BAWA KE HADAPAN JAN {tahun-1}", normal),
        f"{pendapatan.get('BAKI BAWA',0):,.2f}",
        ""
    ])

    # ===== SUMBANGAN PIBG =====
    data.append([
        Paragraph("SUMBANGAN PIBG TAHUN SEMASA", normal),
        f"{pendapatan.get('SUMBANGAN PIBG TAHUN SEMASA',0):,.2f}",
        ""
    ])

    # ===== KIRA JUMLAH PENDAPATAN (JANGAN RESET LAGI) =====
    jumlah_pendapatan = (
        pendapatan.get("BAKI BAWA",0)
        + pendapatan.get("SUMBANGAN PIBG TAHUN SEMASA",0)
    )
    
    # ===== LAIN-LAIN PENDAPATAN (IKUT PERKARA & ABJAD) =====
    file_lain = os.path.join(DATA_DIR_LAIN, f"pendapatan_{tahun}.csv")

    if os.path.exists(file_lain):
        df_lain = pd.read_csv(file_lain)
        df_lain["Jumlah"] = pd.to_numeric(df_lain["Jumlah"], errors="coerce").fillna(0)
        df_lain["Perkara"] = df_lain["Perkara"].astype(str).str.strip()

        ringkas_lain = (
            df_lain.groupby("Perkara")["Jumlah"]
            .sum()
            .reset_index()
            .sort_values("Perkara")
        )

        for _, r in ringkas_lain.iterrows():
            data.append([Paragraph(r["Perkara"], normal), f"{r['Jumlah']:,.2f}", ""])
            jumlah_pendapatan += r["Jumlah"]

    # ===== JUMLAH PENDAPATAN =====
    idx_last_income_item = len(data) - 1
    style.append(("LINEBELOW", (1, idx_last_income_item), (1, idx_last_income_item), 1, colors.black))

    data.append([
        Paragraph("JUMLAH PENDAPATAN", bold),
        "",
        f"{jumlah_pendapatan:,.2f}"
    ])

    style.append(("FONTNAME", (2, len(data)-1), (2, len(data)-1), "Helvetica-Bold"))

    # ================= PERBELANJAAN =================
    data.append(["", "", ""])
    data.append([Paragraph("<b>PERBELANJAAN</b>", bold), "", ""])

    jumlah_belanja = 0
    if not belanja_df.empty:
        ringkas = belanja_df.groupby("Kluster")["Jumlah"].sum().reset_index()
        for _, r in ringkas.iterrows():
            jumlah_belanja += r["Jumlah"]
            data.append([Paragraph(r["Kluster"], normal), f"{r['Jumlah']:,.2f}", ""])

        idx_last_expense_item = len(data) - 1
        style.append(
            ("LINEBELOW", (1, idx_last_expense_item), (1, idx_last_expense_item), 1, colors.black)
        )

    data.append([
        Paragraph("JUMLAH PERBELANJAAN", bold),
        "",
        f"{jumlah_belanja:,.2f}"
    ])
    style.append(("FONTNAME", (2, len(data)-1), (2, len(data)-1), "Helvetica-Bold"))

    # ===== JUMLAH TOLAK 1 =====
    baki_operasi = jumlah_pendapatan - jumlah_belanja
    idx_tolakan1 = len(data)
    data.append(["", "", f"{baki_operasi:,.2f}"])

    style += [
        ("BACKGROUND", (0, len(data)-1), (-1, len(data)-1), ROW_GREY),
        ("FONTNAME", (2, idx_tolakan1), (2, idx_tolakan1), "Helvetica-Bold"),
        ("LINEABOVE", (2, idx_tolakan1), (2, idx_tolakan1), 1.5, colors.black),
        ("LINEBELOW", (2, idx_tolakan1), (2, idx_tolakan1), 1.5, colors.black),
    ]

    # ================= BAKI =================
    data.append(["", "", ""])
    data.append([Paragraph("<b>BAKI</b>", bold), "", ""])

    data.append(["Baki Bank", f"{baki_bank:,.2f}", ""])
    data.append(["Baki Tunai", f"{baki_tunai:,.2f}", ""])

    idx_last_baki_item = len(data) - 1
    style.append(
        ("LINEBELOW", (1, idx_last_baki_item), (1, idx_last_baki_item), 1, colors.black)
    )

    # ===== JUMLAH AKHIR =====
    jumlah_akhir = baki_bank + baki_tunai
    data.append(["", "", f"{jumlah_akhir:,.2f}"])
    style.extend([
        ("BACKGROUND", (0, len(data)-1), (-1, len(data)-1), ROW_GREY),
        ("FONTNAME", (2, len(data)-1), (2, len(data)-1), "Helvetica-Bold"),
        ("LINEABOVE", (2, len(data)-1), (2, len(data)-1), 1.5, colors.black),
        ("LINEBELOW", (2, len(data)-1), (2, len(data)-1), 1.5, colors.black),
    ])

    table = Table(data, colWidths=[260, 100, 100])
    table.setStyle(TableStyle(style))

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf

    # ===== BAKI =====
    y -= 30
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "BAKI")

    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(70, y, f"Baki Bank : RM {baki_bank:,.2f}")
    y -= 16
    c.drawString(70, y, f"Baki Tunai : RM {baki_tunai:,.2f}")
    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(70, y, f"Jumlah Akhir : RM {(baki_bank + baki_tunai):,.2f}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()

# ======================================================
# RENDER
# ======================================================
def render():
    st.markdown("## PENYATA PENDAPATAN & PERBELANJAAN")

    tahun = st.selectbox("Pilih Tahun", TAHUN_OPTIONS)
    st.divider()

    # ===== PENDAPATAN =====
    pibg_total, pibg_bank, pibg_tunai = load_kutipan_pibg(tahun)
    lain_total, lain_bank, lain_tunai = load_lain_lain_pendapatan(tahun)

    pendapatan = {
        "SUMBANGAN PIBG TAHUN SEMASA": pibg_total,
    }

    st.markdown("### PENDAPATAN")

    baki_data = load_baki()
    baki_bawa = 0.0

    # ===== TAHUN 2025 → ISI SENDIRI =====
    if tahun == 2025:
        # ===== HARDCODE BAKI AWAL SISTEM =====
        baki_bawa = 117296.59

        baki_bank_awal = baki_bawa - 116.50
        baki_tunai_awal = 116.50

        # Simpan untuk auto tahun depan
        baki_data["2025"] = baki_bawa
        save_baki(baki_data)

        baki_sumber_data = load_baki_sumber()
        baki_sumber_data["2025"] = {
            "bank": baki_bank_awal,
            "tunai": baki_tunai_awal
        }
        save_baki_sumber(baki_sumber_data)

    # ===== TAHUN 2026+ → AUTO =====
    else:
        baki_bawa = float(baki_data.get(str(tahun), 0))

        baki_sumber_data = load_baki_sumber()
        data_sumber = baki_sumber_data.get(str(tahun), {"bank":0,"tunai":0})
        baki_bank_awal = data_sumber["bank"]
        baki_tunai_awal = data_sumber["tunai"]
        
    st.write(f"- BAKI BAWA KE HADAPAN JAN {tahun-1} : RM {baki_bawa:,.2f}")

    # ===== 1. SUMBANGAN PIBG =====
    st.write(f"- SUMBANGAN PIBG TAHUN SEMASA : RM {pibg_total:,.2f}")

    # ===== 2. LAIN-LAIN PENDAPATAN IKUT PERKARA =====
    file_lain = os.path.join(DATA_DIR_LAIN, f"pendapatan_{tahun}.csv")

    jumlah_lain_display = 0
    lain_ada = False
    jumlah_pendapatan = pibg_total


    if os.path.exists(file_lain):
        df_lain = pd.read_csv(file_lain)
        df_lain["Jumlah"] = pd.to_numeric(df_lain["Jumlah"], errors="coerce").fillna(0)
        df_lain["Perkara"] = df_lain["Perkara"].astype(str).str.strip()

        ringkas_lain = (
            df_lain.groupby("Perkara")["Jumlah"]
            .sum()
            .reset_index()
            .sort_values("Perkara")
        )

        if not ringkas_lain.empty:
            lain_ada = True
            for _, r in ringkas_lain.iterrows():
                st.write(f"- {r['Perkara']} : RM {r['Jumlah']:,.2f}")
                jumlah_lain_display += r["Jumlah"]

    # 👉 KALAU TIADA DATA
    if not lain_ada:
        st.write("- LAIN-LAIN PENDAPATAN : RM 0.00")
     
    jumlah_pendapatan = baki_bawa + pibg_total + jumlah_lain_display

    st.write("")
    st.markdown(f"**JUMLAH PENDAPATAN : RM {jumlah_pendapatan:,.2f}**")

    st.divider()

    # ===== PERBELANJAAN =====
    st.markdown("### PERBELANJAAN")

    if not os.path.exists(DATA_PERBELANJAAN):
        df_belanja = pd.DataFrame(columns=["Tarikh", "Kluster", "Jumlah", "Kaedah Pembayaran"])
        belanja_bank = belanja_tunai = 0.0
        st.info("Tiada fail perbelanjaan.")
    else:
        df_belanja = pd.read_csv(DATA_PERBELANJAAN)

        df_belanja["Tarikh"] = pd.to_datetime(df_belanja["Tarikh"], errors="coerce")
        df_belanja["Jumlah"] = pd.to_numeric(df_belanja["Jumlah"], errors="coerce").fillna(0)
        df_belanja["Kluster"] = df_belanja["Kluster"].astype(str).str.strip()

        df_belanja = df_belanja[
            (df_belanja["Tarikh"].notna()) &
            (df_belanja["Tarikh"].dt.year == tahun)
        ]

        if df_belanja.empty:
            belanja_bank = belanja_tunai = 0.0
            st.write("- Jumlah Perbelanjaan : RM 0.00")
        else:
            ringkas = df_belanja.groupby("Kluster")["Jumlah"].sum().reset_index()
            for _, r in ringkas.iterrows():
                st.write(f"- {r['Kluster']} : RM {r['Jumlah']:,.2f}")

            belanja_bank = df_belanja[df_belanja["Kaedah Pembayaran"] == "Bank"]["Jumlah"].sum()
            belanja_tunai = df_belanja[df_belanja["Kaedah Pembayaran"] == "Tunai"]["Jumlah"].sum()
            
    if df_belanja.empty:
        jumlah_belanja_display = 0.0
    else:
        jumlah_belanja_display = ringkas["Jumlah"].sum()

    st.write("")
    st.markdown(f"**JUMLAH PERBELANJAAN : RM {jumlah_belanja_display:,.2f}**")

    st.divider()

    # ===== BAKI =====
    baki_bank = baki_bank_awal + (pibg_bank + lain_bank) - belanja_bank
    baki_tunai = baki_tunai_awal + (pibg_tunai + lain_tunai) - belanja_tunai

    st.markdown("### BAKI")
    st.write(f"Baki Bank : RM {baki_bank:,.2f}")
    st.write(f"Baki Tunai : RM {baki_tunai:,.2f}")
    st.markdown(f"## Jumlah Akhir : RM {(baki_bank + baki_tunai):,.2f}")
    jumlah_keseluruhan = jumlah_pendapatan - jumlah_belanja_display

    # simpan untuk tahun depan (auto)
    baki_data[str(tahun + 1)] = jumlah_keseluruhan
    save_baki(baki_data)
    baki_sumber_data[str(tahun + 1)] = {
        "bank": baki_bank,
        "tunai": baki_tunai
    }
    save_baki_sumber(baki_sumber_data)

    # ===== CETAK =====
    if st.button("MENCETAK"):
        pendapatan["BAKI BAWA"] = baki_bawa

        pdf = generate_pdf(
            tahun,
            pendapatan,
            df_belanja,
            baki_bank,
            baki_tunai,
        )

        b64 = base64.b64encode(pdf).decode()
        components.html(
            f"""
            <script>
            var a=document.createElement("a");
            a.href="data:application/pdf;base64,{b64}";
            a.download="penyata_{tahun}.pdf";
            a.click();
            </script>
            """,
            height=0
        )