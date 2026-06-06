
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

# ===== CSS DARK MODE =====
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0e0e0e;
        color: #ffffff;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a2e;
        border-right: 2px solid #e94560;
    }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #e94560, #c23152);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 75%;
        margin-left: auto;
        font-size: 15px;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #16213e, #1a1a2e);
        color: #e0e0e0;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 80%;
        border: 1px solid #e94560;
        font-size: 15px;
    }
    
    /* Header */
    .manga-header {
        background: linear-gradient(135deg, #e94560, #0f3460);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Cards */
    .manga-card {
        background: #16213e;
        border: 1px solid #e94560;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
    }

    .stat-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #e94560;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 5px;
    }

    /* Input */
    .stTextInput input {
        background-color: #1a1a2e !important;
        color: white !important;
        border: 1px solid #e94560 !important;
        border-radius: 25px !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #e94560, #c23152) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 8px 24px !important;
        font-weight: bold !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a2e;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #e0e0e0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e94560 !important;
        border-radius: 8px;
    }

    /* Hide streamlit branding */
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

# ===== FUNGSI CHAPTER =====
def cek_chapter_terbaru(judul):
    try:
        url = "https://api.jikan.moe/v4/manga"
        params = {"q": judul, "limit": 1}
        response = requests.get(url, params=params)
        hasil = response.json()
        time.sleep(0.5)
        if hasil["data"]:
            manga = hasil["data"][0]
            chapters = manga.get("chapters")
            if chapters and isinstance(chapters, int) and chapters > 0:
                return chapters
        # Fallback SerpAPI
        url2 = "https://serpapi.com/search"
        params2 = {"q": f"{judul} manga latest chapter 2026",
                   "api_key": SERP_API_KEY, "num": 5}
        r2 = requests.get(url2, params=params2).json()
        snippets = ""
        if "organic_results" in r2:
            for r in r2["organic_results"][:3]:
                snippets += r.get("snippet","") + " " + r.get("title","") + " "
        if snippets.strip():
            prompt = f'''Dari teks: "{snippets}"
Temukan chapter terbaru manga "{judul}".
Jawab HANYA angka bulat. Contoh: 1185. Jika tidak ada, jawab: 0'''
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"user","content":prompt}],
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
            manhwa, dan manhua. Jawab dalam Bahasa Indonesia yang santai 
            dan friendly. Gunakan emoji. Tolak topik di luar manga."""
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

data = st.session_state.data
reading_list = data.get("reading_list", [])

# ===== HEADER =====
st.markdown("""
<div class="manga-header">
    <h1>🎌 MangaBot AI</h1>
    <p style="color:#f0f0f0; margin:0">Asisten manga, manhwa & manhua favoritmu!</p>
</div>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### ⚙️ MangaBot Menu")
    st.markdown("---")
    
    # Info statistik cepat
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
        with st.spinner("Mengecek chapter terbaru..."):
            ada_update = False
            for m in reading_list:
                if m["status"] == "Sedang Baca":
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
    st.caption("Powered by Groq + Jikan API")

# ===== TABS UTAMA =====
tab1, tab2, tab3 = st.tabs(["💬 Chat AI", "📚 Reading List", "📊 Statistik"])

# ===== TAB 1: CHAT =====
with tab1:
    # Tampilkan riwayat chat
    chat_container = st.container()
    with chat_container:
        if not st.session_state.riwayat:
            st.markdown("""
            <div class="bot-message">
                🎌 Halo! Aku MangaBot, asisten manga favoritmu!<br>
                Tanya apa saja soal manga, manhwa, atau manhua ya~ 📚
            </div>
            """, unsafe_allow_html=True)
        
        for msg in st.session_state.riwayat:
            if msg["role"] == "user":
                st.markdown(f'''
                <div class="user-message">{msg["content"]}</div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="bot-message">🤖 {msg["content"]}</div>
                ''', unsafe_allow_html=True)
    
    # Input chat
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
                jawaban, riwayat_baru = tanya_ai(
                    pertanyaan, 
                    st.session_state.riwayat
                )
                st.session_state.riwayat = riwayat_baru
            st.rerun()

