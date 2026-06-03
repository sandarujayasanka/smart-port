import cv2
import cv2.aruco as aruco
import numpy as np
import streamlit as st
import time
import platform
from db import register_user, get_supabase_client

# --- SESSION CHECK ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login_page.py")

st.set_page_config(
    page_title="Smart Port | Container Yard Management",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background-color: #0a0e1a; color: #e2e8f0; }
.port-header { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border: 1px solid #1e3a5f; border-radius: 12px; padding: 16px 24px; margin-bottom: 16px; display: flex; align-items: center; gap: 16px; }
.port-header h1 { font-size: 20px; font-weight: 700; color: #38bdf8; margin: 0; }
.port-header p { font-size: 12px; color: #64748b; margin: 2px 0 0 0; font-family: 'JetBrains Mono', monospace; }
.metric-card { background: #111827; border: 1px solid #1e3a5f; border-radius: 10px; padding: 16px 20px; margin-bottom: 12px; }
.metric-card .label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; color: #475569; font-family: 'JetBrains Mono', monospace; margin-bottom: 6px; }
.metric-card .value { font-size: 28px; font-weight: 700; font-family: 'JetBrains Mono', monospace; line-height: 1; }
.metric-card .value.green { color: #22c55e; } .metric-card .value.red { color: #ef4444; } .metric-card .value.amber { color: #f59e0b; }
.metric-card .sub { font-size: 12px; color: #475569; margin-top: 4px; }
.status-pill { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.status-free { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.status-occupied { background: #1c0505; color: #f87171; border: 1px solid #7f1d1d; }
.avail-banner { border-radius: 10px; padding: 14px 20px; text-align: center; margin-bottom: 12px; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; }
.avail-free { background: #052e16; border: 1px solid #166534; color: #4ade80; }
.avail-full { background: #1c0505; border: 1px solid #7f1d1d; color: #f87171; }
.alert-danger { background: #1c0505; border: 1px solid #7f1d1d; border-left: 4px solid #ef4444; border-radius: 8px; padding: 12px 16px; color: #fca5a5; font-size: 13px; font-family: 'JetBrains Mono', monospace; margin-bottom: 10px; }
.alert-success { background: #052e16; border: 1px solid #166534; border-left: 4px solid #22c55e; border-radius: 8px; padding: 12px 16px; color: #86efac; font-size: 13px; font-family: 'JetBrains Mono', monospace; margin-bottom: 10px; }
.slot-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #1e293b; font-size: 13px; }
.slot-row:last-child { border-bottom: none; }
.slot-name { color: #94a3b8; font-family: 'JetBrains Mono', monospace; }
.truck-card { background: #0f172a; border: 1px solid #1e3a5f; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; }
.truck-id { font-size: 11px; color: #f59e0b; font-family: 'JetBrains Mono', monospace; font-weight: 600; }
.truck-lane { font-size: 13px; color: #cbd5e1; margin-top: 2px; }
.video-container { background: #050a12; border: 1px solid #1e3a5f; border-radius: 12px; overflow: hidden; }
.video-label { background: #0f172a; border-bottom: 1px solid #1e3a5f; padding: 10px 16px; font-size: 12px; font-family: 'JetBrains Mono', monospace; color: #38bdf8; }
.live-dot { width: 8px; height: 8px; background: #ef4444; border-radius: 50%; display: inline-block; animation: blink 1s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.section-label { font-size: 11px; color: #475569; font-family: 'JetBrains Mono', monospace; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; padding: 4px 0 8px; }
.success-msg { background: #052e16; border: 1px solid #166534; border-left: 4px solid #22c55e; border-radius: 8px; padding: 12px 16px; color: #86efac; font-size: 13px; font-family: 'JetBrains Mono', monospace; margin: 8px 0; }
.error-msg { background: #1c0505; border: 1px solid #7f1d1d; border-left: 4px solid #ef4444; border-radius: 8px; padding: 12px 16px; color: #fca5a5; font-size: 13px; font-family: 'JetBrains Mono', monospace; margin: 8px 0; }
.ip-card { background: #0f172a; border: 1px solid #1e3a5f; border-radius: 10px; padding: 16px 20px; margin-bottom: 16px; }
.ip-badge { display: inline-block; background: #042f4b; border: 1px solid #0284c7; color: #38bdf8; font-family: 'JetBrains Mono', monospace; font-size: 12px; padding: 4px 12px; border-radius: 6px; margin-top: 6px; }
.signout-bar { position: sticky; top: 0; z-index: 999; background: #0a0e1a; border-bottom: 1px solid #1e3a5f; padding: 8px 0 10px; margin-bottom: 8px; display: flex; justify-content: flex-end; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 1rem; }
.stTabs [data-baseweb="tab-list"] { background: #0a0e1a; border-bottom: 1px solid #1e3a5f; }
.stTabs [data-baseweb="tab"] { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #475569; padding: 10px 20px; }
.stTabs [aria-selected="true"] { color: #38bdf8 !important; border-bottom: 2px solid #38bdf8 !important; background: transparent !important; }
.stButton > button { background: #0f172a !important; color: #94a3b8 !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important; }
.stButton > button:hover { border-color: #38bdf8 !important; color: #38bdf8 !important; }
.signout-btn > button { background: #1c0505 !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; border-radius: 8px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important; }
.signout-btn > button:hover { border-color: #ef4444 !important; color: #ef4444 !important; }
</style>
""", unsafe_allow_html=True)

user = st.session_state.user
is_admin = user["role"] == "admin"

# --- HEADER with Sign Out ---
role_color = "#a78bfa" if is_admin else "#4ade80"
role_label = "ADMIN" if is_admin else "OPERATOR"

header_col, signout_col = st.columns([8, 1])

with header_col:
    st.markdown(f"""
    <div class="port-header">
        <div style="font-size: 28px;">🚢</div>
        <div>
            <h1>Smart Container Yard Management System</h1>
            <p>REAL-TIME FREE SPACE &amp; TRAFFIC MONITORING &nbsp;|&nbsp; EXHIBITION PROTOTYPE v1.0</p>
        </div>
        <div style="margin-left: auto; background:#0f172a; border:1px solid #1e3a5f; border-radius:8px; padding:8px 16px; font-family:'JetBrains Mono',monospace; font-size:12px;">
            👤 &nbsp;<span style="color:{role_color}; font-weight:600;">{user['full_name']}</span>
            &nbsp;<span style="color:#334155;">|</span>&nbsp;
            <span style="color:{role_color};">{role_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with signout_col:
    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="signout-btn">', unsafe_allow_html=True)
    if st.button("🚪 Sign Out", key="logout_btn"):
        from db import logout_user
        logout_user(st.session_state.token)
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.token = None
        st.switch_page("login_page.py")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TABS ---
if is_admin:
    tab_yard, tab_settings, tab_admin = st.tabs(["📹  Yard Monitor", "⚙️  Settings", "👥  User Management"])
else:
    tab_yard, tab_settings = st.tabs(["📹  Yard Monitor", "⚙️  Settings"])

# ══════════════════════════
#  SETTINGS TAB (Updated for Ngrok/Localhost Flexibility)
# ══════════════════════════
with tab_settings:
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Camera Feed Configuration</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ip-card">
        <div style="font-size:13px; color:#94a3b8; margin-bottom:12px; font-family:'JetBrains Mono',monospace;">
            📡 &nbsp;<b>Exhibition Mode (Ngrok URL):</b> Paste the complete HTTPS forwarding URL from Ngrok terminal.<br>
            💻 &nbsp;<b>Localhost Mode:</b> Use the local IP Webcam stream format directly.<br>
            <span style="color:#475569; font-size:11px;">Example: &nbsp;<span style="color:#38bdf8;">https://xxxx.ngrok-free.app/video</span> &nbsp;or&nbsp; <span style="color:#38bdf8;">http://172.20.10.1:8080/video</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # single input box එකක් හැදුවා මුළු URL එකම කෙලින්ම පේස්ට් කරන්න ලේසි වෙන්න
    default_url = st.session_state.get("camera_url", "http://172.20.10.1:8080/video")
    input_url = st.text_input("Camera Stream URL (Ngrok or Local IP)", value=default_url, placeholder="https://your-ngrok.ngrok-free.app/video", key="camera_url_input")

    if st.button("💾  Save Camera Settings", key="btn_save_ip"):
        st.session_state["camera_url"] = input_url
        st.markdown(f'<div class="success-msg">✅ &nbsp;Camera URL saved successfully!</div>', unsafe_allow_html=True)
        st.rerun()

# ══════════════════════════
#  ADMIN — USER MANAGEMENT
# ══════════════════════════
if is_admin:
    with tab_admin:
        st.markdown('<div class="section-label">Create New User</div>', unsafe_allow_html=True)
        create_msg = st.empty()

        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("Full Name", placeholder="Kamal Perera", key="new_name")
            new_email = st.text_input("Email Address", placeholder="kamal@smartport.lk", key="new_email")
        with c2:
            role_options = {"Operator": "operator", "Administrator": "admin"}
            new_role = role_options[st.selectbox("Role", options=list(role_options.keys()), key="new_role")]
            new_password = st.text_input("Temporary Password", type="password", placeholder="Min 8 chars", key="new_password")

        if st.button("➕  Create User", key="btn_create"):
            if not new_name or not new_email or not new_password:
                create_msg.markdown('<div class="error-msg">⚠️ &nbsp;All fields are required.</div>', unsafe_allow_html=True)
            else:
                result = register_user(new_name, new_email, new_password, new_role)
                if result["ok"]:
                    create_msg.markdown(f'<div class="success-msg">✅ &nbsp;User <b>{new_name}</b> created.</div>', unsafe_allow_html=True)
                else:
                    create_msg.markdown(f'<div class="error-msg">❌ &nbsp;{result["error"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="padding-top:24px">All Users</div>', unsafe_allow_html=True)

        supabase = get_supabase_client()
        if supabase:
            try:
                res = supabase.table("users").select("id, full_name, email, role, is_active, last_login").order("created_at", desc=True).execute()
                all_users = res.data
            except Exception as e:
                st.error(f"Failed to fetch users: {e}")
                all_users = []

            for u in all_users:
                rc = "#a78bfa" if u["role"] == "admin" else "#4ade80"
                rl = "ADMIN" if u["role"] == "admin" else "OPERATOR"
                active_badge = '<span style="background:#052e16;color:#4ade80;border:1px solid #166534;padding:2px 8px;border-radius:20px;font-size:11px;">ACTIVE</span>' if u["is_active"] else '<span style="background:#1c0505;color:#f87171;border:1px solid #7f1d1d;padding:2px 8px;border-radius:20px;font-size:11px;">DISABLED</span>'
                last = str(u["last_login"])[:16] if u["last_login"] else "Never logged in"

                col_info, col_action = st.columns([4, 1])
                with col_info:
                    st.markdown(f"""
                    <div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:8px;padding:12px 16px;margin-bottom:4px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div><b>{u['full_name']}</b> &nbsp; {active_badge}</div>
                            <span style="color:{rc};font-size:12px;font-family:'JetBrains Mono'; font-weight:600;">{rl}</span>
                        </div>
                        <div style="font-size:12px;color:#475569;margin-top:4px;">{u['email']} &nbsp;·&nbsp; Last login: {last}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_action:
                    if u["id"] != user["id"]:
                        btn_txt = "🔴 Disable" if u["is_active"] else "🟢 Enable"
                        if st.button(btn_txt, key=f"tog_{u['id']}"):
                            try:
                                supabase.table("users").update({"is_active": not u["is_active"]}).eq("id", u["id"]).execute()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Update failed: {e}")
                    else:
                        st.markdown('<div style="font-size:11px;color:#334155;text-align:center;padding-top:12px;">YOU</div>', unsafe_allow_html=True)

# ══════════════════════════
#  YARD MONITOR
# ══════════════════════════
with tab_yard:
    col_video, col_panel = st.columns([3, 1])

    with col_panel:
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        avail_placeholder = st.empty()
        st.markdown('<div class="section-label">Yard Metrics</div>', unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        with col_m1: free_metric = st.empty()
        with col_m2: occupied_metric = st.empty()
        st.markdown('<div class="section-label" style="padding-top:12px">Slot Status</div>', unsafe_allow_html=True)
        slot_table = st.empty()
        st.markdown('<div class="section-label" style="padding-top:12px">Truck Tracker</div>', unsafe_allow_html=True)
        truck_tracker = st.empty()
        st.markdown('<div class="section-label" style="padding-top:12px">Traffic Alerts</div>', unsafe_allow_html=True)
        alert_box = st.empty()

        cam_url = st.session_state.get("camera_url", "http://172.20.10.1:8080/video")
        st.markdown(f"""
        <div style="background:#0a1628; border:1px solid #1e3a5f; border-radius:8px; padding:8px 12px; margin-top:8px;">
            <div style="font-size:11px; color:#38bdf8; font-family:'JetBrains Mono'; word-break:break-all;">🔗 Current Target: {cam_url}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_video:
        st.markdown('<div class="video-container"><div class="video-label"><span class="live-dot"></span> LIVE OVERHEAD VIEW</div></div>', unsafe_allow_html=True)
        video_frame = st.empty()

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters) # OpenCV 4.7+ සහ Python 3.14 වෙනුවෙන් අලුත් කළා

    total_slots = {
        1: {"name": "Slot A1", "lane": "Lane A1"},
        2: {"name": "Slot A2", "lane": "Lane A1"},
        3: {"name": "Slot B1", "lane": "Lane B1"},
        4: {"name": "Slot B2", "lane": "Lane B2"}
    }

    TRUCK_IDS = {
        5: {"label": "TRUCK-01", "last_x": 0, "last_y": 0, "still_start": None, "last_lane": "Unknown Lane", "status": "moving"},
        6: {"label": "TRUCK-02", "last_x": 0, "last_y": 0, "still_start": None, "last_lane": "Unknown Lane", "status": "moving"}
    }

    def play_alert():
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1200, 250)
        else:
            print('\a', end='', flush=True)

    camera_url = st.session_state.get("camera_url", "http://172.20.10.1:8080/video")
    
    # --- SAFE CAMERA INIT (Streamlit Cloud එක Freeze වීම වැළැක්වීම) ---
    try:
        cap = cv2.VideoCapture(camera_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            with col_video:
                st.warning(f"⚠️ Camera feed offline. Dashboard running in Mock/Static mode. URL: {camera_url}")
                st.info("💡 Exhibition Tip: Open 'Settings' tab and paste the latest Ngrok URL to activate Live Tracking.")
            st.stop()
    except Exception as cam_err:
        with col_video:
            st.error(f"❌ Camera Connection Error: {cam_err}")
        st.stop()

    # --- VIDEO PROCESSING LOOP ---
    blink_state = True
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("⚠️ Camera feed lost.")
            break

        current_time = time.time()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray) # Python 3.14 සඳහා අලුත් ක්‍රමය

        visible_ids = []
        slot_positions = {}
        detected_trucks_this_frame = {}

        if ids is not None:
            visible_ids = ids.flatten().tolist()
            for i, marker_id in enumerate(visible_ids):
                c = corners[i][0]
                center_x = int(c[:, 0].mean())
                center_y = int(c[:, 1].mean())
                if marker_id in TRUCK_IDS:
                    detected_trucks_this_frame[marker_id] = (center_x, center_y)
                    cv2.polylines(frame, [c.astype(int)], True, (0, 165, 255), 3)
                elif marker_id in total_slots:
                    slot_positions[marker_id] = (center_x, center_y)

        current_blocked_lanes = []
        for truck_id, data in TRUCK_IDS.items():
            if truck_id in detected_trucks_this_frame:
                tx, ty = detected_trucks_this_frame[truck_id]
                closest_slot, min_distance = None, float('inf')
                for slot_id, pos in slot_positions.items():
                    dist = np.sqrt((tx - pos[0])**2 + (ty - pos[1])**2)
                    if dist < min_distance:
                        min_distance = dist; closest_slot = slot_id
                if closest_slot is not None:
                    data["last_lane"] = total_slots[closest_slot]["lane"]
                if abs(tx - data["last_x"]) < 15 and abs(ty - data["last_y"]) < 15:
                    if data["still_start"] is None: data["still_start"] = current_time; data["status"] = "slowing"
                    elif current_time - data["still_start"] > 3.0:
                        data["status"] = "blocked"
                        alert_entry = f"{data['label']} blocking {data['last_lane']}"
                        if alert_entry not in current_blocked_lanes: current_blocked_lanes.append(alert_entry)
                else:
                    data["still_start"] = None; data["status"] = "moving"
                data["last_x"] = tx; data["last_y"] = ty
            else:
                data["still_start"] = None; data["status"] = "offline"

        free_count, occupied_count, yard_status = 0, 0, {}
        for slot_id, info in total_slots.items():
            if slot_id in visible_ids:
                yard_status[info["name"]] = "free"; free_count += 1
            else:
                yard_status[info["name"]] = "occupied"; occupied_count += 1

        blink_state = not blink_state
        if free_count > 0:
            dot = "🟢" if blink_state else "⚫"
            avail_placeholder.markdown(f'<div class="avail-banner avail-free">{dot} &nbsp;{free_count} SPACE AVAILABLE</div>', unsafe_allow_html=True)
        else:
            avail_placeholder.markdown('<div class="avail-banner avail-full">🔴 &nbsp;YARD FULL — NO SPACE</div>', unsafe_allow_html=True)

        free_metric.markdown(f'<div class="metric-card"><div class="label">Free Slots</div><div class="value green">{free_count}</div></div>', unsafe_allow_html=True)
        occupied_metric.markdown(f'<div class="metric-card"><div class="label">Occupied</div><div class="value red">{occupied_count}</div></div>', unsafe_allow_html=True)

        slot_rows = "".join([f'<div class="slot-row"><span class="slot-name">{n}</span><span class="status-pill {"status-free" if s=="free" else "status-occupied"}">{s.upper()}</span></div>' for n, s in yard_status.items()])
        slot_table.markdown(f'<div style="background:#111827;border:1px solid #1e3a5f;border-radius:10px;padding:4px 16px;">{slot_rows}</div>', unsafe_allow_html=True)

        if current_blocked_lanes:
            alert_box.markdown("".join([f'<div class="alert-danger">🚨 &nbsp;BLOCKED: {a}</div>' for a in current_blocked_lanes]), unsafe_allow_html=True)
            play_alert()
        else:
            alert_box.markdown('<div class="alert-success">✅ &nbsp;ALL LANES CLEAR</div>', unsafe_allow_html=True)

        display_frame = cv2.resize(frame, (960, 540), interpolation=cv2.INTER_LINEAR)
        video_frame.image(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

    cap.release()
