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

# ===== CSS OCEAN DARK ANILIST STYLE =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    * { font-family: 'Nunito', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0b1622 0%, #0d1f3c 100%);
        color: #c9d1d9;
    }
    [data-testid="stSidebar"] {
        background: #0d1f3c;
        border-right: 2px solid #00d4ff;
    }
    .main-header {
        background: linear-gradient(135deg, #0066cc, #00d4ff);
        padding: 25px 30px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 40px rgba(0,212,255,0.3);
    }
    .main-header h1 { color: white; font-size: 2.2em; font-weight: 800; margin: 0; }
    .main-header p { color: rgba(255,255,255,0.9); margin: 5px 0 0; }

    /* Search Result Cards */
    .search-card {
        display: flex;
        background: #152032;
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 12px;
        margin: 8px 0;
        overflow: hidden;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .search-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 4px 20px rgba(0,212,255,0.2);
        transform: translateY(-2px);
    }
    .search-card img {
        width: 60px;
        height: 85px;
        object-fit: cover;
    }
    .search-card-info {
        padding: 10px 14px;
        flex: 1;
    }
    .search-card-title {
        font-weight: 700;
        color: #e0f0ff;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .search-card-meta {
        font-size: 12px;
        color: #7ab0cc;
    }

    /* Reading List Cards */
    .rl-card {
        display: flex;
        background: #152032;
        border: 1px solid rgba(0,212,255,0.15);
        border-radius: 14px;
        margin: 8px 0;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .rl-card:hover {
        border-color: rgba(0,212,255,0.5);
        box-shadow: 0 4px 20px rgba(0,212,255,0.1);
    }
    .rl-card-img {
        width: 70px;
        min-height: 100px;
        object-fit: cover;
    }
    .rl-card-body {
        padding: 10px 14px;
        flex: 1;
    }
    .rl-card-title {
        font-weight: 800;
        color: #e0f0ff;
        font-size: 15px;
        margin-bottom: 4px;
    }
    .rl-card-meta { font-size: 12px; color: #7ab0cc; }

    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        margin: 2px;
    }
    .badge-action { background: rgba(255,80,80,0.2); color: #ff8080; border: 1px solid #ff5050; }
    .badge-romance { background: rgba(255,100,180,0.2); color: #ff80c0; border: 1px solid #ff64b4; }
    .badge-fantasy { background: rgba(130,80,255,0.2); color: #b080ff; border: 1px solid #8050ff; }
    .badge-default { background: rgba(0,212,255,0.15); color: #00d4ff; border: 1px solid rgba(0,212,255,0.4); }

    .status-reading { color: #00d4ff; font-weight: 700; }
    .status-done { color: #00ff88; font-weight: 700; }
    .status-queue { color: #ffaa00; font-weight: 700; }

    .section-title {
        color: #00d4ff;
        font-size: 1.1em;
        font-weight: 800;
        padding: 8px 0;
        border-bottom: 2px solid rgba(0,212,255,0.3);
        margin: 15px 0 10px 0;
    }

    .stButton button {
        background: linear-gradient(135deg, #0066cc, #00d4ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(0,212,255,0.3) !important;
    }
    .del-btn button {
        background: linear-gradient(135deg, #cc0000, #ff4444) !important;
        font-size: 12px !important;
        border-radius: 20px !important;
    }
    .stTextInput input {
        background-color: #0d1f3c !important;
        color: #e0f0ff !important;
        border: 1px solid rgba(0,212,255,0.4) !important;
        border-radius: 12px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #0d1f3c;
        border-radius: 15px;
        padding: 5px;
        border: 1px solid rgba(0,212,255,0.2);
    }
    .stTabs [data-baseweb="tab"] { color: #7ab0cc; border-radius: 10px; font-weight: 600; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066cc, #00d4ff) !important;
        color: white !important;
    }
    .user-message {
        background: linear-gradient(135deg, #0066cc, #0099ff);
        color: white; padding: 14px 20px;
        border-radius: 20px 20px 4px 20px;
        margin: 10px 0; max-width: 75%; margin-left: auto;
        box-shadow: 0 4px 15px rgba(0,102,204,0.4);
    }
    .bot-message {
        background: #152032; color: #e0f0ff;
        padding: 14px 20px;
        border-radius: 20px 20px 20px 4px;
        margin: 10px 0; max-width: 80%;
        border: 1px solid rgba(0,212,255,0.3);
        box-shadow: 0 4px 15px rgba(0,212,255,0.1);
    }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: 800 !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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

def cek_duplikat(judul, reading_list):
    return any(m["judul"].lower() == judul.lower() for m in reading_list)

def get_badge_class(genre):
    g = genre.lower()
    if "action" in g: return "badge-action"
    if "romance" in g: return "badge-romance"
    if "fantasy" in g or "supernatural" in g: return "badge-fantasy"
    return "badge-default"

# ===== FUNGSI JIKAN API =====
def search_manga(query, limit=6):
    """Search manga dari Jikan API"""
    try:
        url = "https://api.jikan.moe/v4/manga"
        params = {"q": query, "limit": limit}
        r = requests.get(url, params=params)
        hasil = r.json()
        time.sleep(0.3)
        if hasil.get("data"):
            results = []
            for m in hasil["data"]:
                genres = [g["name"] for g in m.get("genres", [])]
                cover = m.get("images", {}).get("jpg", {}).get("image_url", "")
                results.append({
                    "mal_id": m.get("mal_id"),
                    "judul": m.get("title", ""),
                    "judul_en": m.get("title_english", ""),
                    "tipe": m.get("type", "Manga"),
                    "chapters": m.get("chapters"),
                    "volumes": m.get("volumes"),
                    "status": m.get("status", ""),
                    "score": m.get("score"),
                    "genre": ", ".join(genres),
                    "cover": cover,
                    "synopsis": m.get("synopsis", "")[:150] + "..." if m.get("synopsis") else ""
                })
            return results
    except Exception as e:
        st.error(f"Error: {e}")
    return []

def cek_chapter_terbaru(judul):
    try:
        results = search_manga(judul, limit=1)
        if results and results[0]["chapters"]:
            return results[0]["chapters"]
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

# ===== INISIALISASI SESSION =====
if "riwayat" not in st.session_state:
    st.session_state.riwayat = []
if "data" not in st.session_state:
    st.session_state.data = muat_data()
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "selected_manga" not in st.session_state:
    st.session_state.selected_manga = None

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
    st.markdown("### 🌊 MangaBot")
    st.markdown("---")
    selesai_s = len([m for m in reading_list if m["status"] == "Selesai"])
    sedang_s = len([m for m in reading_list if m["status"] == "Sedang Baca"])
    belum_s = len([m for m in reading_list if m["status"] == "Belum Baca"])
    col1, col2, col3 = st.columns(3)
    col1.metric("✅", selesai_s, "Selesai")
    col2.metric("📖", sedang_s, "Baca")
    col3.metric("🔖", belum_s, "Antri")
    st.markdown("---")
    if st.button("🔄 Cek Update Chapter", use_container_width=True):
        with st.spinner("Mengecek..."):
            ada_update = False
            for m in reading_list:
                if m["status"] == "Sedang Baca" and m.get("tipe") not in ["Novel", "Light Novel"]:
                    ch_baru = cek_chapter_terbaru(m["judul"])
                    if ch_baru:
                        ch_lama = m.get("chapter_total", 0)
                        if isinstance(ch_lama, int) and ch_baru > ch_lama:
                            m["chapter_total"] = ch_baru
                            ada_update = True
                            st.success(f"🔔 {m['judul']}: →Ch.{ch_baru}!")
            if ada_update:
                data["reading_list"] = reading_list
                simpan_data(data)
                st.session_state.data = data
            else:
                st.info("✅ Up-to-date!")
    st.markdown("---")
    st.caption("🌊 Powered by Groq + Jikan API")

# ===== TABS =====
tab1, tab2, tab3 = st.tabs(["💬 Chat AI", "📚 Reading List", "📊 Statistik"])

# ===== TAB 1: CHAT =====
with tab1:
    if not st.session_state.riwayat:
        st.markdown("""
        <div class="bot-message">
            🌊 Halo! Aku MangaBot!<br>
            Tanya soal manga, manhwa, manhua, light novel, atau novel ya~ 📚
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
            with st.spinner("Berpikir..."):
                jawaban, riwayat_baru = tanya_ai(pertanyaan, st.session_state.riwayat)
                st.session_state.riwayat = riwayat_baru
            st.rerun()

# ===== TAB 2: READING LIST =====
with tab2:
    # ===== SEARCH BAR =====
    st.markdown("### 🔍 Cari & Tambah")
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        query = st.text_input("",
            placeholder="Cari manga, manhwa, manhua, novel...",
            label_visibility="collapsed",
            key="search_input")
    with col_btn:
        if st.button("🔍 Cari", use_container_width=True):
            if query:
                with st.spinner("Mencari..."):
                    st.session_state.search_results = search_manga(query, limit=6)

    # ===== HASIL SEARCH =====
    if st.session_state.search_results:
        st.markdown('<div class="section-title">🔍 Hasil Pencarian</div>',
                   unsafe_allow_html=True)
        for idx, manga in enumerate(st.session_state.search_results):
            col_img, col_info, col_add = st.columns([1, 5, 2])

            with col_img:
                if manga["cover"]:
                    st.image(manga["cover"], width=60)

            with col_info:
                genres = manga["genre"].split(", ")[:3] if manga["genre"] else []
                badges = " ".join([
                    f'<span class="badge {get_badge_class(g)}">{g}</span>'
                    for g in genres if g
                ])
                ch_info = f"Ch.{manga['chapters']}" if manga.get('chapters') else "Ongoing"
                score = f"⭐{manga['score']}" if manga.get('score') else ""
                tipe = manga.get("tipe", "Manga")

                st.markdown(f"""
                <div style="padding: 5px 0">
                    <div style="font-weight:800; color:#e0f0ff; font-size:14px">
                        {manga['judul']}
                    </div>
                    <div style="font-size:12px; color:#7ab0cc; margin: 3px 0">
                        {tipe} • {ch_info} • {score}
                    </div>
                    <div>{badges}</div>
                    <div style="font-size:11px; color:#5a8099; margin-top:4px">
                        {manga['synopsis']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_add:
                if cek_duplikat(manga["judul"], reading_list):
                    st.markdown("✅ *Ada*")
                else:
                    if st.button("➕ Tambah", key=f"add_{idx}"):
                        st.session_state.selected_manga = manga
                        st.rerun()

        st.markdown("---")

    # ===== FORM TAMBAH (setelah pilih dari search) =====
    if st.session_state.selected_manga:
        m = st.session_state.selected_manga
        st.markdown(f'<div class="section-title">➕ Tambah: {m["judul"]}</div>',
                   unsafe_allow_html=True)

        col_cover, col_form = st.columns([1, 3])
        with col_cover:
            if m.get("cover"):
                st.image(m["cover"], width=100)

        with col_form:
            with st.form("form_tambah_selected"):
                tipe_options = ["Manga", "Manhwa", "Manhua", "Light Novel", "Novel"]
                default_tipe = m.get("tipe", "Manga")
                if default_tipe not in tipe_options:
                    default_tipe = "Manga"
                tipe = st.selectbox("Tipe", tipe_options,
                    index=tipe_options.index(default_tipe))

                genre_val = m.get("genre", "")
                genre = st.text_input("Genre", value=genre_val)

                status = st.selectbox("Status",
                    ["Belum Baca", "Sedang Baca", "Selesai"])

                label_ch = "Volume" if tipe in ["Novel", "Light Novel"] else "Chapter"
                default_ch = m.get("chapters") or 0
                ch_total = st.number_input(f"Total {label_ch}",
                    min_value=0, value=int(default_ch) if default_ch else 0)

                ch_dibaca = 0
                if status == "Sedang Baca":
                    ch_dibaca = st.number_input(f"Sudah Baca {label_ch}",
                        min_value=0, value=0)

                rating = None
                if status == "Selesai":
                    rating = st.slider("Rating", 1, 10, 8)

                col_save, col_cancel = st.columns(2)
                with col_save:
                    simpan = st.form_submit_button("✅ Simpan", use_container_width=True)
                with col_cancel:
                    batal = st.form_submit_button("❌ Batal", use_container_width=True)

                if simpan:
                    manga_baru = {
                        "judul": m["judul"],
                        "tipe": tipe,
                        "genre": genre,
                        "status": status,
                        "chapter_dibaca": ch_dibaca,
                        "chapter_total": int(ch_total) if ch_total > 0 else "?",
                        "chapter_terbaru": int(ch_total) if ch_total > 0 else "?",
                        "rating": str(rating) if rating else None,
                        "cover": m.get("cover", ""),
                        "mal_id": m.get("mal_id"),
                        "terakhir_update": datetime.now().strftime("%d/%m/%Y")
                    }
                    reading_list.append(manga_baru)
                    data["reading_list"] = reading_list
                    simpan_data(data)
                    st.session_state.data = data
                    st.session_state.selected_manga = None
                    st.session_state.search_results = []
                    st.success(f"✅ '{m['judul']}' ditambahkan!")
                    st.rerun()

                if batal:
                    st.session_state.selected_manga = None
                    st.rerun()

    # ===== READING LIST =====
    st.markdown("### 📚 Reading List")

    if not reading_list:
        st.info("📋 Reading list kosong! Cari manga di atas yuk~")

    def render_list(items, status_class, status_label):
        for i, m in enumerate(items):
            col_img, col_body, col_del = st.columns([1, 6, 1])
            genres = m.get("genre", "").split(", ")[:3] if m.get("genre") else []
            badges = " ".join([
                f'<span class="badge {get_badge_class(g)}">{g}</span>'
                for g in genres if g
            ])
            tipe = m.get("tipe", "Manga")
            tipe_icon = {"Manga": "📖", "Manhwa": "📗", "Manhua": "📘",
                        "Light Novel": "📒", "Novel": "📕"}.get(tipe, "📖")
            ch_baca = m.get("chapter_dibaca", 0)
            ch_total = m.get("chapter_total", "?")
            label = "Vol" if tipe in ["Novel", "Light Novel"] else "Ch"
            rating = f" • ⭐{m['rating']}/10" if m.get("rating") else ""

            with col_img:
                if m.get("cover"):
                    st.image(m["cover"], width=65)
                else:
                    st.markdown(f"""
                    <div style="width:65px;height:90px;background:#0d1f3c;
                    border:1px solid #00d4ff;border-radius:8px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:24px">{tipe_icon}</div>
                    """, unsafe_allow_html=True)

            with col_body:
                if status_label == "Sedang Baca":
                    progress_val = 0
                    if isinstance(ch_baca, int) and isinstance(ch_total, int) and ch_total > 0:
                        progress_val = min(ch_baca / ch_total, 1.0)
                    persen = int(progress_val * 100)
                    st.markdown(f"""
                    <div style="padding:5px 0">
                        <div style="font-weight:800;color:#e0f0ff">{m['judul']}</div>
                        <div style="font-size:12px;color:#7ab0cc">{tipe}</div>
                        <div>{badges}</div>
                        <div class="{status_class}" style="font-size:13px;margin-top:4px">
                            ● {label}.{ch_baca}/{ch_total} ({persen}%)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(progress_val)
                else:
                    st.markdown(f"""
                    <div style="padding:5px 0">
                        <div style="font-weight:800;color:#e0f0ff">{m['judul']}</div>
                        <div style="font-size:12px;color:#7ab0cc">{tipe}</div>
                        <div>{badges}</div>
                        <div class="{status_class}" style="font-size:13px;margin-top:4px">
                            ● {status_label}{rating}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_del:
                st.markdown('<div class="del-btn">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{status_label}_{i}_{m['judul']}"):
                    reading_list.remove(m)
                    data["reading_list"] = reading_list
                    simpan_data(data)
                    st.session_state.data = data
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    sedang_list = [m for m in reading_list if m["status"] == "Sedang Baca"]
    belum_list = [m for m in reading_list if m["status"] == "Belum Baca"]
    selesai_list = [m for m in reading_list if m["status"] == "Selesai"]

    if sedang_list:
        st.markdown('<div class="section-title">📖 Sedang Dibaca</div>',
                   unsafe_allow_html=True)
        render_list(sedang_list, "status-reading", "Sedang Baca")

    if belum_list:
        st.markdown('<div class="section-title">🔖 Belum Dibaca</div>',
                   unsafe_allow_html=True)
        render_list(belum_list, "status-queue", "Belum Dibaca")

    if selesai_list:
        st.markdown('<div class="section-title">✅ Selesai</div>',
                   unsafe_allow_html=True)
        render_list(selesai_list, "status-done", "Selesai")

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
        if tipe_count:
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
                col_tb, col_info = st.columns([1, 3])
                with col_tb:
                    if terbaik.get("cover"):
                        st.image(terbaik["cover"], width=60)
                with col_info:
                    st.markdown(f"""
                    <div style="background:#152032;border:1px solid rgba(0,212,255,0.3);
                    border-radius:12px;padding:12px">
                        <div class="section-title">⭐ Rating</div>
                        <p>Rata-rata: <b>{avg:.1f}/10</b></p>
                        <p>🏆 <b>{terbaik['judul']}</b><br>({terbaik['rating']}/10)</p>
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
                                   key=lambda x: x[1], reverse=True)[:5]
                genre_html = "".join([
                    f'<span class="badge {get_badge_class(g)}">{g} ({c})</span> '
                    for g, c in top_genres
                ])
                st.markdown(f"""
                <div style="background:#152032;border:1px solid rgba(0,212,255,0.3);
                border-radius:12px;padding:12px">
                    <div class="section-title">🎭 Top Genre</div>
                    {genre_html}
                </div>
                """, unsafe_allow_html=True)

        total_ch = sum(m.get("chapter_dibaca", 0)
                      for m in reading_list
                      if isinstance(m.get("chapter_dibaca"), int))
        st.markdown(f"""
        <div style="background:#152032;border:1px solid rgba(0,212,255,0.3);
        border-radius:12px;padding:12px;margin-top:10px">
            <div class="section-title">📖 Total Dibaca</div>
            <p style="font-size:1.5em;font-weight:800;color:#00d4ff">
                {total_ch} <span style="font-size:0.6em;color:#7ab0cc">chapter/volume</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

        sedang_progress = [m for m in reading_list
                          if m["status"] == "Sedang Baca"
                          and isinstance(m.get("chapter_dibaca"), int)
                          and isinstance(m.get("chapter_total"), int)
                          and m.get("chapter_total", 0) > 0]
        if sedang_progress:
            st.markdown('<div class="section-title">📈 Progress</div>',
                       unsafe_allow_html=True)
            for m in sedang_progress:
                ch_baca = m["chapter_dibaca"]
                ch_total = m["chapter_total"]
                persen = int((ch_baca / ch_total) * 100)
                tipe = m.get("tipe", "Manga")
                label = "Vol" if tipe in ["Novel", "Light Novel"] else "Ch"
                col_cov, col_prog = st.columns([1, 5])
                with col_cov:
                    if m.get("cover"):
                        st.image(m["cover"], width=40)
                with col_prog:
                    st.markdown(f"**{m['judul']}** — {label}.{ch_baca}/{ch_total} ({persen}%)")
                    st.progress(ch_baca / ch_total)
