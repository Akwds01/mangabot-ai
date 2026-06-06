import streamlit as st
import json
import os
import requests
import time
import re
from groq import Groq
from datetime import datetime

# ===== KONFIGURASI =====
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SERP_API_KEY = st.secrets["SERP_API_KEY"]
FILE_DATA = "mangabot_data.json"

client = Groq(api_key=GROQ_API_KEY)

# ===== CSS OCEAN DARK =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Nunito', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #020818 0%, #0a1628 50%, #020818 100%);
        color: #e0f0ff;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628 0%, #0d1f3c 100%);
        border-right: 2px solid #00d4ff;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0066cc, #00d4ff, #0099ff);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 0 40px rgba(0, 212, 255, 0.3);
        border: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5em;
        font-weight: 800;
        color: white;
        text-shadow: 0 0 20px rgba(255,255,255,0.5);
        margin: 0;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 5px 0 0 0;
        font-size: 1.1em;
    }

    .user-message {
        background: linear-gradient(135deg, #0066cc, #0099ff);
        color: white;
        padding: 14px 20px;
        border-radius: 20px 20px 4px 20px;
        margin: 10px 0;
        max-width: 75%;
        margin-left: auto;
        font-size: 15px;
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.4);
    }
    
    .bot-message {
        background: linear-gradient(135deg, #0a1628, #0d1f3c);
        color: #e0f0ff;
        padding: 14px 20px;
        border-radius: 20px 20px 20px 4px;
        margin: 10px 0;
        max-width: 80%;
        border: 1px solid rgba(0, 212, 255, 0.4);
        font-size: 15px;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.1);
    }

    .manga-card {
        background: linear-gradient(135deg, #0a1628, #0d1f3c);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 15px 18px;
        margin: 8px 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .manga-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.2);
    }

    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin: 2px;
    }

    .badge-action { background: rgba(255,80,80,0.2); color: #ff8080; border: 1px solid #ff5050; }
    .badge-romance { background: rgba(255,100,180,0.2); color: #ff80c0; border: 1px solid #ff64b4; }
    .badge-fantasy { background: rgba(130,80,255,0.2); color: #b080ff; border: 1px solid #8050ff; }
    .badge-default { background: rgba(0,212,255,0.2); color: #00d4ff; border: 1px solid #00d4ff; }
    
    .status-reading { color: #00d4ff; font-weight: 700; }
    .status-done { color: #00ff88; font-weight: 700; }
    .status-queue { color: #ffaa00; font-weight: 700; }

    .section-title {
        color: #00d4ff;
        font-size: 1.1em;
        font-weight: 800;
        padding: 8px 0;
        border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        margin: 15px 0 10px 0;
    }

    .stButton button {
        background: linear-gradient(135deg, #0066cc, #00d4ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        box-shadow: 0 4px 25px rgba(0, 212, 255, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    .stTextInput input, .stSelectbox select {
        background-color: #0a1628 !important;
        color: #e0f0ff !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #0a1628;
        border-radius: 15px;
        padding: 5px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }

    .stTabs [data-baseweb="tab"] {
        color: #7ab0cc;
        border-radius: 10px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066cc, #00d4ff) !important;
        color: white !important;
    }

    .delete-btn button {
        background: linear-gradient(135deg, #cc0000, #ff4444) !important;
        font-size: 12px !important;
        padding: 4px 12px !important;
        border-radius: 20px !important;
        box-shadow: 0 2px 8px rgba(255,0,0,0.3) !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

# ===== FUNGSI DATA =====
def muat_data():
    if os.path.exists(FILE_DATA):
        with open(FILE_DATA, "r") as f:
            return json.load(f)
    return {"reading_list": []}

def simpan_data(data):
    with open(FILE_DATA, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ===== FUNGSI JIKAN API =====
def cari_info_manga(judul):
    """Ambil info lengkap manga dari Jikan API"""
    try:
        url = "https://api.jikan.moe/v4/manga"
        params = {"q": judul, "limit": 1}
        response = requests.get(url, params=params)
        hasil = response.json()
        time.sleep(0.5)
        if hasil["data"]:
            manga = hasil["data"][0]
            genres = [g["name"] for g in manga.get("genres", [])]
            genre_str = ", ".join(genres) if genres else ""
            return {
                "chapters": manga.get("chapters"),
                "status": manga.get("status", ""),
                "genre": genre_str,
                "score": manga.get("score"),
                "mal_id": manga.get("mal_id"),
                "type": manga.get("type", "")
            }
    except:
        pass
    return None

def cek_chapter_terbaru(judul):
    """Cek chapter terbaru via Jikan + SerpAPI"""
    try:
        info = cari_info_manga(judul)
        if info and info["chapters"] and isinstance(info["chapters"], int):
            return info["chapters"]
        # Fallback SerpAPI
        url2 = "https://serpapi.com/search"
        params2 = {"q": f"{judul} manga latest chapter 2026",
                   "api_key": SERP_API_KEY, "num": 5}
        r2 = requests.get(url2, params=params2).json()
        snippets = ""
        if "organic_results" in r2:
            for r in r2["organic_results"][:3]:
                snippets += r.get("snippet", "") + " " + r.get("title", "") + " "
        if snippets.strip():
            prompt = f"""Dari teks: "{snippets}"
Temukan chapter terbaru manga "{judul}".
Jawab HANYA angka bulat. Contoh: 1185. Jika tidak ada, jawab: 0"""
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10)
            angka = re.findall(r"\d+", resp.choices[0].message.content.strip())
            if angka:
                return int(angka[0])
        return None
    except:
        return None

# ===== FUNGSI AI =====
def tanya_ai(pertanyaan, riwayat):
    riwayat.append({"role": "user", "content": pertanyaan})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "system",
            "content": """Kamu adalah MangaBot, asisten AI expert manga, 
            manhwa, manhua, light novel, dan novel. 
            Jawab dalam Bahasa Indonesia yang santai dan friendly. 
            Gunakan emoji. Tolak topik di luar manga/novel."""
        }] + riwayat,
        max_tokens=1000
    )
    jawaban = response.choices[0].message.content
    riwayat.append({"role": "assistant", "content": jawaban})
    return jawaban, riwayat

def get_badge_class(genre):
    genre_lower = genre.lower()
    if "action" in genre_lower: return "badge-action"
    if "romance" in genre_lower: return "badge-romance"
    if "fantasy" in genre_lower or "supernatural" in genre_lower: return "badge-fantasy"
    return "badge-default"

def cek_duplikat(judul, reading_list):
    return any(m["judul"].lower() == judul.lower() for m in reading_list)

# ===== INISIALISASI SESSION =====
if "riwayat" not in st.session_state:
    st.session_state.riwayat = []
if "data" not in st.session_state:
    st.session_state.data = muat_data()
if "hapus_konfirmasi" not in st.session_state:
    st.session_state.hapus_konfirmasi = None

data = st.session_state.data
reading_list = data.get("reading_list", [])

# ===== HEADER =====
st.markdown("""
<div class="main-header">
    <h1>🌊 MangaBot AI</h1>
    <p>Asisten manga, manhwa, manhua & novel favoritmu!</p>
</div>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### 🌊 MangaBot Menu")
    st.markdown("---")

    selesai = len([m for m in reading_list if m["status"] == "Selesai"])
    sedang = len([m for m in reading_list if m["status"] == "Sedang Baca"])
    belum = len([m for m in reading_list if m["status"] == "Belum Baca"])

    col1, col2, col3 = st.columns(3)
    col1.metric("✅", selesai, "Selesai")
    col2.metric("📖", sedang, "Baca")
    col3.metric("🔖", belum, "Antri")

    st.markdown("---")
    st.markdown("**🔔 Cek Update Chapter**")
    if st.button("🔄 Update Semua", use_container_width=True):
        with st.spinner("Mengecek update..."):
            ada_update = False
            for m in reading_list:
                if m["status"] == "Sedang Baca" and m.get("tipe") not in ["Novel", "Light Novel"]:
                    ch_baru = cek_chapter_terbaru(m["judul"])
                    if ch_baru:
                        ch_lama = m.get("chapter_total", 0)
                        if isinstance(ch_lama, int) and ch_baru > ch_lama:
                            m["chapter_total"] = ch_baru
                            m["chapter_terbaru"] = ch_baru
                            ada_update = True
                            st.success(f"🔔 {m['judul']}: Ch.{ch_lama}→{ch_baru}!")
            if ada_update:
                data["reading_list"] = reading_list
                simpan_data(data)
                st.session_state.data = data
            else:
                st.info("✅ Semua sudah up-to-date!")

    st.markdown("---")
    st.caption("🌊 Powered by Groq + Jikan API")

# ===== TABS =====
tab1, tab2, tab3 = st.tabs(["💬 Chat AI", "📚 Reading List", "📊 Statistik"])

# ===== TAB 1: CHAT =====
with tab1:
    if not st.session_state.riwayat:
        st.markdown("""
        <div class="bot-message">
            🌊 Halo! Aku MangaBot, asisten manga & novel favoritmu!<br>
            Tanya apa saja soal manga, manhwa, manhua, light novel, atau novel ya~ 📚
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.riwayat:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{msg["content"]}</div>',
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">🤖 {msg["content"]}</div>',
                       unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            pertanyaan = st.text_input("",
                placeholder="Tanya soal manga, rekomendasi, chapter terbaru...",
                label_visibility="collapsed")
        with col2:
            kirim = st.form_submit_button("Send 🚀")

        if kirim and pertanyaan:
            with st.spinner("MangaBot sedang berpikir..."):
                jawaban, riwayat_baru = tanya_ai(pertanyaan, st.session_state.riwayat)
                st.session_state.riwayat = riwayat_baru
            st.rerun()

# ===== TAB 2: READING LIST =====
with tab2:
    col_kiri, col_kanan = st.columns([3, 2])

    with col_kiri:
        st.markdown("### 📚 Reading List Kamu")

        if not reading_list:
            st.info("📋 Reading list masih kosong! Tambah dulu yuk~")

        # Sedang dibaca
        sedang_list = [m for m in reading_list if m["status"] == "Sedang Baca"]
        if sedang_list:
            st.markdown('<div class="section-title">📖 Sedang Dibaca</div>',
                       unsafe_allow_html=True)
            for i, m in enumerate(sedang_list):
                ch_baca = m.get("chapter_dibaca", 0)
                ch_total = m.get("chapter_total", "?")
                tipe = m.get("tipe", "Manga")
                tipe_icon = {"Manga": "📖", "Manhwa": "📗", "Manhua": "📘",
                            "Light Novel": "📒", "Novel": "📕"}.get(tipe, "📖")

                genres = m.get("genre", "").split(", ") if m.get("genre") else []
                genre_badges = " ".join([
                    f'<span class="badge {get_badge_class(g)}">{g}</span>'
                    for g in genres[:3] if g
                ])

                progress_val = 0
                ch_label = f"Ch.{ch_baca}/{ch_total}"
                if tipe in ["Novel", "Light Novel"]:
                    ch_label = f"Vol.{ch_baca}/{ch_total}"
                if isinstance(ch_baca, int) and isinstance(ch_total, int) and ch_total > 0:
                    progress_val = min(ch_baca / ch_total, 1.0)

                col_card, col_del = st.columns([5, 1])
                with col_card:
                    st.markdown(f"""
                    <div class="manga-card">
                        <b>{tipe_icon} {m["judul"]}</b><br>
                        {genre_badges}<br>
                        <small class="status-reading">● {ch_label}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    if progress_val > 0:
                        st.progress(progress_val)
                with col_del:
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_sedang_{i}",
                                help=f"Hapus {m['judul']}"):
                        reading_list.remove(m)
                        data["reading_list"] = reading_list
                        simpan_data(data)
                        st.session_state.data = data
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        # Belum dibaca
        belum_list = [m for m in reading_list if m["status"] == "Belum Baca"]
        if belum_list:
            st.markdown('<div class="section-title">🔖 Belum Dibaca</div>',
                       unsafe_allow_html=True)
            for i, m in enumerate(belum_list):
                tipe = m.get("tipe", "Manga")
                tipe_icon = {"Manga": "📖", "Manhwa": "📗", "Manhua": "📘",
                            "Light Novel": "📒", "Novel": "📕"}.get(tipe, "📖")
                genres = m.get("genre", "").split(", ") if m.get("genre") else []
                genre_badges = " ".join([
                    f'<span class="badge {get_badge_class(g)}">{g}</span>'
                    for g in genres[:3] if g
                ])
                col_card, col_del = st.columns([5, 1])
                with col_card:
                    st.markdown(f"""
                    <div class="manga-card">
                        <b>{tipe_icon} {m["judul"]}</b><br>
                        {genre_badges}
                        <small class="status-queue"> ● Belum Dibaca</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_belum_{i}",
                                help=f"Hapus {m['judul']}"):
                        reading_list.remove(m)
                        data["reading_list"] = reading_list
                        simpan_data(data)
                        st.session_state.data = data
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        # Selesai
        selesai_list = [m for m in reading_list if m["status"] == "Selesai"]
        if selesai_list:
            st.markdown('<div class="section-title">✅ Selesai Dibaca</div>',
                       unsafe_allow_html=True)
            for i, m in enumerate(selesai_list):
                tipe = m.get("tipe", "Manga")
                tipe_icon = {"Manga": "📖", "Manhwa": "📗", "Manhua": "📘",
                            "Light Novel": "📒", "Novel": "📕"}.get(tipe, "📖")
                genres = m.get("genre", "").split(", ") if m.get("genre") else []
                genre_badges = " ".join([
                    f'<span class="badge {get_badge_class(g)}">{g}</span>'
                    for g in genres[:3] if g
                ])
                rating = f"⭐ {m['rating']}/10" if m.get("rating") else ""
                col_card, col_del = st.columns([5, 1])
                with col_card:
                    st.markdown(f"""
                    <div class="manga-card">
                        <b>{tipe_icon} {m["judul"]}</b><br>
                        {genre_badges}<br>
                        <small class="status-done">● Selesai {rating}</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_selesai_{i}",
                                help=f"Hapus {m['judul']}"):
                        reading_list.remove(m)
                        data["reading_list"] = reading_list
                        simpan_data(data)
                        st.session_state.data = data
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with col_kanan:
        st.markdown("### ➕ Tambah Baru")
        with st.form("tambah_form"):
            judul = st.text_input("📖 Judul")

            tipe = st.selectbox("📌 Tipe",
                ["Manga", "Manhwa", "Manhua", "Light Novel", "Novel"])

            # Tombol auto-isi genre
            genre = st.text_input("🎭 Genre",
                placeholder="Ketik manual atau klik Auto-Fill")
            auto_fill = st.form_submit_button("🔍 Auto-Fill Info dari MAL")

            status = st.selectbox("📌 Status",
                ["Belum Baca", "Sedang Baca", "Selesai"])

            label_ch = "Volume" if tipe in ["Novel", "Light Novel"] else "Chapter"
            ch_total = st.number_input(f"📚 Total {label_ch}", min_value=0, value=0)
            ch_dibaca = 0
            if status == "Sedang Baca":
                ch_dibaca = st.number_input(f"📖 Sudah Baca {label_ch}",
                    min_value=0, value=0)
            rating = None
            if status == "Selesai":
                rating = st.slider("⭐ Rating", 1, 10, 8)

            tambah = st.form_submit_button("➕ Tambah", use_container_width=True)

            # Auto-fill info
            if auto_fill and judul:
                with st.spinner(f"Mencari info {judul}..."):
                    info = cari_info_manga(judul)
                    if info:
                        st.success(f"✅ Info ditemukan!")
                        if info.get("genre"):
                            st.info(f"🎭 Genre: {info['genre']}")
                        if info.get("chapters"):
                            st.info(f"📚 Total chapter: {info['chapters']}")
                        if info.get("score"):
                            st.info(f"⭐ MAL Score: {info['score']}")
                    else:
                        st.warning("⚠️ Info tidak ditemukan di MAL")

            # Tambah manga
            if tambah and judul:
                if cek_duplikat(judul, reading_list):
                    st.error(f"⚠️ '{judul}' sudah ada di reading list!")
                else:
                    # Auto-fill genre kalau kosong
                    genre_final = genre
                    if not genre_final:
                        with st.spinner("Auto-fill genre..."):
                            info = cari_info_manga(judul)
                            if info and info.get("genre"):
                                genre_final = info["genre"]
                                if info.get("chapters") and ch_total == 0:
                                    ch_total = info["chapters"]

                    manga_baru = {
                        "judul": judul,
                        "tipe": tipe,
                        "genre": genre_final,
                        "status": status,
                        "chapter_dibaca": ch_dibaca,
                        "chapter_total": int(ch_total) if ch_total > 0 else "?",
                        "chapter_terbaru": int(ch_total) if ch_total > 0 else "?",
                        "rating": str(rating) if rating else None,
                        "terakhir_update": datetime.now().strftime("%d/%m/%Y")
                    }
                    reading_list.append(manga_baru)
                    data["reading_list"] = reading_list
                    simpan_data(data)
                    st.session_state.data = data
                    st.success(f"✅ '{judul}' berhasil ditambahkan!")
                    st.rerun()

# ===== TAB 3: STATISTIK =====
with tab3:
    st.markdown("### 📊 Statistik Bacaan")

    if not reading_list:
        st.info("Belum ada data!")
    else:
        total = len(reading_list)
        selesai_n = len([m for m in reading_list if m["status"] == "Selesai"])
        sedang_n = len([m for m in reading_list if m["status"] == "Sedang Baca"])
        belum_n = len([m for m in reading_list if m["status"] == "Belum Baca"])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📚 Total", total)
        col2.metric("✅ Selesai", selesai_n)
        col3.metric("📖 Sedang", sedang_n)
        col4.metric("🔖 Antri", belum_n)

        st.markdown("---")

        # Tipe breakdown
        tipe_count = {}
        for m in reading_list:
            t = m.get("tipe", "Manga")
            tipe_count[t] = tipe_count.get(t, 0) + 1

        tipe_icons = {"Manga": "📖", "Manhwa": "📗", "Manhua": "📘",
                     "Light Novel": "📒", "Novel": "📕"}
        cols = st.columns(len(tipe_count))
        for i, (tipe, count) in enumerate(tipe_count.items()):
            cols[i].metric(f"{tipe_icons.get(tipe,'📖')} {tipe}", count)

        st.markdown("---")

        col_a, col_b = st.columns(2)
        with col_a:
            rated = [m for m in reading_list
                    if m.get("rating") and str(m.get("rating", "")).isdigit()]
            if rated:
                avg = sum(int(m["rating"]) for m in rated) / len(rated)
                terbaik = max(rated, key=lambda m: int(m["rating"]))
                st.markdown(f"""
                <div class="manga-card">
                    <div class="section-title">⭐ Rating</div>
                    <p>Rata-rata: <b>{avg:.1f}/10</b></p>
                    <p>🏆 Terbaik: <b>{terbaik["judul"]} ({terbaik["rating"]}/10)</b></p>
                </div>
                """, unsafe_allow_html=True)

        with col_b:
            all_genres = []
            for m in reading_list:
                if m.get("genre"):
                    for g in m["genre"].split(", "):
                        if g.strip():
                            all_genres.append(g.strip())
            if all_genres:
                genre_count = {}
                for g in all_genres:
                    genre_count[g] = genre_count.get(g, 0) + 1
                top_genres = sorted(genre_count.items(),
                                   key=lambda x: x[1], reverse=True)[:3]
                genre_html = "".join([
                    f'<span class="badge {get_badge_class(g)}">{g} ({c})</span> '
                    for g, c in top_genres
                ])
                st.markdown(f"""
                <div class="manga-card">
                    <div class="section-title">🎭 Top Genre</div>
                    {genre_html}
                </div>
                """, unsafe_allow_html=True)

        # Progress bar
        total_ch = sum(m.get("chapter_dibaca", 0)
                      for m in reading_list
                      if isinstance(m.get("chapter_dibaca"), int))
        st.markdown(f"""
        <div class="manga-card">
            <div class="section-title">📖 Total Dibaca</div>
            <p><b>{total_ch}</b> chapter/volume</p>
        </div>
        """, unsafe_allow_html=True)

        sedang_progress = [m for m in reading_list
                          if m["status"] == "Sedang Baca"
                          and isinstance(m.get("chapter_dibaca"), int)
                          and isinstance(m.get("chapter_total"), int)
                          and m.get("chapter_total", 0) > 0]
        if sedang_progress:
            st.markdown('<div class="section-title">📈 Progress per Judul</div>',
                       unsafe_allow_html=True)
            for m in sedang_progress:
                ch_baca = m["chapter_dibaca"]
                ch_total = m["chapter_total"]
                persen = int((ch_baca / ch_total) * 100)
                tipe = m.get("tipe", "Manga")
                label = "Vol" if tipe in ["Novel", "Light Novel"] else "Ch"
                st.markdown(f"**{m['judul']}** — {label}.{ch_baca}/{ch_total} ({persen}%)")
                st.progress(ch_baca / ch_total)
