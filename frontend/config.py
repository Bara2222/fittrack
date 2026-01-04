"""
Configuration and constants for FitTrack Streamlit application.
Contains CSS styles, API configuration, and global constants.
"""
import os
import streamlit as st

# API Configuration
def get_api_base():
    """Get API base URL from environment, secrets, or default."""
    api_base = os.environ.get('API_BASE')
    if not api_base:
        try:
            api_base = st.secrets.get('api_base', 'http://localhost:5000/api')
        except:
            api_base = 'http://localhost:5000/api'
    return api_base

def get_api_base_external():
    """Get external API base URL for browser redirects (OAuth)"""
    api_base_external = os.environ.get('API_BASE_EXTERNAL')
    if not api_base_external:
        try:
            api_base_external = st.secrets.get('api_base_external', 'http://localhost:5000/api')
        except:
            api_base_external = 'http://localhost:5000/api'
    return api_base_external

API_BASE = get_api_base()
API_BASE_EXTERNAL = get_api_base_external()

# Global CSS Styles
GLOBAL_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

/* Theme variables - Black & Yellow Design */
:root{
    --bg: #000000;           
    --surface: #0a0a0a;      
    --primary: #ffd700;      
    --secondary: #ffffff;    
    --accent: #ffed4e;       
    --muted: #999999;        
    --success: #4ade80;
    --danger: #ef4444;
    --border: #ffd700;       
    --text-primary: #ffffff; 
    --text-secondary: #000000;
}

/* Global styles */
html, body, [class*='css'] { 
    font-family: 'Poppins', sans-serif !important; 
    color: var(--text-primary) !important; 
    background: var(--bg) !important;
}

/* Hide Streamlit elements but keep header functional */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Hide Streamlit "Running" status messages */
div[data-testid="stStatusWidget"] {
    display: none !important;
}

.stSpinner > div {
    display: none !important;
}

[data-testid="stStatus"] {
    display: none !important;
}

/* Hide any element containing "Running" text */
div:has-text("Running") {
    display: none !important;
}

/* Additional selectors for running status */
.stAlert {
    display: none !important;
}

.running-text {
    display: none !important;
}

/* Hide toast notifications that might show running status */
div[data-testid="toastContainer"] {
    display: none !important;
}

/* Hide any status messages in general */
div[class*="status"] {
    display: none !important;
}

/* Force hide elements with "Running" in text content */
div:contains("Running") {
    display: none !important;
}

div:contains("get_user_workouts") {
    display: none !important;
}

/* Make header transparent but keep it functional for hamburger menu */
header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 100 !important;
}

/* Hide the colorful decoration bar at top */
div[data-testid="stDecoration"] {
    display: none !important;
}

/* Style hamburger button to be visible */
button[kind="header"] {
    background-color: transparent !important;
    color: var(--primary) !important;
    border: 1px solid var(--primary) !important;
    border-radius: 8px !important;
}

/* Container */
.block-container{
    max-width: 1400px !important; 
    margin: 0 auto !important; 
    padding: 3rem 2rem !important; 
    background: var(--bg) !important;
}

/* Reset button styles */
.stButton > button {
    min-height: 48px !important;
    padding: 12px 32px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    line-height: 1.5 !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
}

.stButton > button span,
.stButton > button p {
    color: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
}

/* Headers with glow effect */
h1, h2, h3, .main-header {
    color: var(--text-primary) !important;
    font-weight: 800 !important;
    text-align: center !important;
    text-shadow: 0 0 20px rgba(255,215,0,0.6),
                 0 0 40px rgba(255,215,0,0.4),
                 0 0 60px rgba(255,215,0,0.2) !important;
    letter-spacing: 0.5px !important;
}

.main-header{
    font-size: 48px !important; 
    font-weight: 900 !important; 
    margin-bottom: 16px !important;
    padding: 0 !important;
    background: transparent !important;
}

.hero-subtitle {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 3px !important;
    margin-bottom: 24px !important;
    text-shadow: none !important;
}

.hero-description {
    font-size: 18px !important;
    color: rgba(255,255,255,0.85) !important;
    line-height: 1.8 !important;
    max-width: 900px !important;
    margin: 0 auto 48px !important;
    text-shadow: none !important;
}

/* Primary yellow buttons */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"],
.stButton > button {
    background: var(--primary) !important;
    color: var(--text-secondary) !important;
    border: none !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(255,215,0,0.4) !important;
}

