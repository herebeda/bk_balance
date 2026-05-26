import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import sys
import os
import re
import json

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
        
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #FFF !important;
            border-radius: 12px !important;
            font-family: 'Fira Code', monospace;
        }
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border-color: #00E5FF !important;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.15) !important;
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

@st.cache_resource
def initialize_browser_pipeline():
    try:
        os.system(f"{sys.executable} -m playwright install chromium")
        return True
    except Exception as e:
        st.error(f"Pipeline Engine Initialization Failed: {e}")
        return False

engine_ready = initialize_browser_pipeline()

# --- অ্যাডভান্সড ডাইনামিক ব্যাকএন্ড স্ক্যানার লজিক ---
async def scan_matrix_node(target_number, clean_token, api_endpoint, req_method, raw_payload_template):
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            
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
            
            # মেথড অনুযায়ী ডাইনামিক ইউআরএল বা পে-লোড হ্যান্ডলিং
            if req_method == "GET":
                # যদি ইউআরএল এর শেষে নম্বর প্যারামিটার হিসেবে যুক্ত করতে হয়
                final_url = api_endpoint.replace("{number}", target_number) if "{number}" in api_endpoint else f"{api_endpoint}?phone={target_number}"
                try:
                    resp = await page.goto(final_url, wait_until="networkidle", timeout=12000)
                    status_code = resp.status if resp else 500
                    res_data = await resp.json()
                except Exception:
                    status_code = 500
                    res_data = None
            else:
                # POST মেথডের জন্য কাস্টম পে-লোড জেনারেট করা
                processed_payload = raw_payload_template.replace("{number}", target_number)
                try:
                    payload_json = json.loads(processed_payload)
                except Exception:
                    payload_json = {"phone": target_number}
                
                try:
                    response = await page.evaluate(f"""
                        async () => {{
                            const res = await fetch('{api_endpoint}', {{
                                method: 'POST',
                                headers: {{
                                    'Authorization': 'Bearer {clean_token}',
                                    'Content-Type': 'application/json'
                                }},
                                body: JSON.stringify({json.dumps(payload_json)})
                            }});
                            if (res.status === 401 || res.status === 403) return {{ status: res.status }};
                            return {{ status: res.status, data: await res.json().catch(() => null) }};
                        }}
                    """)
                    status_code = response.get("status", 500)
                    res_data = response.get("data", None)
                except Exception:
                    status_code = 500
                    res_data = None

            await browser.close()
            
            if status_code in [401, 403]:
                return {"status": "auth_error", "message": "Token Invalid or UMS Service Outage."}
            elif status_code == 200:
                return {"status": "success", "data": res_data if res_data else "Node Connected Successfully"}
            else:
                return {"status": "failed", "message": f"HTTP Gateway Server Status {status_code}"}
                
        except Exception as e:
            if 'browser' in locals():
                await browser.close()
            return {"status": "error", "message": str(e)}

# --- মডার্ন এবং রেসপন্সিভ গ্রিড ইন্টারফেস লেআউট ---
left_panel, right_panel = st.columns([1, 1.1], gap="large")

