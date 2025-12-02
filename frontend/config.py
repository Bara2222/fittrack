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

API_BASE = get_api_base()

# Global CSS Styles
GLOBAL_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
html, body, [class*='css'] { font-family: 'Poppins', sans-serif; color:#1a1a1a; background:var(--bg) !important }

/* Button alignment styles - Right align login/register buttons */
div[data-testid="column"]:nth-child(2) .stButton,
div[data-testid="column"]:nth-child(3) .stButton {
    text-align: right !important;
    justify-content: flex-end !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-end !important;
}

/* Header button container alignment - only for specific header columns */
div[data-testid="column"]:nth-child(2) .stButton > button,
div[data-testid="column"]:nth-child(3) .stButton > button {
    width: auto !important;
    height: 40px !important;
    margin: 0 !important;
    padding: 8px 16px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    min-width: 90px !important;
    max-width: none !important;
    color: #000000 !important;
    background-color: #ffd700 !important;
    border: 1px solid #ffd700 !important;
}

/* Primary button specific styling - only for header */
div[data-testid="column"]:nth-child(2) .stButton > button[data-testid="baseButton-primary"],
div[data-testid="column"]:nth-child(3) .stButton > button[data-testid="baseButton-primary"] {
    background-color: #ffd700 !important;
    color: #000000 !important;
    border: 2px solid #ffd700 !important;
}

/* Secondary button specific styling - only for header */
div[data-testid="column"]:nth-child(2) .stButton > button[data-testid="baseButton-secondary"],
div[data-testid="column"]:nth-child(3) .stButton > button[data-testid="baseButton-secondary"] {
    background-color: transparent !important;
    color: #ffd700 !important;
    border: 2px solid #ffd700 !important;
}

/* Hover effects - only for header buttons */
div[data-testid="column"]:nth-child(2) .stButton > button:hover,
div[data-testid="column"]:nth-child(3) .stButton > button:hover {
    background-color: #ffed4e !important;
    color: #000000 !important;
    border-color: #ffed4e !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 8px rgba(255, 215, 0, 0.3) !important;
}

/* Special styling for "ZAČÍT CVIČIT" button */
button[aria-label="🚀 ZAČÍT CVIČIT"] {
    width: 300px !important;
    height: 50px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    margin: 20px auto !important;
    display: block !important;
    border-radius: 25px !important;
    background: linear-gradient(45deg, #ffd700, #ffed4e) !important;
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4) !important;
    transition: all 0.3s ease !important;
}

button[aria-label="🚀 ZAČÍT CVIČIT"]:hover {
    transform: translateY(-3px) scale(1.05) !important;
    box-shadow: 0 8px 25px rgba(255, 215, 0, 0.6) !important;
    background: linear-gradient(45deg, #ffed4e, #fff352) !important;
}

/* Alternative selector for main start button */
div[data-testid="column"] .stButton button:has-text("🚀 ZAČÍT CVIČIT"),
div[data-testid="column"] .stButton > button[data-testid="baseButton-primary"]:contains("ZAČÍT CVIČIT") {
    width: 300px !important;
    height: 50px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    margin: 20px auto !important;
    display: block !important;
    border-radius: 25px !important;
    background: linear-gradient(45deg, #ffd700, #ffed4e) !important;
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4) !important;
}

/* More specific selector using position */
div[data-testid="column"]:nth-child(2) .stButton button {
    width: 300px !important;
    height: 50px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    margin: 20px auto !important;
    display: block !important;
    border-radius: 25px !important;
    background: linear-gradient(45deg, #ffd700, #ffed4e) !important;
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4) !important;
    transition: all 0.3s ease !important;
}

/* Specific button styling for header */
div[data-testid="column"]:nth-child(2) button,
div[data-testid="column"]:nth-child(3) button {
    display: block !important;
    margin-left: auto !important;
    margin-right: 0 !important;
    width: auto !important;
    height: 40px !important;
}

/* Theme variables - Black & Yellow */
:root{
    --bg: #000000;           /* pure black background */
    --surface: #1c1c1c;      /* dark surface with slight lift */
    --primary: #ffd700;      /* vibrant gold/yellow */
    --secondary: #ffffff;    /* white for text */
    --accent: #ffed4e;       /* lighter yellow accent */
    --muted: #b8b8b8;        /* lighter gray for better readability */
    --success: #4ade80;
    --danger: #ef4444;
    --border: #ffd700;       /* yellow borders */
    --text-primary: #ffffff; /* primary white text */
    --text-secondary: #000000; /* black text for yellow backgrounds */
}

/* Responsive Container */
.block-container{
    max-width:1200px; 
    margin:0 auto; 
    padding:2rem 1.5rem; 
    background:var(--bg);
    position: relative;
}

/* Mobile-First Responsive Grid */
@media (max-width: 640px) {
    .block-container { padding: 1rem 0.5rem; }
    .main-header { font-size: 24px; padding: 16px 20px; }
    .stat-number { font-size: 40px; }
    .card { padding: 20px; border-radius: 16px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 12px; font-size: 12px; }
}
@media (max-width: 768px) {
    .block-container { padding: 1.5rem 1rem; }
    .main-header { font-size: 28px; }
    .stat-number { font-size: 48px; }
}
@media (max-width: 1024px) {
    .block-container { max-width: 100%; padding: 1.5rem; }
}

/* Touch-friendly elements */
@media (hover: none) and (pointer: coarse) {
    .stButton>button { min-height: 48px; font-size: 16px; }
    .card { margin-bottom: 16px; }
    .stTextInput>div>div>input { min-height: 48px; }
}
.block-container::before{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        repeating-linear-gradient(90deg, transparent, transparent 50px, rgba(255,215,0,0.03) 50px, rgba(255,215,0,0.03) 51px),
        repeating-linear-gradient(0deg, transparent, transparent 50px, rgba(255,215,0,0.03) 50px, rgba(255,215,0,0.03) 51px);
    pointer-events: none;
    z-index: -1;
}

/* Main header */
.main-header{
    font-size:36px; 
    font-weight:800; 
    color:var(--text-secondary); 
    background: linear-gradient(135deg, var(--primary), var(--accent)); 
    padding:24px 36px; 
    border-radius:18px; 
    text-align:center; 
    margin-bottom:32px; 
    box-shadow: 0 12px 36px rgba(255,215,0,0.4), 
                0 0 60px rgba(255,215,0,0.3); 
    text-shadow: none;
    position: relative;
    overflow: hidden;
    border: 2px solid rgba(255,215,0,0.6);
}
.main-header::before{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: shine 3s infinite;
}
@keyframes shine {
    0% { left: -100%; }
    50% { left: 100%; }
    100% { left: 100%; }
}

.main-sub{
    font-size:18px; 
    font-weight:600; 
    opacity:0.8; 
    margin-left:16px;
}

/* Primary buttons */
.stButton>button{
    background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
    color: var(--text-secondary) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    transition: all .4s cubic-bezier(0.23, 1, 0.32, 1) !important;
    box-shadow: 0 6px 20px rgba(255,215,0,0.3) !important;
    text-transform: none !important;
    border: 2px solid transparent !important;
    position: relative;
    overflow: hidden;
}
.stButton>button::before{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: left 0.5s ease;
}
.stButton>button:hover{
    transform: translateY(-3px) scale(1.05) !important;
    box-shadow: 0 12px 30px rgba(255,215,0,0.6), 
                0 0 40px rgba(255,215,0,0.4) !important;
    border-color: rgba(255,255,255,0.3) !important;
}
.stButton>button:hover::before{
    left: 100%;
}
.stButton>button:active{
    transform: translateY(-1px) scale(1.02) !important;
    box-shadow: 0 6px 20px rgba(255,215,0,0.4) !important;
}

/* Tabs styling */
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
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{
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