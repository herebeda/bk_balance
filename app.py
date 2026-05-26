import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import sys
import os
import re

# --- পৃষ্ঠা কনফিগারেশন এবং থিম (ইউজার ইন্টারফেস) ---
st.set_page_config(
    page_title="SEU MATRIX TARGET BAL-SCANNER",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# আপনার টার্মিনালের ম্যাট্রিক্স গ্রিন থিম ও ডার্ক মোড সিএসএস
st.markdown("""
    <style>
        body { background-color: #0e1117; }
        .terminal-box {
            background-color: #000000 !important;
            color: #00FF00 !important;
            font-family: 'Courier New', Courier, monospace !important;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #1f2937;
            line-height: 1.6;
            margin-bottom: 20px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .header-title {
            color: #00FF00;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0px;
        }
        .sub-pipeline {
            text-align: center;
            color: #888;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='header-title'>🧬 SEU MATRIX TARGET BAL-SCANNER</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-pipeline'>[ BACKEND PIPELINE: ENGINE READY ]</p>", unsafe_allow_html=True)

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
            # ব্যাকগ্রাউন্ড মোডে ব্রাউজার রান করা হচ্ছে
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            
            # টোকেন থেকে অতিরিক্ত কোটেশন বা স্পেস থাকলে তা আরও গভীরভাবে ক্লিন করার লজিক
            clean_token = clean_token.replace("Bearer ", "").replace('"', '').replace("'", "").strip()
            
            # স্ট্যান্ডার্ড হেডার সেটআপ যা UMS গেটওয়ে রিকোয়েস্ট এক্সেপ্ট করে
            headers = {
                "Authorization": f"Bearer {clean_token}",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Origin": "https://ums.seu.edu.bd",
                "Referer": "https://ums.seu.edu.bd/"
            }
            
            context = await browser.new_context(extra_http_headers=headers)
            page = await context.new_page()
            
            # 🎯 টার্গেট রিকোয়েস্ট এন্ডপয়েন্ট ইউআরএল (প্রয়োজন অনুযায়ী পরিবর্তন করে নেবেন)
            api_url = f"https://ums.seu.edu.bd/api/student/balance-check?phone={target_number}"
            
            response = await page.goto(api_url, wait_until="networkidle", timeout=15000)
            status_code = response.status if response else 500
            
            # টোকেন ভ্যালিডেশন চেক এবং রেসপন্স এনালাইসিস
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

# --- ফ্রন্টএন্ড প্যানেল ইন্টারফেস ---
st.markdown("### 🖥️ Cyber Live Matrix Terminal")

# টোকেন ইনপুট সেশন স্টেট ম্যানেজমেন্ট
if 'locked_token' not in st.session_state:
    st.session_state.locked_token = ""

token_input = st.text_input("⚙️ System Authorization (Bearer Auth Token):", value=st.session_state.locked_token, type="password")

col1, col2 = st.columns([1.5, 5])
with col1:
    if st.button("Save & Lock Token"):
        if token_input:
            # ইনপুট থেকে Bearer এবং স্পেস ক্লিয়ার করে সেশন স্টেটে সেভ করা
            st.session_state.locked_token = token_input.replace("Bearer ", "").strip()
            st.success("Authorization Synced Successfully!")
        else:
            st.warning("Input a valid token array.")

st.markdown("---")

# টার্গেট ডাটা ইনপুট
data_feed = st.text_area("📥 Data Feed Input (Paste Target Numbers):", height=150, placeholder="017XXXXXXXX\n013XXXXXXXX")

# বাংলাদেশী ফরম্যাটের মোবাইল নম্বর এক্সট্রাক্ট করার রেগুলার এক্সপ্রেশন
target_numbers = re.findall(r'(?:013|014|015|016|017|018|019)\d{8}', data_feed)

# কোর পাইপলাইন এক্সিকিউশন
if st.button("🚀 Deploy Core Cluster Matrix Scan"):
    if not st.session_state.locked_token:
        st.error("[CRITICAL ERROR]: No Security Token Found. Please lock authorization token first.")
    elif not target_numbers:
        st.warning("[WARNING]: Empty matrix feed. No valid numbers detected.")
    else:
        terminal_output = "[SYSTEM LOG]: Initializing core cluster matrix pipeline for 7 nodes...\n"
        
        # রিয়েল-টাইম টার্মিনাল আপডেট করার জন্য প্লেসহোল্ডার
        terminal_placeholder = st.empty()
        terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
        
        success_accounts = []
        
        # নোড স্ক্যান লুপ
        for number in target_numbers:
            terminal_output += f"[TARGET]: Scanning Matrix Node → {number}\n"
            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
            
            # ব্যাকএন্ড ফাংশন রান
            result = asyncio.run(scan_matrix_node(number, st.session_state.locked_token))
            
            if result["status"] == "auth_error":
                terminal_output += f" ├─ [AUTH MISM_ERR]: {result['message']}\n"
            elif result["status"] == "success":
                terminal_output += f" ├─ [SUCCESS]: Node Verified. Data Payload Connected.\n"
                success_accounts.append({
                    "Node Target": number, 
                    "Status": "Verified Active", 
                    "Payload": str(result["data"])
                })
            else:
                terminal_output += f" ├─ [NODE_ERR]: {result['message']}\n"
                
            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
        
        terminal_output += "[SYSTEM LOG]: Target Scan Deployment Terminal Sequence Over.\n"
        terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
        
        # লাইভ হিট গ্রিড সেকশন
        st.markdown("### 📊 Live Hits & Verified Accounts Grid")
        if success_accounts:
            st.dataframe(success_accounts, use_container_width=True)
        else:
            st.markdown("<p style='color:#ff4b4b; font-family:monospace;'>No successful positive accounts registered yet in this session matrix.</p>", unsafe_allow_html=True)
