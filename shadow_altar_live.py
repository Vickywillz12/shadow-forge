#!/usr/bin/env python3
"""
SHΔDØW‑FB‑FORGE · LIVE OTP RITUAL (CLOUD READY)
Educational tool — use ONLY on authorized targets.
"""

import os, sys, time, random, json, threading, re, logging, uuid
from flask import Flask, request, jsonify, render_template_string
from fake_useragent import UserAgent
from cryptography.fernet import Fernet
import colorama; colorama.init(autoreset=True)
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ---------- LOGGER & C2 ----------
FERNET_KEY = os.getenv("VOID_KEY", Fernet.generate_key())
CIPHER = Fernet(FERNET_KEY)

class AbyssLogger:
    def __init__(self):
        self.logger = logging.getLogger('VOID')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
        self.logger.addHandler(ch)
        self.tg_token = os.getenv("VOID_TG_TOKEN", "")
        self.tg_chat  = os.getenv("VOID_TG_CHAT", "")
    def log(self, msg, level="info", encrypt=False):
        prefix = "🕷️" if level == "info" else "💀" if level == "error" else "🔮"
        formatted = f"{prefix} {msg}"
        if level == "info": self.logger.info(formatted)
        elif level == "warning": self.logger.warning(formatted)
        elif level == "error": self.logger.error(formatted)
        else: self.logger.debug(formatted)
        if encrypt:
            try:
                ct = CIPHER.encrypt(msg.encode()).decode()
                self._tg_send(f"🔒 VOID REPORT:\n{ct}")
            except: pass
    def _tg_send(self, text):
        if not self.tg_token or not self.tg_chat: return
        import requests
        try:
            requests.post(f"https://api.telegram.org/bot{self.tg_token}/sendMessage",
                          json={"chat_id": self.tg_chat, "text": text}, timeout=5)
        except: pass

logger = AbyssLogger()

# ---------- BROWSER POOL (SESSION MANAGEMENT) ----------
class BrowserForge:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.driver = None
    def _build_options(self):
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1280,900")
        ua = UserAgent().random
        opts.add_argument(f"user-agent={ua}")
        opts.add_argument("--lang=en-US")
        if self.proxy:
            opts.add_argument(f'--proxy-server={self.proxy}')
        opts.add_argument("--disable-notifications")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        return opts
    def start(self):
        opts = self._build_options()
        self.driver = uc.Chrome(options=opts, version_main=None)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    def quit(self):
        if self.driver:
            self.driver.quit()

# Global browser sessions
sessions = {}         # session_id -> BrowserForge instance
sessions_lock = threading.Lock()

def cleanup_session(session_id):
    """Remove session after 5 minutes."""
    time.sleep(300)
    with sessions_lock:
        if session_id in sessions:
            sessions[session_id].quit()
            del sessions[session_id]

# ---------- FACEBOOK CRAFTER (STEP 1 & STEP 2) ----------
class FacebookCrafter:
    SIGNUP_URL = "https://mbasic.facebook.com/reg"

    def __init__(self, browser):
        self.browser = browser
    def _delay(self, base=0.5, jit=0.5):
        time.sleep(base + random.uniform(0, jit))

    def trigger_sms(self, first, last, password, phone):
        """Fill form, submit, and wait for OTP page. Returns True if OTP page loaded."""
        driver = self.browser.driver
        driver.get(self.SIGNUP_URL)
        self._delay(2)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "firstname")))
        driver.find_element(By.NAME, "firstname").send_keys(first)
        driver.find_element(By.NAME, "lastname").send_keys(last)
        driver.find_element(By.NAME, "reg_passwd__").send_keys(password)
        driver.find_element(By.NAME, "sex").send_keys(random.choice(["1","2"]))
        driver.find_element(By.NAME, "birthday_day").send_keys(str(random.randint(1,28)))
        driver.find_element(By.NAME, "birthday_month").send_keys(str(random.randint(1,12)))
        driver.find_element(By.NAME, "birthday_year").send_keys(str(random.randint(1985,2002)))
        driver.find_element(By.NAME, "phone_number").send_keys(phone.lstrip("+"))
        self._delay(1)
        driver.find_element(By.NAME, "submit").click()
        # Wait for OTP input field to appear
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "code")))
            return True
        except Exception as e:
            logger.log(f"OTP page not reached: {e}", level="error", encrypt=True)
            return False

    def submit_otp(self, otp):
        """Enter OTP and submit. Returns (success, cookies_or_error)."""
        driver = self.browser.driver
        driver.find_element(By.NAME, "code").send_keys(otp.strip())
        driver.find_element(By.NAME, "submit").click()
        self._delay(4)
        page = driver.page_source.lower()
        url = driver.current_url
        if "home.php" in url or "welcome" in page:
            cookies = {c['name']: c['value'] for c in driver.get_cookies()}
            logger.log(f"🔥 Account created — ID: {cookies.get('c_user')}", encrypt=True)
            return True, cookies
        elif "incorrect" in page or "invalid" in page:
            return False, "OTP rejected by Facebook"
        else:
            return False, f"Unknown state after OTP: {url[:80]}"

