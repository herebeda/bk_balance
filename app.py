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

# ডার্ক মোড এবং ম্যাকওএস-স্টাইল প্রফেশনাল টার্মিনাল সিএসএস (CSS)
st.markdown("""
    <style>
        .reportview-container { background: #0e1117; }
        .terminal-box {
            background-color: #000000;
            color: #00FF00;
            font-family: 'Courier New', Courier, monospace;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #333;
            line-height: 1.5;
            margin-bottom: 20px;
        }
        .header-title {
            color: #00FF00;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='header-title'>🧬 SEU MATRIX TARGET BAL-SCANNER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>[ BACKEND PIPELINE: ENGINE READY ]</p>", unsafe_allow_html=True)

# --- প্লে-রাইট ব্রাউজার ড্রাইভার লোডার (রুট পারমিশন ছাড়া নিরাপদ সেটাপ) ---
@st.cache_resource
def initialize_browser_pipeline():
    try:
        # শুধুমাত্র প্লে-রাইটের আইসোলেটেড ক্রোমিয়াম বাইনারি নামাবে, ওএস সিস্টেমে হাত দেবে না
        os.system(f"{sys.executable} -m playwright install chromium")
        return True
    except Exception as e:
        st.error(f"Pipeline Engine Initialization Failed: {e}")
        return False

engine_ready = initialize_browser_pipeline()

# --- ব্যাকএন্ড স্ক্যানার কোর লজিক (API/Browser request) ---
async def scan_matrix_node(target_number, clean_token):
    async with async_playwright() as p:
        try:
            # হেডলেস ব্রাউজার লঞ্চ (উইন্ডো ছাড়া ব্যাকগ্রাউন্ডে চলবে)
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
            )
            
            # নিখুঁত হেডার কনফিগারেশন এবং টোকেন ইনজেকশন
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
            
            # 🎯 আপনার টার্গেট UMS API বা এন্ডপয়েন্ট ইউআরএল এখানে বসাবেন
            # উদাহরণ হিসেবে একটি ডামি ব্যালেন্স চেক এন্ডপয়েন্ট দেওয়া হলো:
            api_url = f"https://ums.seu.edu.bd/api/student/balance-check?phone={target_number}"
            
            response = await page.goto(api_url)
            status_code = response.status if response else 500
            
            await browser.close()
            
            # টোকেন কাজ না করলে বা সার্ভার ডাউন থাকলে Unauthorized (401/403) রেসপন্স হ্যান্ডলিং
            if status_code in [401, 403]:
                return {"status": "auth_error", "message": "Token Invalid or UMS Service Outage."}
            elif status_code == 200:
                # সফল হলে রেসপন্স ডাটা রিটার্ন করবে
                try:
                    data = await response.json()
                    return {"status": "success", "data": data}
                except:
                    return {"status": "success", "data": "Account Active (No Data Payload)"}
            else:
                return {"status": "failed", "message": f"Server responded with code {status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

# --- ফ্রন্টএন্ড লেআউট ও ইউজার ইনপুট প্যানেল ---
st.subheader("🖥️ Cyber Live Matrix Terminal")

# টোকেন ইনপুট সেকশন
if 'locked_token' not in st.session_state:
    st.session_state.locked_token = ""

token_input = st.text_input("⚙️ System Authorization (Bearer Auth Token):", value=st.session_state.locked_token, type="password")

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Save & Lock Token"):
        if token_input:
            # 💡 আপনার রিকোয়েস্ট করা মূল টোকেন ক্লিনিং মেকানিজম:
            # ইনপুট থেকে ডাবল 'Bearer ' বা অতিরিক্ত স্পেস থাকলে তা স্বয়ংক্রিয়ভাবে মুছে ফেলবে
            st.session_state.locked_token = token_input.replace("Bearer ", "").strip()
            st.success("Token Locked & Sanitized Securely!")
        else:
            st.warning("Please input a valid token.")

# টার্গেট ডাটা ইনপুট সেকশন
data_feed = st.text_area("📥 Data Feed Input (Paste Target Numbers):", height=150, placeholder="017XXXXXXXX\n013XXXXXXXX")

# মোবাইল নম্বর ফিল্টার করার রেগুলার এক্সপ্রেশন (Regex)
target_numbers = re.findall(r'(?:013|014|015|016|017|018|019)\d{8}', data_feed)

# স্ক্যান ট্রিগার বাটুন
if st.button("🚀 Deploy Core Cluster Matrix Scan"):
    if not st.session_state.locked_token:
        st.error("[CRITICAL ERROR]: No Token Found. Please lock your authorization token first.")
    elif not target_numbers:
        st.warning("[WARNING]: No valid target nodes/numbers detected in the data feed.")
    else:
        terminal_output = ""
        st.info(f"[SYSTEM LOG]: Initializing core cluster matrix pipeline for {len(target_numbers)} nodes...")
        
        # লাইভ টার্মিনাল ডিসপ্লে বক্স
        terminal_placeholder = st.empty()
        success_accounts = []
        
        # লুপ চালিয়ে প্রতিটি নম্বর স্ক্যান করা
        for number in target_numbers:
            terminal_output += f"[TARGET]: Scanning Matrix Node → {number}\n"
            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
            
            # এসিনক্রোনাস ফাংশন রান করা
            result = asyncio.run(scan_matrix_node(number, st.session_state.locked_token))
            
            if result["status"] == "auth_error":
                terminal_output += f" ├─ [AUTH MISM_ERR]: {result['message']}\n"
            elif result["status"] == "success":
                terminal_output += f" ├─ [SUCCESS]: Node Verified. Data Connected.\n"
                success_accounts.append({"Number": number, "Status": "Verified/Active", "Log": str(result["data"])})
            else:
                terminal_output += f" ├─ [NODE_ERR]: {result['message']}\n"
                
            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
        
        terminal_output += "[SYSTEM LOG]: Target Scan Deployment Terminal Sequence Over.\n"
        terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
        
        # সাকসেসফুল ডেটা গ্রিড শো করা
        st.subheader("📊 Live Hits & Verified Accounts Grid")
        if success_accounts:
            st.dataframe(success_accounts, use_container_width=True)
        else:
            st.markdown("<p style='color:#ff4b4b;'>No successful positive accounts registered yet in this session matrix.</p>", unsafe_allow_html=True)