.stButton > button:hover {
    background: var(--accent) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(255,215,0,0.6) !important;
}

/* Feature cards with yellow borders */
.card, .feature-card {
    background: var(--bg) !important;
    border: 3px solid var(--primary) !important;
    border-radius: 16px !important;
    padding: 48px 32px !important;
    margin-bottom: 24px !important;
    transition: all 0.3s ease !important;
    min-height: 320px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
}

.card:hover, .feature-card:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 30px rgba(255,215,0,0.3) !important;
    transform: translateY(-4px) !important;
}

.card-icon {
    font-size: 64px !important;
    margin-bottom: 24px !important;
}

.card-title {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    margin-bottom: 16px !important;
    border-left: 4px solid var(--primary) !important;
    padding-left: 16px !important;
    text-align: left !important;
    width: 100% !important;
}

.card-description {
    font-size: 15px !important;
    color: var(--muted) !important;
    line-height: 1.7 !important;
}

/* Tertiary/default buttons */
.stButton > button:not([kind]):not([data-testid*="primary"]):not([data-testid*="secondary"]) {
    background: linear-gradient(135deg, #ffd700, #ffed4e) !important;
    color: #000000 !important;
    border: 2px solid #ffd700 !important;
    box-shadow: 0 4px 12px rgba(255,215,0,0.3) !important;
}

.stButton > button:not([kind]):not([data-testid*="primary"]):not([data-testid*="secondary"]):hover {
    background: linear-gradient(135deg, #ffed4e, #fff44d) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(255,215,0,0.5) !important;
}

/* Full width buttons - ensure proper sizing */
div[data-testid="column"] .stButton[data-testid="baseButton-fullWidth"] > button,
div[data-testid="column"] .stButton > button[style*="width: 100%"] {
    width: 100% !important;
    max-width: 100% !important;
}

/* Small delete/action buttons */
.stButton > button[aria-label*="❌"],
.stButton > button[aria-label*="🗑️"] {
    min-width: 44px !important;
    max-width: 60px !important;
    padding: 8px 12px !important;
    font-size: 18px !important;
}

/* Form submit buttons */
button[type="submit"],
button[kind="formSubmit"] {
    min-height: 48px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

/* Theme variables - Black & Yellow */
.stTabs {
    margin: 20px 0;
    border: 2px solid rgba(255,215,0,0.2);
    border-radius: 16px;
    padding: 8px;
    background: rgba(28, 28, 28, 0.5);
    backdrop-filter: blur(10px);
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    justify-content: center;
    background: transparent;
    border: none;
    border: 2px solid rgba(255,215,0,0.2);
}
.stTabs [data-baseweb="tab"]{
    border-radius:12px;
    padding:14px 28px;
    font-weight:700;
    color: var(--muted);
    border: 2px solid transparent;
    transition: all .3s ease;
}
.stTabs [data-baseweb="tab"]:hover{
    background: rgba(255,215,0,0.1);
    border-color: rgba(255,215,0,0.3);
    color: var(--primary);
}
.stTabs [aria-selected="true"]{
    background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
    color: var(--text-secondary) !important;
    border-color: var(--primary) !important;
    box-shadow: 0 4px 12px rgba(255,215,0,0.4);
    font-weight: 800;
}

/* Cards - Glassmorphism */
.card{
    background: rgba(28, 28, 28, 0.7); 
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius:24px; 
    padding:32px; 
    box-shadow: 0 8px 32px rgba(255,215,0,0.3), 
                inset 0 1px 0 rgba(255,255,255,0.1),
                0 0 0 1px rgba(255,215,0,0.2);
    border: 1px solid rgba(255,215,0,0.4);
    transition: all .6s cubic-bezier(0.23, 1, 0.32, 1);
    position: relative;
    overflow: hidden;
}
.card::before{
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 26px;
    background: linear-gradient(45deg, var(--primary), var(--accent), transparent, var(--primary));
    z-index: -1;
    opacity: 0;
    transition: all .6s ease;
    background-size: 300% 300%;
    animation: gradientShift 3s ease infinite;
}
.card::after{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.6s ease;
}
.card:hover{
    background: rgba(28, 28, 28, 0.8);
    box-shadow: 0 20px 60px rgba(255,215,0,0.5), 
                0 0 80px rgba(255,215,0,0.3),
                inset 0 1px 0 rgba(255,255,255,0.2);
    transform: translateY(-8px) rotateX(5deg) rotateY(2deg) scale(1.03);
    border-color: var(--primary);
}
.card:hover::before{
    opacity: 1;
}
.card:hover::after{
    left: 100%;
}
@keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Override Streamlit defaults */
.stApp{background:var(--bg) !important}
.main{background:var(--bg) !important}
.block-container{background:var(--bg) !important}

/* Markdown/text */
.stMarkdown, .stText, .stHtml, .stMarkdown div, .stCaption{
    color: var(--text-primary) !important;
    background: transparent !important;
    line-height: 1.6;
}
.stMarkdown h1{
    color: var(--primary) !important;
    font-weight: 800;
    font-size: 2.5rem;
    text-shadow: 0 0 30px rgba(255,215,0,0.6);
    margin-bottom: 1rem;
}
.stMarkdown h2{
    color: var(--accent) !important;
    font-weight: 700;
    font-size: 2rem;
    text-shadow: 0 0 20px rgba(255,237,78,0.5);
    margin-bottom: 0.8rem;
}
.stMarkdown h3{
    color: var(--text-primary) !important;
    font-weight: 600;
    font-size: 1.5rem;
    border-left: 4px solid var(--primary);
    padding-left: 12px;
    margin-bottom: 0.6rem;
}
.stMarkdown p{
    color: var(--muted) !important;
    font-size: 1rem;
}
.stMarkdown a{
    color: var(--primary) !important;
    text-decoration: none;
    font-weight:600;
    border-bottom: 2px solid transparent;
    transition: all .3s ease;
}
.stMarkdown a:hover{
    border-bottom-color: var(--primary);
    text-shadow: 0 0 10px rgba(255,215,0,0.6);
}

/* Form inputs */
.stTextInput>div>div>input, 
.stTextArea>div>div>textarea,
.stSelectbox>div>div>div,
.stNumberInput>div>div>input{
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c) !important;
    border: 2px solid rgba(255,215,0,0.3) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding:14px 16px !important;
    font-size:16px !important;
    transition: all .3s ease;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
}

/* Selectbox specific styling */
.stSelectbox > div > div {
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c) !important;
    border: 2px solid rgba(255,215,0,0.3) !important;
    border-radius: 12px !important;
}

.stSelectbox > div > div > div {
    color: var(--text-primary) !important;
    background: transparent !important;
}

/* Dropdown menu options */
.stSelectbox [data-baseweb="select"] {
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c) !important;
    border: 2px solid rgba(255,215,0,0.3) !important;
}

