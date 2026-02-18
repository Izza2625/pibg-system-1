import streamlit as st
import pandas as pd
import os, json
import matplotlib.pyplot as plt
import numpy as np

# ======================
# PATH
# ======================
DATA_NAMA_DIR = "data/senarai_nama"
DATA_PENDAPATAN_DIR = "data/lain_lain_pendapatan"
DATA_PERBELANJAAN = "data/senarai_perbelanjaan.csv"

TAHUN_OPTIONS = list(range(2025, 2050))

# ======================
# UI CARD
# ======================
def card(title, value):
    return f"""
    <div style="
        background:#A83232;
        padding:18px;
        border-radius:18px;
        text-align:center;
        color:white;
    ">
        <div style="font-size:13px;">{title}</div>
        <div style="font-size:24px;font-weight:bold;">{value}</div>
    </div>
    """

# ======================
# KUTIPAN PIBG (IKUT TAHUN / KOHORT)
# ======================
def load_kutipan_pibg(tahun):
    total = bayar = pelajar = 0

    if not os.path.exists(DATA_NAMA_DIR):
        return 0, 0, 0, {}

    tahun_data = {
        "1 SVM": 0,
        "2 SVM": 0,
        "1 DVM": 0,
        "2 DVM": 0,
    }

    for meta_file in os.listdir(DATA_NAMA_DIR):
        if not meta_file.endswith("_meta.json"):
            continue

        with open(os.path.join(DATA_NAMA_DIR, meta_file)) as f:
            meta = json.load(f)

        if str(meta.get("kohort")) != str(tahun):
            continue

        kelas = meta_file.replace("_meta.json", "").replace("_", " ")
        csv_file = os.path.join(DATA_NAMA_DIR, f"{kelas.replace(' ', '_')}.csv")

        if not os.path.exists(csv_file):
            continue

        df = pd.read_csv(csv_file)
        df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)

        total += df["Jumlah"].sum()
        bayar += (df["Jumlah"] > 0).sum()
        pelajar += len(df)

        for k in tahun_data:
            if k in kelas:
                tahun_data[k] += df["Jumlah"].sum()

    return total, bayar, pelajar, tahun_data

# ======================
# LAIN-LAIN PENDAPATAN (IKUT TAHUN)
# ======================
def load_lain_pendapatan(tahun):
    file = os.path.join(DATA_PENDAPATAN_DIR, f"pendapatan_{tahun}.csv")

    if not os.path.exists(file):
        return 0

    df = pd.read_csv(file)

    if "Amaun" in df.columns and "Jumlah" not in df.columns:
        df.rename(columns={"Amaun": "Jumlah"}, inplace=True)

    df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)
    return df["Jumlah"].sum()

# ======================
# PERBELANJAAN (IKUT TAHUN)
# ======================
def load_perbelanjaan(tahun):
    if not os.path.exists(DATA_PERBELANJAAN):
        return pd.DataFrame(columns=["Tarikh", "Kluster", "Jumlah", "Kaedah Pembayaran"])

    df = pd.read_csv(DATA_PERBELANJAAN)

    df["Tarikh"] = pd.to_datetime(df["Tarikh"], errors="coerce")
    df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)
    df["Kluster"] = df["Kluster"].astype(str).str.strip()

    return df[df["Tarikh"].dt.year == tahun]