# ---------- FLASK APP WITH EMBEDDED LIVE ALTAR ----------
app = Flask(__name__)

ALTAR_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SHΔDØW-FB-FORGE · Live OTP</title>
<style>
    :root{--bg:#0a0a0a;--text:#c0c0c0;--accent:#b300b3;--dim:#330033}
    *{box-sizing:border-box}
    body{background:var(--bg);color:var(--text);font-family:'Courier New',monospace;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;padding:1rem}
    .container{max-width:500px;width:100%;padding:1.5rem;background:#111;border:1px solid var(--dim);box-shadow:0 0 20px #5a005a;border-radius:12px}
    h1{color:var(--accent);text-align:center;margin-bottom:0.2em;font-size:1.8rem}
    .sub{text-align:center;font-size:0.8rem;color:#666;margin-bottom:1.5rem}
    input,textarea,button{width:100%;padding:10px;margin-bottom:10px;background:#1a1a1a;border:1px solid var(--dim);color:#ccc;border-radius:4px;font-family:inherit}
    input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 8px var(--accent)}
    button{background:#2a002a;border-color:var(--accent);color:var(--accent);font-weight:bold;text-transform:uppercase;cursor:pointer}
    button:disabled{opacity:0.5;cursor:not-allowed}
    .hidden{display:none}
    .status{padding:10px;border-left:3px solid var(--accent);margin:1rem 0;min-height:2.5em}
    .success{color:#0f0}.error{color:#f33}
    .log{background:var(--bg);border:1px dashed var(--dim);padding:10px;font-size:0.8rem;max-height:200px;overflow-y:auto;white-space:pre-wrap;margin-top:1rem}
    .step-indicator{text-align:center;font-size:0.9rem;color:#666;margin-bottom:1rem}
    @media(max-width:450px){h1{font-size:1.5rem}}
</style>
</head>
<body>
<div class="container">
    <h1>🔮 SHΔDØW-FB-FORGE</h1>
    <div class="sub">Real‑time OTP Ritual</div>

    <!-- Step indicator -->
    <div class="step-indicator" id="step-indicator">Step 1 · Offer the Name</div>

    <!-- Step 1 Form -->
    <form id="step1-form">
        <input type="text" id="first" placeholder="First Name" required>
        <input type="text" id="last" placeholder="Last Name" required>
        <input type="password" id="password" placeholder="Password" required>
        <input type="text" id="phone" placeholder="Phone (+1234567890)" required>
        <input type="text" id="proxy" placeholder="Proxy (socks5://... optional)">
        <button type="submit">🩸 SEND SMS & PROCEED</button>
    </form>

    <!-- Step 2 OTP Form (hidden initially) -->
    <div id="step2-area" class="hidden">
        <p style="text-align:center;color:#888;">Enter the 6‑digit code from your phone</p>
        <input type="text" id="otp-input" placeholder="OTP Code" maxlength="8" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code">
        <button id="verify-btn">🔑 SUBMIT CODE & FORGE</button>
        <button id="retry-btn" style="background:#1a1a1a;border-color:#444;color:#999;">↺ Start Over</button>
    </div>

    <div class="status" id="status"></div>
    <div class="log" id="log"></div>
</div>

<script>
const logEl = document.getElementById('log');
function addLog(msg, isError=false) {
    const div = document.createElement('div');
    div.style.color = isError ? '#f33' : '#0f0';
    div.textContent = '> ' + msg;
    logEl.appendChild(div);
    logEl.scrollTop = logEl.scrollHeight;
}
const statusEl = document.getElementById('status');
const step1Form = document.getElementById('step1-form');
const step2Area = document.getElementById('step2-area');
const stepIndicator = document.getElementById('step-indicator');
const verifyBtn = document.getElementById('verify-btn');
const retryBtn = document.getElementById('retry-btn');
let currentSessionId = null;

function resetToStep1() {
    step1Form.classList.remove('hidden');
    step2Area.classList.add('hidden');
    stepIndicator.textContent = 'Step 1 · Offer the Name';
    statusEl.innerHTML = '';
    document.getElementById('otp-input').value = '';
}

// Step 1: Send name/phone, trigger SMS
step1Form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const first = document.getElementById('first').value.trim();
    const last = document.getElementById('last').value.trim();
    const password = document.getElementById('password').value;
    const phone = document.getElementById('phone').value.trim();
    const proxy = document.getElementById('proxy').value.trim();
    if (!first || !last || !password || !phone) return addLog('All fields required', true);

    addLog('Initiating SMS ritual...');
    const payload = { first, last, password, phone, proxy };
    try {
        const res = await fetch('/start', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success && data.session_id) {
            currentSessionId = data.session_id;
            addLog('✅ SMS triggered! Check your phone for the code.');
            // Hide step1, show step2
            step1Form.classList.add('hidden');
            step2Area.classList.remove('hidden');
            stepIndicator.textContent = 'Step 2 · Whisper the OTP';
            document.getElementById('otp-input').focus();
        } else {
            addLog('❌ FAILED: ' + data.message, true);
        }
    } catch (err) {
        addLog('❌ Network error.', true);
    }
});

// Step 2: Send OTP
verifyBtn.addEventListener('click', async () => {
    const otp = document.getElementById('otp-input').value.trim();
    if (!otp) return;
    if (!currentSessionId) {
        addLog('Session lost. Please start over.', true);
        resetToStep1();
        return;
    }
    verifyBtn.disabled = true;
    verifyBtn.textContent = '⏳ Verifying...';
    addLog('Sending OTP to the void...');
    try {
        const res = await fetch('/verify', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ session_id: currentSessionId, otp })
        });
        const data = await res.json();
        if (data.success) {
            addLog('🔥 ACCOUNT FORGED SUCCESSFULLY');
            addLog('User ID: ' + (data.cookies.c_user || 'unknown'));
            addLog('Cookies: ' + JSON.stringify(data.cookies));
            statusEl.innerHTML = '<span class="success">🎉 Phantom born! Cookies in log.</span>';
            // clear session
            currentSessionId = null;
            step2Area.classList.add('hidden');
            // show start over button only
            retryBtn.classList.remove('hidden');
        } else {
            addLog('💀 FAILED: ' + data.message, true);
            statusEl.innerHTML = '<span class="error">💀 ' + data.message + '</span>';
            // keep OTP field for retry, but mark wrong
        }
    } catch (err) {
        addLog('❌ Connection error.', true);
    } finally {
        verifyBtn.disabled = false;
        verifyBtn.textContent = '🔑 SUBMIT CODE & FORGE';
    }
});

retryBtn.addEventListener('click', () => {
    // Clean up session on server if needed
    if (currentSessionId) {
        fetch('/cancel', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ session_id: currentSessionId })
        }).catch(()=>{});
    }
    currentSessionId = null;
    resetToStep1();
    logEl.innerHTML = '';
    statusEl.innerHTML = '';
});