/* Dropdown popover */
[data-baseweb="popover"] {
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c) !important;
    border: 2px solid var(--primary) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 24px rgba(255,215,0,0.4) !important;
}

/* Dropdown menu items */
[data-baseweb="menu"] {
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c) !important;
    border: none !important;
    border-radius: 12px !important;
}

/* Individual dropdown options */
[role="option"] {
    background: transparent !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    border-radius: 8px !important;
    margin: 2px 4px !important;
    transition: all 0.2s ease !important;
}

[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
    color: var(--text-secondary) !important;
    transform: translateX(4px) !important;
    box-shadow: 0 2px 8px rgba(255,215,0,0.3) !important;
}

/* Arrow icon in selectbox */
.stSelectbox svg {
    fill: var(--primary) !important;
}

/* Additional selectbox styling - alternative selectors */
div[data-testid="stSelectbox"] > div > div {
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c) !important;
    border: 2px solid rgba(255,215,0,0.3) !important;
    color: var(--text-primary) !important;
}

div[data-testid="stSelectbox"] div[role="combobox"] {
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c) !important;
    color: var(--text-primary) !important;
    border: 2px solid rgba(255,215,0,0.3) !important;
}

/* Ensure all select dropdown text is visible */
select, option {
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--primary) !important;
}

/* Force visibility for all dropdown elements */
div[class*="select"] {
    color: var(--text-primary) !important;
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c) !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus,
.stSelectbox>div>div>div:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 4px rgba(255,215,0,0.3), inset 0 2px 4px rgba(0,0,0,0.3) !important;
    background: linear-gradient(145deg, #303030, #202020) !important;
}