with left_panel:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 🔑 System Authorization & Endpoint")
    
    if 'locked_token' not in st.session_state:
        st.session_state.locked_token = ""
        
    token_input = st.text_input(
        "Bearer Auth Token Array:", 
        value=st.session_state.locked_token, 
        type="password", 
        placeholder="eyJhbGciOiJIUzUxMiJ9.eyJzdWIi..."
    )
    
    # 🌟 নতুন ডাইনামিক ফিল্ডসমূহ (এন্ডপয়েন্ট টিউনিংয়ের জন্য)
    api_endpoint = st.text_input("📡 Target API Endpoint Gateway:", value="https://ums-api-service.seu.edu.bd/accounts/v/2.0.0/online-payment/bkash-pay")
    req_method = st.selectbox("🌐 HTTP Request Method:", ["POST", "GET"])
    
    raw_payload_template = ""
    if req_method == "POST":
        raw_payload_template = st.text_area("📦 Custom JSON Payload (Use {number} as placeholder):", value='{\n  "amount": 2000.0,\n  "gateway": "bkash",\n  "initiator": "online-payment",\n  "actionUrl": null,\n  "applicationApply": {\n    "onlineApplicationType": null,\n    "urgentApplication": null,\n    "mobile": "{number}",\n    "email": null,\n    "copies": null\n  }\n}', height=160)
    
    if st.button("🔒 Save & Verify Gateway Access Engine", use_container_width=True):
        if token_input:
            st.session_state.locked_token = token_input.replace("Bearer ", "").strip()
            st.toast("Authorization and Endpoint Configurations Latched!", icon="🚀")
        else:
            st.warning("Please insert a secure token stream.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("### 📥 Matrix Feed Targets")
    data_feed = st.text_area("Paste Target Phone Numbers:", height=120, placeholder="01723436943\n01329132803")
    
    target_numbers = re.findall(r'(?:013|014|015|016|017|018|019)\d{8}', data_feed)
    st.markdown(f"<p style='color: #00E5FF; font-size:13px; font-family: \"Fira Code\", monospace; margin: 5px 0 0 0;'>🔍 Filtered Active Nodes: {len(target_numbers)}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right_panel:
    st.markdown("<div class='glass-panel' style='height: 100%;'>", unsafe_allow_html=True)
    st.markdown("### 🖥️ Cyber Live Terminal Log")
    
    run_scan = st.button("⚡ DEPLOY CORE CLUSTER SCANNERS", use_container_width=True, type="primary")
    
    terminal_placeholder = st.empty()
    terminal_placeholder.markdown("<pre class='terminal-box'>[SYSTEM LOG]: System standing by. Awaiting live cluster node deployment...</pre>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- কোর এক্সিকিউশন ও লাইভ টার্মিনাল স্ট্রিমিং ---
if run_scan:
    if not st.session_state.locked_token:
        st.error("[CRITICAL ERROR]: Pipeline Core Missing Token Database. Action Refused.")
    elif not target_numbers:
        st.warning("[WARNING]: Empty Feed Queue. Scan framework could not identify targets.")
    else:
        terminal_output = "⏳ [SYSTEM LOG]: Initializing core cluster matrix pipeline...\n"
        terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
        
        success_accounts = []
        
        for number in target_numbers:
            terminal_output += f"📡 [TARGET]: Scanning Matrix Node → {number}\n"
            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
            
            # ডাইনামিক মেথডসহ ব্যাকএন্ড ক্রলার এক্সিকিউশন
            result = asyncio.run(scan_matrix_node(number, st.session_state.locked_token, api_endpoint.strip(), req_method, raw_payload_template))
            
            if result["status"] == "auth_error":
                terminal_output += f"   ❌ [AUTH MISM_ERR]: Token Invalid or UMS Service Outage.\n"
            elif result["status"] == "success":
                terminal_output += f"   🔥 [SUCCESS]: Node Verified. Data Connected.\n"
                success_accounts.append({
                    "Index": len(success_accounts) + 1,
                    "Target Node": number, 
                    "Status": "ACTIVE HIT", 
                    "Payload Log": str(result["data"])
                })
            else:
                terminal_output += f"   ⚠️ [NODE_ERR]: {result['message']}\n"
                
            terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)
            
        terminal_output += "🏁 [SYSTEM LOG]: Target Scan Deployment Terminal Sequence Finished.\n"
        terminal_placeholder.markdown(f"<pre class='terminal-box'>{terminal_output}</pre>", unsafe_allow_html=True)

        # --- লাইভ সাকসেস ডাটা গ্রিড প্যানেল ---
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("### 📊 Live Hits & Verified Accounts Grid")
        if success_accounts:
            st.dataframe(success_accounts, use_container_width=True)
        else:
            st.markdown("<p style='color:#ef4444; font-family:\"Fira Code\", monospace; font-size:14px; margin:0;'>❌ No successful active matrix data payload caught in this deployment frame.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