// Prevent accidental leave
window.addEventListener('beforeunload', () => {
    if (currentSessionId) navigator.sendBeacon('/cancel', JSON.stringify({session_id: currentSessionId}));
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(ALTAR_HTML)

@app.route('/start', methods=['POST'])
def start():
    data = request.json
    first = data.get('first','').strip()
    last  = data.get('last','').strip()
    pw    = data.get('password','').strip()
    phone = data.get('phone','').strip()
    proxy = data.get('proxy','').strip()
    if not (first and last and pw and phone):
        return jsonify({"success":False,"message":"Missing fields"}),400

    browser = BrowserForge(proxy=proxy if proxy else None)
    try:
        browser.start()
    except Exception as e:
        return jsonify({"success":False,"message":f"Browser launch failed: {e}"}),500

    crafter = FacebookCrafter(browser)
    sms_sent = crafter.trigger_sms(first, last, pw, phone)
    if not sms_sent:
        browser.quit()
        return jsonify({"success":False,"message":"Failed to reach OTP page. Phone may be invalid or network blocked."}),400

    # Create session
    session_id = str(uuid.uuid4())
    with sessions_lock:
        sessions[session_id] = browser
    # Background cleanup
    threading.Thread(target=cleanup_session, args=(session_id,), daemon=True).start()
    return jsonify({"success":True,"session_id":session_id,"message":"SMS triggered. Enter OTP."})

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    session_id = data.get('session_id','')
    otp = data.get('otp','').strip()
    if not session_id or not otp:
        return jsonify({"success":False,"message":"Missing session or OTP"}),400

    with sessions_lock:
        browser = sessions.get(session_id)
        if not browser:
            return jsonify({"success":False,"message":"Session expired or invalid"}),404

    crafter = FacebookCrafter(browser)
    success, result = crafter.submit_otp(otp)

    # Clean up session regardless
    with sessions_lock:
        if session_id in sessions:
            del sessions[session_id]
    browser.quit()

    if success:
        return jsonify({"success":True,"cookies":result})
    else:
        return jsonify({"success":False,"message":result})

@app.route('/cancel', methods=['POST'])
def cancel():
    data = request.json
    session_id = data.get('session_id','')
    with sessions_lock:
        if session_id in sessions:
            sessions[session_id].quit()
            del sessions[session_id]
    return jsonify({"ok":True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port, debug=False)