/* Labels */
.stTextInput>label, .stTextArea>label, .stSelectbox>label, .stNumberInput>label{
    color: var(--primary) !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    margin-bottom: 10px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Sidebar elements */
[data-testid="stSidebar"] .stButton>button{
    width:100%;
    text-align:left;
    justify-content:flex-start;
    background: transparent !important;
    color: var(--text-primary) !important;
    box-shadow:none;
    border: 2px solid rgba(255,215,0,0.2) !important;
    border-radius: 12px;
}
[data-testid="stSidebar"] .stButton>button:hover{
    background: rgba(255,215,0,0.15) !important;
    border-color: var(--primary) !important;
    transform: translateX(6px);
    box-shadow: 0 0 20px rgba(255,215,0,0.3) !important;
    color: var(--primary) !important;
}

/* Animated Stat boxes with Progress Rings */
.stat-box{
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
    color: var(--text-primary);
    padding:40px;
    border-radius:24px;
    text-align:center;
    box-shadow: 0 15px 45px rgba(255,215,0,0.4), 
                0 0 0 2px rgba(255,215,0,0.6),
                inset 0 1px 0 rgba(255,255,255,0.1);
    border: 2px solid rgba(255,215,0,0.8);
    position: relative;
    overflow: hidden;
    transition: all 0.4s ease;
}
.stat-box::before{
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(from 0deg, transparent, rgba(255,215,0,0.1), transparent);
    animation: rotate 6s linear infinite;
    z-index: 0;
}
.stat-box:hover{
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 25px 60px rgba(255,215,0,0.6), 
                0 0 100px rgba(255,215,0,0.4),
                0 0 0 3px rgba(255,215,0,0.8);
}
.stat-number{
    font-size:72px;
    font-weight:900;
    margin-bottom:16px;
    color: #FFFFFF !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8), 0 0 20px rgba(255,215,0,0.8);
    position: relative;
    z-index: 10;
    line-height: 1;
    font-family: 'Poppins', sans-serif;
}
.stat-label{
    font-size:16px;
    font-weight:700;
    color: #FFD700 !important;
    text-transform:uppercase;
    letter-spacing:2px;
    position: relative;
    z-index: 10;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}
.progress-ring {
    position: absolute;
    top: 15px;
    right: 15px;
    width: 50px;
    height: 50px;
    z-index: 5;
    opacity: 0.8;
}
.progress-ring circle {
    fill: none;
    stroke: rgba(255,215,0,0.2);
    stroke-width: 3;
}
.progress-ring .progress {
    stroke: var(--primary);
    stroke-linecap: round;
    transition: stroke-dasharray 2s cubic-bezier(0.23, 1, 0.32, 1);
    filter: drop-shadow(0 0 6px rgba(255,215,0,0.6));
}
@keyframes rotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
@keyframes countUp {
    0% { opacity: 0; transform: scale(0.9); }
    100% { opacity: 1; transform: scale(1); }
}

/* Expander */
.streamlit-expanderHeader{
    background: var(--surface);
    border-radius:12px;
    padding:16px;
    border: 1px solid var(--border);
    font-weight:600;
    color: var(--secondary);
}
.streamlit-expanderHeader:hover{
    border-color: var(--primary);
    background: rgba(255,215,0,0.05);
}

/* Footer at bottom of page */
.main .block-container {
    min-height: calc(100vh - 200px);
    padding-bottom: 2rem;
}

/* Neon Graph Theme */
.neon-graph {
    background: radial-gradient(circle at center, rgba(255,215,0,0.05), transparent);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,215,0,0.3);
    box-shadow: 0 0 30px rgba(255,215,0,0.2);
    position: relative;
    overflow: hidden;
}
.neon-graph::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
    animation: scan 2s linear infinite;
}

@keyframes scan {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

/* Dark/Light Toggle Switch */
.theme-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    background: rgba(28, 28, 28, 0.9);
    backdrop-filter: blur(10px);
    border: 2px solid var(--primary);
    border-radius: 25px;
    padding: 8px 16px;
    font-size: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    color: var(--primary);
}
.theme-toggle:hover {
    background: rgba(255, 215, 0, 0.1);
    box-shadow: 0 0 20px rgba(255,215,0,0.4);
    transform: scale(1.1);
}