# ======================
# MAIN
# ======================
def render():
    st.markdown("## HALAMAN UTAMA PIBG")

    # ===== PILIH TAHUN =====
    tahun = st.selectbox("Pilih Tahun", TAHUN_OPTIONS)
    st.divider()

    # ===== LOAD DATA =====
    kutipan_pibg, pelajar_bayar, jumlah_pelajar, svm_dvm_data = load_kutipan_pibg(tahun)
    sumbangan = load_lain_pendapatan(tahun)
    df_belanja = load_perbelanjaan(tahun)

    # ===== KIRAAN UTAMA =====
    jumlah_pendapatan = kutipan_pibg + sumbangan
    jumlah_perbelanjaan = df_belanja["Jumlah"].sum() if not df_belanja.empty else 0
    baki_semasa = jumlah_pendapatan - jumlah_perbelanjaan

    peratus = (pelajar_bayar / jumlah_pelajar * 100) if jumlah_pelajar else 0

    # ======================
    # KAD ATAS
    # ======================
    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(card("Jumlah Pendapatan", f"RM {jumlah_pendapatan:,.2f}"), unsafe_allow_html=True)
    c2.markdown(card("Jumlah Perbelanjaan", f"RM {jumlah_perbelanjaan:,.2f}"), unsafe_allow_html=True)
    c3.markdown(card("Baki Semasa", f"RM {baki_semasa:,.2f}"), unsafe_allow_html=True)
    c4.markdown(card("Lain-lain Pendapatan", f"RM {sumbangan:,.2f}"), unsafe_allow_html=True)

    # ======================
    # PERATUSAN
    # ======================
    st.markdown(f"""
    <div style="
        background:#A83232;
        padding:20px;
        border-radius:18px;
        color:white;
        text-align:center;
        margin-top:15px;
    ">
        <div style="font-size:13px;">PERATUSAN PEMBAYARAN ({tahun})</div>
        <div style="font-size:36px;font-weight:bold;">{peratus:.2f}%</div>
        <div>
        Pelajar Telah Bayar: {pelajar_bayar} | 
        Pelajar Belum Bayar: {jumlah_pelajar - pelajar_bayar}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ======================
    # PERATUS IKUT TAHUN PENGAJIAN
    # ======================
    def kira_peratus_tahun(tahun):

        result = {
            "2 DVM": {"bayar": 0, "pelajar": 0},
            "1 DVM": {"bayar": 0, "pelajar": 0},
            "2 SVM": {"bayar": 0, "pelajar": 0},
            "1 SVM": {"bayar": 0, "pelajar": 0},
        }

        if not os.path.exists(DATA_NAMA_DIR):
            return result

        for meta_file in os.listdir(DATA_NAMA_DIR):
            if not meta_file.endswith("_meta.json"):
                continue

            with open(os.path.join(DATA_NAMA_DIR, meta_file)) as f:
                meta = json.load(f)

            if str(meta.get("kohort")) != str(tahun):
                continue

            kelas = meta_file.replace("_meta.json", "").replace("_", " ")
            csv_file = os.path.join(DATA_NAMA_DIR, f"{kelas.replace(' ', '_')}.csv")
  
            if not os.path.exists(csv_file):
                 continue

            df = pd.read_csv(csv_file)
            df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0)

            bayar = (df["Jumlah"] > 0).sum()
            pelajar = len(df)

            # ================= MAP TAHUN =================
            if kelas.startswith("2 DVM"):
                key = "2 DVM"
            elif kelas.startswith("1 DVM"):
                key = "1 DVM"
            elif kelas.startswith("2 SVM") or kelas.startswith("5 OPP"):
                key = "2 SVM"
            elif kelas.startswith("1 SVM") or kelas.startswith("4 OPP"):
                key = "1 SVM"
            else:
                continue

            result[key]["bayar"] += bayar
            result[key]["pelajar"] += pelajar

        return result

    # ======================
    # PERATUS IKUT TAHUN
    # ======================
    tahun_detail = kira_peratus_tahun(tahun)

    cols = st.columns(4)

    for i, k in enumerate(["2 DVM", "1 DVM", "2 SVM", "1 SVM"]):
        bayar = tahun_detail[k]["bayar"]
        pelajar = tahun_detail[k]["pelajar"]

        peratus_k = (bayar / pelajar * 100) if pelajar else 0

        cols[i].markdown(f"""
        <div style="
            background:#7A1F1F;
            padding:14px;
            border-radius:14px;
            text-align:center;
            color:white;
            margin-top:10px;
        ">
            <div style="font-size:13px;">{k}</div>
            <div style="font-size:20px;font-weight:bold;">{peratus_k:.2f}%</div>
            <div style="font-size:12px;">
            Bayar: {bayar} / {pelajar}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ======================
    # GRAF (KECIL & KEMAS)
    # ======================
    col1, col2 = st.columns(2)

    # ===== PERBELANJAAN IKUT KATEGORI =====
    with col1:
        st.markdown("### Perbelanjaan Mengikut Kategori")

        kategori = df_belanja.groupby("Kluster")["Jumlah"].sum()

        fig, ax = plt.subplots(figsize=(6, 7.5))

        bg_color = "#5B0F0F"
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        if len(kategori) > 0:
            cmap = plt.cm.Set3
            slice_colors = [
                "#E8C07D",  # soft gold
                "#9EC1A3",  # soft green
                "#A3BFD9",  # soft blue
                "#E6A4A4",  # soft pink
                "#C7B8EA",  # lavender
                "#F2D7A1",
                "#A8D5BA",
                "#B5C9E2"
            ][:len(kategori)]


            wedges, texts, autotexts = ax.pie(
                kategori,
                autopct="%1.0f%%",
                startangle=90,
                colors=slice_colors,
                radius=1.0,
                pctdistance=0.7,
                wedgeprops=dict(edgecolor="#5B0F0F"),
                textprops=dict(color="white", fontsize=11)
            )

            ax.axis("equal")

            legend_labels = [
                f"{k} — RM {v:,.0f}" for k, v in kategori.items()
            ]

            legend = ax.legend(
                wedges,
                legend_labels,
                loc="lower center",
                bbox_to_anchor=(0.5, -0.15),
                frameon=False,
                fontsize=9,
                ncol=1
            )

            for text in legend.get_texts():
                text.set_color("white")

            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")

        else:
            ax.set_aspect("auto")          
            ax.set_xticks([])
            ax.set_yticks([])

            ax.set_position([0.05, 0.05, 0.9, 0.9])
            ax.axis("off")

        plt.tight_layout()
        st.pyplot(fig)

    # ===== KUTIPAN SVM / DVM =====
    with col2:
        st.markdown("### Kutipan Mengikut Tahun Pengajian")

        fig, ax = plt.subplots(figsize=(6, 8.4))
        bg_color = "#5B0F0F"
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        bar_colors = [
            "#C97A7A",  # soft red
            "#7FB3B3",  # soft teal
            "#D9B96E",  # soft gold
            "#8FBF7A"   # soft green
        ]

        bars = ax.bar(
            svm_dvm_data.keys(),
            svm_dvm_data.values(),
            color=bar_colors,
            edgecolor="#5B0F0F"
        )

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                height,
                f"RM {height:,.0f}",
                ha="center",
                va="bottom",
                color="white",
                fontsize=11,
                fontweight="bold"
            )

        ax.tick_params(colors="white")
        ax.spines[:].set_color("white")
        ax.set_title("Kutipan Mengikut Tahun Pengajian", color="white")

        st.pyplot(fig)

    # ======================
    # TREND BULANAN
    # ======================
    st.markdown("### Trend Hasil & Perbelanjaan (Bulanan)")

    fig, ax = plt.subplots(figsize=(6, 3))
    bg_color = "#5B0F0F"
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # ===== CHECK ADA DATA ATAU TAK =====
    if not df_belanja.empty:

        df_belanja = df_belanja.dropna(subset=["Tarikh"])
        df_belanja["Bulan"] = df_belanja["Tarikh"].dt.month
        trend = df_belanja.groupby("Bulan")["Jumlah"].sum()

        ax.plot(
            trend.index,
            trend.values,
            marker="o",
            linewidth=2.5,
            color="#FFD966",
            markerfacecolor="#FFFFFF",
            markeredgecolor="#FFD966",
            markersize=6
        )

        for x, y in zip(trend.index, trend.values):
            max_val = max(trend.values) if len(trend.values) > 0 else 1
            offset = 1400 if y < max_val * 0.25 else 980
            ax.text(
                x, y,
                f"RM {y:,.0f}",
                ha="center",
                va="bottom",
                fontsize=4,
                color="#2B0000",
                bbox=dict(
                    boxstyle="round,pad=0.25",
                    facecolor="#FFE9A8",
                    edgecolor="none",
                    alpha=0.85
                )
            )

    # ===== AXIS (SENTIASA PAPAR WALAU KOSONG) =====
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(
    ["JAN","FEB","MAC","APR","MEI","JUN","JUL","OGOS","SEP","OKT","NOV","DIS"],
        fontsize=6,
    )

    ax.tick_params(colors="white", labelsize=6)

    for label in ax.get_xticklabels():
        label.set_color("white")

    for label in ax.get_yticklabels():
        label.set_color("white")

    st.pyplot(fig)
