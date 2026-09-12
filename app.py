import streamlit as st
import json
import os
from glob import glob

# Must be the first Streamlit command
st.set_page_config(
    page_title="VLSI Prep Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Typography & Hide Defaults */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #f8fafc; }
    
    /* Headers */
    h1 { color: #0f172a; font-weight: 800; letter-spacing: -0.02em; }
    h2, h3 { color: #1e293b; font-weight: 700; letter-spacing: -0.01em; }

    /* Custom Dashboard Grid (Fixes Truncation) */
    .dash-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 10px;
        margin-bottom: 30px;
    }
    .dash-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .dash-title {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .dash-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.1;
    }
    .status-pass { color: #10b981; }
    .status-review { color: #f59e0b; font-size: 1.5rem; } /* Slightly smaller to ensure fit */

    /* Explanation Box */
    .explanation-box {
        background: linear-gradient(to right, #f8fafc, #f1f5f9);
        border-left: 4px solid #3b82f6;
        padding: 18px 24px;
        border-radius: 0 8px 8px 0;
        margin-top: 15px;
        font-size: 0.95rem;
        color: #334155;
        line-height: 1.6;
        box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.02);
    }
    
    /* Submit Button Styling Override */
    div.stButton > button:first-child {
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
@st.cache_data
def load_quiz(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- Sidebar Navigation & Setup ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9334/9334173.png", width=55)
    st.markdown("## VLSI Prep")
    st.markdown("Professional silicon engineering assessments.")
    st.markdown("---")
    
    quiz_files = glob("quizzes/*.json")
    if not quiz_files:
        quiz_files = glob("*.json")
    
    if not quiz_files:
        st.error("No quiz files found! Create a 'quizzes' folder and add your JSON.")
        st.stop()

    topic_map = {os.path.basename(f).replace(".json", "").replace("_", " ").title(): f for f in quiz_files}
    selected_topic = st.selectbox("📚 Select Domain", list(topic_map.keys()))
    
    mode = st.radio("⚙️ Assessment Mode", ["Exam Mode", "Practice Mode"], 
                    captions=["Submit at the end for a score.", "Get immediate feedback."])
    
    st.markdown("---")
    if st.button("🔄 Reset Assessment", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

quiz_data = load_quiz(topic_map[selected_topic])
total_q = len(quiz_data)

# --- Session State Initialization ---
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- Top Header ---
colA, colB = st.columns([2.5, 1.5])
with colA:
    st.title(selected_topic)
    st.caption(f"Comprehensive Assessment • {total_q} Questions")
with colB:
    st.markdown("<br>", unsafe_allow_html=True)
    answered_count = sum(1 for v in st.session_state.answers.values() if v is not None)
    st.progress(answered_count / total_q, text=f"Progress: {answered_count} / {total_q} Answered")

st.markdown("<br>", unsafe_allow_html=True)

# --- Main Quiz UI ---
if mode == "Exam Mode":
    if not st.session_state.submitted:
        # 1. Taking the Exam
        with st.form("exam_form", border=False):
            for idx, item in enumerate(quiz_data):
                with st.container(border=True):
                    st.markdown(f"**Q{idx + 1}. {item['question']}**")
                    selected = st.radio(
                        label="Options",
                        options=item["options"],
                        key=f"q_{idx}",
                        index=None,
                        label_visibility="collapsed"
                    )
                    st.session_state.answers[idx] = selected
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
            with submit_col2:
                submitted = st.form_submit_button("🏁 Submit Final Assessment", use_container_width=True, type="primary")
                if submitted:
                    st.session_state.submitted = True
                    st.rerun()

    else:
        # 2. Post-Exam Analytics Dashboard
        score = sum(1 for idx, item in enumerate(quiz_data) if st.session_state.answers.get(idx) == item["options"][item["correct_index"]])
        accuracy = (score / total_q) * 100
        unanswered = sum(1 for i in range(total_q) if st.session_state.answers.get(i) is None)
        
        status_text = "✅ PASSED" if accuracy >= 70 else "⚠️ NEEDS REVIEW"
        status_class = "status-pass" if accuracy >= 70 else "status-review"

        st.success("Assessment Completed Successfully!")
        
        # Custom HTML Scoreboard (Bypasses Streamlit's truncation issue)
        st.markdown(f"""
        <div class="dash-grid">
            <div class="dash-card">
                <div class="dash-title">Final Score</div>
                <div class="dash-value">{score} / {total_q}</div>
            </div>
            <div class="dash-card">
                <div class="dash-title">Accuracy</div>
                <div class="dash-value">{accuracy:.1f}%</div>
            </div>
            <div class="dash-card">
                <div class="dash-title">Unanswered</div>
                <div class="dash-value">{unanswered}</div>
            </div>
            <div class="dash-card">
                <div class="dash-title">Status</div>
                <div class="dash-value {status_class}">{status_text}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Detailed Performance Review")
        
        # Review Questions
        for idx, item in enumerate(quiz_data):
            user_choice = st.session_state.answers.get(idx)
            correct_answer = item["options"][item["correct_index"]]
            is_correct = user_choice == correct_answer
            is_skipped = user_choice is None
            
            border_color = "🟢" if is_correct else ("⚪" if is_skipped else "🔴")
            
            with st.expander(f"{border_color} Question {idx + 1}"):
                st.markdown(f"**{item['question']}**")
                
                if is_correct:
                    st.success(f"**Your Answer:** {user_choice}")
                elif is_skipped:
                    st.warning(f"**Skipped.** Correct Answer: {correct_answer}")
                else:
                    st.error(f"**Your Answer:** {user_choice}")
                    st.success(f"**Correct Answer:** {correct_answer}")
                
                st.markdown(f"""
                <div class='explanation-box'>
                    <strong>💡 Expert Explanation</strong><br><br>{item['explanation']}
                </div>
                """, unsafe_allow_html=True)

else:
    # --- Practice Mode ---
    st.info("💡 **Practice Mode:** Answers and detailed explanations are revealed immediately after selection.")
    
    for idx, item in enumerate(quiz_data):
        with st.container(border=True):
            st.markdown(f"**Q{idx + 1}. {item['question']}**")
            
            user_choice = st.radio(
                label="Options",
                options=item["options"],
                key=f"prac_{idx}",
                index=None,
                label_visibility="collapsed"
            )
            
            if user_choice is not None:
                correct_answer = item["options"][item["correct_index"]]
                
                if user_choice == correct_answer:
                    st.success("✅ **Correct**")
                else:
                    st.error(f"❌ **Incorrect.** The correct answer is: {correct_answer}")
                
                st.markdown(f"""
                <div class='explanation-box'>
                    <strong>💡 Expert Explanation</strong><br><br>{item['explanation']}
                </div>
                """, unsafe_allow_html=True)