# ===== TAB 2: READING LIST =====
with tab2:
    col_kiri, col_kanan = st.columns([2, 1])
    
    with col_kiri:
        st.markdown("### 📚 Reading List Kamu")
        
        if not reading_list:
            st.info("📋 Reading list masih kosong! Tambah manga dulu.")
        
        # Sedang dibaca
        sedang_list = [m for m in reading_list if m["status"] == "Sedang Baca"]
        if sedang_list:
            st.markdown("**📖 Sedang Dibaca**")
            for m in sedang_list:
                ch_baca = m.get("chapter_dibaca", 0)
                ch_total = m.get("chapter_total", "?")
                ch_terbaru = m.get("chapter_terbaru", ch_total)
                
                notif = ""
                if isinstance(ch_terbaru, int) and isinstance(ch_total, int):
                    if ch_terbaru > ch_total:
                        notif = f" 🔔 Ch.{ch_terbaru} tersedia!"
                
                progress_val = 0
                if isinstance(ch_baca, int) and isinstance(ch_total, int) and ch_total > 0:
                    progress_val = min(ch_baca / ch_total, 1.0)
                
                st.markdown(f"""
                <div class="manga-card">
                    <b>📖 {m["judul"]}</b> 
                    <span style="color:#e94560">[{m.get("genre","-")}]</span>
                    {notif}<br>
                    <small>Chapter: {ch_baca}/{ch_total}</small>
                </div>
                """, unsafe_allow_html=True)
                st.progress(progress_val)
        
        # Belum dibaca
        belum_list = [m for m in reading_list if m["status"] == "Belum Baca"]
        if belum_list:
            st.markdown("**🔖 Belum Dibaca**")
            for m in belum_list:
                st.markdown(f"""
                <div class="manga-card">
                    <b>🔖 {m["judul"]}</b>
                    <span style="color:#e94560">[{m.get("genre","-")}]</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Selesai
        selesai_list = [m for m in reading_list if m["status"] == "Selesai"]
        if selesai_list:
            st.markdown("**✅ Selesai Dibaca**")
            for m in selesai_list:
                rating = f"⭐{m['rating']}/10" if m.get("rating") else ""
                st.markdown(f"""
                <div class="manga-card">
                    <b>✅ {m["judul"]}</b>
                    <span style="color:#e94560">[{m.get("genre","-")}]</span>
                    {rating}
                </div>
                """, unsafe_allow_html=True)
    
    with col_kanan:
        st.markdown("### ➕ Tambah Manga")
        with st.form("tambah_form"):
            judul = st.text_input("📖 Judul")
            genre = st.text_input("🎭 Genre")
            status = st.selectbox("📌 Status", 
                ["Belum Baca", "Sedang Baca", "Selesai"])
            ch_total = st.number_input("📚 Total Chapter", 
                min_value=0, value=0)
            ch_dibaca = 0
            if status == "Sedang Baca":
                ch_dibaca = st.number_input("📖 Sudah Baca Chapter", 
                    min_value=0, value=0)
            rating = None
            if status == "Selesai":
                rating = st.slider("⭐ Rating", 1, 10, 8)
            
            if st.form_submit_button("➕ Tambah", use_container_width=True):
                if judul:
                    manga_baru = {
                        "judul": judul,
                        "genre": genre,
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
                    st.success(f"✅ {judul} ditambahkan!")
                    st.rerun()

# ===== TAB 3: STATISTIK =====
with tab3:
    st.markdown("### 📊 Statistik Bacaan Kamu")
    
    if not reading_list:
        st.info("Belum ada data statistik!")
    else:
        # Metric cards
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
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Rating
            rated = [m for m in reading_list 
                    if m.get("rating") and str(m.get("rating","")).isdigit()]
            if rated:
                avg = sum(int(m["rating"]) for m in rated) / len(rated)
                terbaik = max(rated, key=lambda m: int(m["rating"]))
                st.markdown(f"""
                <div class="manga-card">
                    <h4>⭐ Rating</h4>
                    <p>Rata-rata: <b>{avg:.1f}/10</b></p>
                    <p>🏆 Terbaik: <b>{terbaik["judul"]} ({terbaik["rating"]}/10)</b></p>
                </div>
                """, unsafe_allow_html=True)
        
        with col_b:
            # Genre favorit
            genres = [m.get("genre","").lower() 
                     for m in reading_list if m.get("genre")]
            if genres:
                genre_count = {}
                for g in genres:
                    genre_count[g] = genre_count.get(g, 0) + 1
                favorit = max(genre_count, key=genre_count.get)
                st.markdown(f"""
                <div class="manga-card">
                    <h4>🎭 Genre</h4>
                    <p>Favorit: <b>{favorit}</b> ({genre_count[favorit]} manga)</p>
                    <p>Total genre: <b>{len(genre_count)}</b> berbeda</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Total chapter
        total_ch = sum(m.get("chapter_dibaca", 0) 
                      for m in reading_list 
                      if isinstance(m.get("chapter_dibaca"), int))
        st.markdown(f"""
        <div class="manga-card">
            <h4>📖 Progress Bacaan</h4>
            <p>Total chapter dibaca: <b>{total_ch} chapter</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        # List semua manga dengan progress bar
        st.markdown("**📈 Progress per Manga:**")
        for m in reading_list:
            if m["status"] == "Sedang Baca":
                ch_baca = m.get("chapter_dibaca", 0)
                ch_total = m.get("chapter_total", 0)
                if isinstance(ch_baca, int) and isinstance(ch_total, int) and ch_total > 0:
                    persen = int((ch_baca/ch_total)*100)
                    st.markdown(f"**{m['judul']}** — {ch_baca}/{ch_total} ({persen}%)")
                    st.progress(ch_baca/ch_total)

