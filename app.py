import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import sys
import os
import re

# --- প্রিমিয়াম পৃষ্ঠা কনফিগারেশন ---
st.set_page_config(
    page_title="SEU MATRIX SCANNER",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- আল্ট্রা-মডার্ন সাইবারপাঙ্ক UI/UX স্টাইলিং (CSS) ---
st.markdown("""
    <style>
        /* মূল ব্যাকগ্রাউন্ড ও গ্লোবাল ফন্ট */
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@300;500;700&display=swap');
        
        .stApp {
            background: radial-gradient(circle at 50% 10%, #111827 0%, #030712 100%);
            font-family: 'Inter', sans-serif;
            color: #E5E7EB;
        }
        
        /* গ্লোয়িং হেডার টাইটেল */
        .title-container {
            text-align: center;
            padding: 20px 0 10px 0;
            margin-bottom: 25px;
        }
        .main-title {
            font-family: 'Fira Code', monospace;
            font-weight: 700;
            font-size: 2.8rem;
            background: linear-gradient(90deg, #00FF66 0%, #00E5FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0px 0px 20px rgba(0, 255, 102, 0.3);
            letter-spacing: -1px;
        }
        .engine-badge {
            background: rgba(0, 255, 102, 0.1);
            border: 1px solid rgba(0, 255, 102, 0.3);
            color: #00FF66;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-family: 'Fira Code', monospace;
            display: inline-block;
            margin-top: 10px;
            box-shadow: 0 0 15px rgba(0, 255, 102, 0.1);
        }
        
        /* গ্লাসিয়াল মডার্ন কার্ড (Glassmorphism) */
        .glass-card {
            background: rgba(17, 24, 39, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        /* মডার্ন সাইবার টার্মিনাল বক্স */
        .terminal-box {
            background: #05070f !important;
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            color: #00FF66 !important;
            font-family: 'Fira Code', monospace !important;
            font-size: 14px !important;
            line-height: 1.6;
            overflow-y: auto;
            max-height: 400px;
            box-shadow: inset 0 0 20px rgba(0, 229, 255, 0.05);
        }
        
        /* কাস্টম ইনপুট ও বাটন স্টাইলিং ওভাররাইড */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #FFF !important;
            border-radius: 10px !important;
        }
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border-color: #00E5FF !important;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.2) !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- হেডার রেন্ডারিং ---
st.markdown("""
    <div class='title-container'>
        <div class='main-title'>🧬 SEU MATRIX TARGET BAL-SCANNER</div>
        <div class='engine-badge'>⚡ BACKEND PIPELINE: ENGINE READY</div>
    </div>
""", unsafe_allow_html=True)

# --- প্লে-রাইট ব্রাউজার ড্রাইভার লোডার ---
@st.cache_resource
def initialize_browser_pipeline():
    try:
        os.system(f"{sys.executable} -m playwright install chromium")
        return True
    except Exception as e:
        st.error(f"Pipeline Engine Initialization Failed: {e}")
        return False

engine_ready = initialize_browser_pipeline()

# --- ব্যাকএন্ড স্ক্যানার কোর লজিক ---
async def scan_matrix_node(target_number, clean_token):
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            
            # টোকেন ও ক্লিনিং মেকানিজম
            clean_token = clean_token.replace("Bearer ", "").replace('"', '').replace("'", "").strip()
            
            headers = {
                "Authorization": f"Bearer {clean_token}",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json;charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Origin": "https://ums.seu.edu.bd",
                "Referer": "https://ums.seu.edu.bd/"
            }
            
            context = await browser.new_context(extra_http_headers=headers)
            page = await context.new_page()
            
            # 🎯 টার্গেট রিকোয়েস্ট এন্ডপয়েন্ট ইউআরএল 
            api_url = f"https://ums.seu.edu.bd/api/student/balance-check?phone={target_number}"
            
            response = await page.goto(api_url, wait_until="networkidle", timeout=15000)
            status_code = response.status if response else 500
            
            if status_code in [401, 403]:
                await browser.close()
                return {"status": "auth_error", "message": "Token Invalid or UMS Service Outage."}
                
            if status_code == 200:
                try:
                    data = await response.json()
                    await browser.close()
                    return {"status": "success", "data": data}
                except:
                    content = await response.text()
                    await browser.close()
                    return {"status": "success", "data": content[:100]}
            else:
                await browser.close()
                return {"status": "failed", "message": f"Server Status Code {status_code}"}
                
        except Exception as e:
            if 'browser' in locals():
                await browser.close()
            return {"status": "error", "message": str(e)}

# --- মডার্ন ২-কলাম গ্রিড ইউজার ইন্টারফেস (UI/UX) ---
left_col, right_col = st.columns([1, 1.2], gap="large")

with left_col:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🛠️ System Authorization")
    
    if 'locked_token' not in st.session_state:
        st.session_state.locked_token = ""
        
    token_input = st.text_input("Bearer Auth Token Array:", value=st.session_state.locked_token, type="password", placeholder="eyJhbGciOiJIUzUxMiJ9...")
    
    if st.button("✨ Save & Lock System Access Tokens", use_container_width=True):
        if token_input:
            st.session_state.locked_token = token_input.replace("Bearer ", "").strip()
            st.toast("Authorization Synced and Sanitized Locked!", icon="🎯")
        else:
            st.warning("Please insert a valid JWT sequence.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📥 Matrix Feed Targets")
    data_feed = st.text_area("Paste Target Phone Numbers:", height=180, placeholder="01723436943\n01329132803")
    
    # মোবাইল নম্বর ফিল্টার করার Regex
    target_numbers = re.findall(r'(?:013|014|015|016|017|018|019)\d{8}', data_feed)
    st.markdown(f"<p style='color: #00E5FF; font-size:13px; font-family: monospace;'>🔍 Detected Target Nodes: {len(target_numbers)}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
    st.markdown("### 🖥️ Cyber Live Terminal Log")
    
    # লঞ্চ বাটনটি প্রফেশনাল এবং নজরকাড়া গ্লোয়িং ফিল দেওয়া হয়েছে
    run_scan = st.button("🚀 DEPLOY CORE CLUSTER SCANNERS", use_container_width=True, type="primary")
    
    terminal_placeholder = st.empty()
    # ডিফল্ট টার্মিনাল ভিউ
    terminal_placeholder.markdown("<pre class='terminal-box'>[SYSTEM LOG]: System standing by. Awaiting live cluster node deployment...</pre>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- লাইভ ক্রলিং ও টার্মিনাল ফিড প্রসেস ---
if run_scan:
    if not st.session_state.locked_token:
        st.error("[CRITICAL ERROR]: System Token Database Empty. Action Aborted.")
    elif not target_numbers:
        st.warning("[WARNING]: Empty Target Queue. Scan process cannot be initialized.")
    else:
        terminal_output = "⏳ [SYSTEM LOG]: Initializing core cluster matrix pipeline...\n"
        terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
        
        success_accounts = []
        
        for number in target_numbers:
            terminal_output += f"📡 [TARGET]: Scanning Matrix Node → {number}\n"
            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
            
            # ব্যাকএন্ড কল
            result = asyncio.run(scan_matrix_node(number, st.session_state.locked_token))
            
            if result["status"] == "auth_error":
                terminal_output += f"   ❌ [AUTH MISM_ERR]: Token Invalid or UMS Service Outage.\n"
            elif result["status"] == "success":
                terminal_output += f"   🔥 [SUCCESS]: Node Verified. Data Connected.\n"
                success_accounts.append({
                    "Target ID": len(success_accounts) + 1,
                    "Matrix Node": number, 
                    "Pipeline Status": "ACTIVE HITS", 
                    "Payload Log": str(result["data"])
                })
            else:
                terminal_output += f"   ⚠️ [NODE_ERR]: {result['message']}\n"
                
            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
            
        terminal_output += "🏁 [SYSTEM LOG]: Target Scan Deployment Terminal Sequence Finished.\n"
        terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)

        # --- লাইভ সাকসেসফুল ডাটা গ্রিড ---
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📊 Live Hits & Verified Accounts Grid")
        if success_accounts:
            st.dataframe(success_accounts, use_container_width=True)
        else:
            st.markdown("<p style='color:#ef4444; font-family:monospace; font-size:14px;'>❌ No successful active matrix data payload caught in this deployment frame.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