/* Achievement badges */
.achievement-badge {
    background: linear-gradient(135deg, var(--success), #22c55e);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
    margin: 4px 0;
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
    animation: achievement-unlock 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

/* Streak counter */
.streak-counter {
    background: linear-gradient(135deg, #ff6b6b, #ee5a52);
    color: white;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    margin: 16px 0;
    box-shadow: 0 8px 24px rgba(255, 107, 107, 0.3);
}
.streak-number {
    font-size: 48px;
    font-weight: 900;
    margin-bottom: 8px;
}
.streak-label {
    font-size: 16px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Activity heatmap */
.activity-heatmap {
    display: grid;
    grid-template-columns: repeat(52, 1fr);
    gap: 3px;
    padding: 20px;
    background: rgba(28, 28, 28, 0.5);
    border-radius: 12px;
    border: 1px solid rgba(255,215,0,0.3);
}
.activity-day {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    background: rgba(255,215,0,0.2);
    transition: all 0.2s ease;
}
.activity-day.active {
    background: var(--primary);
    box-shadow: 0 0 8px rgba(255,215,0,0.6);
}

/* Toast notifications */
.toast {
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    color: var(--text-secondary);
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    z-index: 9999;
    animation: slideIn 0.3s ease;
}
@keyframes slideIn {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
}

/* Loading spinner */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    min-height: 200px;
}
.loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid rgba(255,215,0,0.2);
    border-top: 4px solid var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.loading-text {
    color: var(--primary);
    margin-top: 1rem;
    font-size: 16px;
    font-weight: 600;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: rgba(28, 28, 28, 0.5);
    border-radius: 20px;
    border: 2px dashed rgba(255,215,0,0.3);
    margin: 2rem 0;
}
.empty-state-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.7;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
.empty-state-title {
    color: var(--primary);
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.empty-state-text {
    color: var(--muted);
    font-size: 1rem;
    margin-bottom: 1.5rem;
}

/* Workout template cards */
.template-card {
    background: linear-gradient(145deg, #1c1c1c, #141414);
    border: 2px solid rgba(255,215,0,0.3);
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    transition: all 0.3s ease;
    cursor: pointer;
}
.template-card:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 20px rgba(255,215,0,0.3);
    transform: translateY(-2px);
}

/* 1RM Calculator styles */
.rm-calculator {
    background: linear-gradient(145deg, #2a2a2a, #1c1c1c);
    border: 2px solid var(--primary);
    border-radius: 16px;
    padding: 24px;
    margin: 20px 0;
}
.rm-result {
    font-size: 2rem;
    font-weight: 800;
    color: var(--primary);
    text-align: center;
    margin: 16px 0;
    text-shadow: 0 0 10px rgba(255,215,0,0.5);
}

/* Loading Skeleton */
.skeleton {
    background: linear-gradient(90deg, rgba(255,255,255,0.1) 25%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.1) 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Achievement Animation */
.achievement-unlock {
    animation: achievement-bounce 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes achievement-bounce {
    0% { transform: scale(0) rotate(180deg); opacity: 0; }
    50% { transform: scale(1.2) rotate(0deg); opacity: 1; }
    100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

/* Smooth Page Transitions */
.page-transition {
    animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
    0% { opacity: 0; transform: translateY(30px); }
    100% { opacity: 1; transform: translateY(0); }
}

</style>
"""

# Constants
DEFAULT_WORKOUT_TEMPLATES = [
    {
        'name': 'Push Day',
        'description': 'Hrudník, ramena, triceps',
        'exercises': ['Bench Press', 'Overhead Press', 'Tricep Dips'],
        'color': '#FF6B6B'
    },
    {
        'name': 'Pull Day', 
        'description': 'Záda, biceps',
        'exercises': ['Pull-ups', 'Barbell Rows', 'Bicep Curls'],
        'color': '#4ECDC4'
    },
    {
        'name': 'Leg Day',
        'description': 'Nohy, gluteus',
        'exercises': ['Squats', 'Deadlifts', 'Leg Press'],
        'color': '#45B7D1'
    }
]

# Available plates for plate calculator (kg)
AVAILABLE_PLATES = [25, 20, 15, 10, 5, 2.5, 1.25]

# Default barbell weight
DEFAULT_BARBELL_WEIGHT = 20

# Exercise Catalog
EXERCISE_CATALOG = {
    'Hrudník': [
        {'name': 'Bench Press', 'equipment': 'Barbell', 'difficulty': 'Intermediate'},
        {'name': 'Incline Bench Press', 'equipment': 'Barbell', 'difficulty': 'Intermediate'},
        {'name': 'Decline Bench Press', 'equipment': 'Barbell', 'difficulty': 'Intermediate'},
        {'name': 'Dumbbell Press', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Incline Dumbbell Press', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Cable Fly', 'equipment': 'Cable', 'difficulty': 'Beginner'},
        {'name': 'Push-ups', 'equipment': 'Bodyweight', 'difficulty': 'Beginner'},
        {'name': 'Dips', 'equipment': 'Bodyweight', 'difficulty': 'Intermediate'},
    ],
    'Záda': [
        {'name': 'Pull-ups', 'equipment': 'Bodyweight', 'difficulty': 'Intermediate'},
        {'name': 'Chin-ups', 'equipment': 'Bodyweight', 'difficulty': 'Intermediate'},
        {'name': 'Barbell Rows', 'equipment': 'Barbell', 'difficulty': 'Intermediate'},
        {'name': 'T-Bar Rows', 'equipment': 'Barbell', 'difficulty': 'Intermediate'},
        {'name': 'Dumbbell Rows', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Lat Pulldown', 'equipment': 'Cable', 'difficulty': 'Beginner'},
        {'name': 'Cable Rows', 'equipment': 'Cable', 'difficulty': 'Beginner'},
        {'name': 'Deadlifts', 'equipment': 'Barbell', 'difficulty': 'Advanced'},
    ],
    'Nohy': [
        {'name': 'Squats', 'equipment': 'Barbell', 'difficulty': 'Intermediate'},
        {'name': 'Front Squats', 'equipment': 'Barbell', 'difficulty': 'Advanced'},
        {'name': 'Leg Press', 'equipment': 'Machine', 'difficulty': 'Beginner'},
        {'name': 'Lunges', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Bulgarian Split Squats', 'equipment': 'Dumbbell', 'difficulty': 'Intermediate'},
        {'name': 'Leg Curls', 'equipment': 'Machine', 'difficulty': 'Beginner'},
        {'name': 'Leg Extensions', 'equipment': 'Machine', 'difficulty': 'Beginner'},
        {'name': 'Calf Raises', 'equipment': 'Machine', 'difficulty': 'Beginner'},
    ],
    'Ramena': [
        {'name': 'Overhead Press', 'equipment': 'Barbell', 'difficulty': 'Intermediate'},
        {'name': 'Dumbbell Shoulder Press', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Lateral Raises', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Front Raises', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Rear Delt Fly', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Face Pulls', 'equipment': 'Cable', 'difficulty': 'Beginner'},
        {'name': 'Arnold Press', 'equipment': 'Dumbbell', 'difficulty': 'Intermediate'},
    ],
    'Biceps': [
        {'name': 'Barbell Curls', 'equipment': 'Barbell', 'difficulty': 'Beginner'},
        {'name': 'Dumbbell Curls', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Hammer Curls', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Preacher Curls', 'equipment': 'Barbell', 'difficulty': 'Intermediate'},
        {'name': 'Cable Curls', 'equipment': 'Cable', 'difficulty': 'Beginner'},
        {'name': 'Concentration Curls', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
    ],
    'Triceps': [
        {'name': 'Tricep Dips', 'equipment': 'Bodyweight', 'difficulty': 'Intermediate'},
        {'name': 'Close-Grip Bench Press', 'equipment': 'Barbell', 'difficulty': 'Intermediate'},
        {'name': 'Skull Crushers', 'equipment': 'Barbell', 'difficulty': 'Intermediate'},
        {'name': 'Overhead Tricep Extension', 'equipment': 'Dumbbell', 'difficulty': 'Beginner'},
        {'name': 'Tricep Pushdown', 'equipment': 'Cable', 'difficulty': 'Beginner'},
        {'name': 'Diamond Push-ups', 'equipment': 'Bodyweight', 'difficulty': 'Intermediate'},
    ],
    'Core': [
        {'name': 'Plank', 'equipment': 'Bodyweight', 'difficulty': 'Beginner'},
        {'name': 'Side Plank', 'equipment': 'Bodyweight', 'difficulty': 'Beginner'},
        {'name': 'Crunches', 'equipment': 'Bodyweight', 'difficulty': 'Beginner'},
        {'name': 'Russian Twists', 'equipment': 'Bodyweight', 'difficulty': 'Beginner'},
        {'name': 'Hanging Leg Raises', 'equipment': 'Bodyweight', 'difficulty': 'Advanced'},
        {'name': 'Ab Wheel Rollout', 'equipment': 'Equipment', 'difficulty': 'Advanced'},
        {'name': 'Cable Crunches', 'equipment': 'Cable', 'difficulty': 'Intermediate'},
    ]
}