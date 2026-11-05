import streamlit as st
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
from supabase import create_client, Client
import pandas as pd
import io
import os

# =========================================================
# ⚙️ 1. إعدادات الصفحة الفاخرة المخصصة للمراكز الطبية الكبرى
# =========================================================
st.set_page_config(
    page_title="Cairo Kidney Center - Integrated Medical ERP Suite", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 2. هندسة الواجهة عبر الـ CSS المتقدم (الهوية الطبية الفاخرة)
st.markdown("""
    <style>
        /* تثبيت الخلفية والألوان النظيفة للمستشفيات */
        :root { color-scheme: light !important; }
        .stApp { background-color: #F8FAFC; font-family: 'Segoe UI', "Cairo", sans-serif; }
        
        /* تصميم الهيدر الطبي الفاخر */
        .medical-hero-banner {
            background: linear-gradient(135deg, #0284C7 0%, #1E3A8A 100%);
            padding: 30px;
            border-radius: 16px;
            color: #FFFFFF !important;
            box-shadow: 0 10px 25px rgba(2, 132, 199, 0.15);
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        /* تحسين التبويبات والأزرار والخطوط */
        h1, h2, h3, h4, .stMarkdown p, .stMarkdown span {
            font-family: "Cairo", sans-serif !important;
        }
        
        /* تجميل الأزرار لتكون تفاعلية ومريحة للمستخدم */
        .stButton > button {
            background: linear-gradient(135deg, #38BDF8 0%, #0284C7 100%) !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2);
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(2, 132, 199, 0.35);
        }
    </style>
""", unsafe_allow_html=True)

# 🔑 3. محرك الاتصال بقاعدة بيانات الهدى (المشروع المشترك)
SUPABASE_URL = st.secrets["SUPABASE_URL"].strip().rstrip("/")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip()

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# =========================================================
# 📥 محركات وقنوات معالجة البيانات السحابية (CRUD Database Engine)
# =========================================================

# --- قنوات موديول المرضى والعيادات الكلوية ---
def load_appointments():
    try:
        response = supabase.table("appointments").select("*").order("id", desc=False).execute()
        return response.data or []
    except Exception:
        return []

def insert_appointment(new_app):
    try:
        supabase.table("appointments").insert(new_app).execute()
        return True
    except Exception as e:
        st.error(f"خطأ سحابي في ملف المريض: {e}")
        return False

def update_appointment_in_db(app_id, fields):
    try:
        supabase.table("appointments").update(fields).eq("id", app_id).execute()
        return True
    except Exception:
        return False

# --- قنوات موديول تكنولوجيا المعلومات والشبكات المشتركة (IT Support) ---
def load_it_tickets():
    try:
        response = supabase.table("tickets").select("*").order("id", desc=False).execute()
        return response.data or []
    except Exception:
        return []

def insert_it_ticket(new_ticket):
    try:
        supabase.table("tickets").insert(new_ticket).execute()
        return True
    except Exception as e:
        st.error(f"خطأ في إرسال بلاغ الـ IT: {e}")
        return False

# =========================================================
# 🎛️ 4. المزامنة المباشرة وتهيئة الذاكرة التلقائية
# =========================================================
if 'appointments' not in st.session_state:
    st.session_state.appointments = load_appointments()
if 'it_tickets' not in st.session_state:
    st.session_state.it_tickets = load_it_tickets()

# ترقيم الحجوزات الطبية
if 'patient_next_id' not in st.session_state:
    if st.session_state.appointments:
        st.session_state.patient_next_id = max([int(a['id']) for a in st.session_state.appointments]) + 1
    else:
        st.session_state.patient_next_id = 5001

# ترقيم بلاغات الـ IT للأعطال التقنية
if 'it_next_id' not in st.session_state:
    if st.session_state.it_tickets:
        st.session_state.it_next_id = max([int(t['id']) for t in st.session_state.it_tickets]) + 1
    else:
        st.session_state.it_next_id = 101


# =========================================================
# 🏥 5. هيدر الواجهة الاحترافية الكبرى وعرض اللوجو الدائري
# =========================================================
col_logo, col_banner = st.columns([1, 4])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='font-size: 90px; text-align: center; margin: 0;'>🩺</h1>", unsafe_allow_html=True)

with col_banner:
    st.markdown("""
        <div style='background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%); padding: 22px; border-radius: 12px; border-right: 8px solid #0284C7;'>
            <h1 style='margin: 0; color: #1E3A8A !important; font-size: 26px; font-weight: bold;'>مركز القاهرة لأمراض الكلى | Cairo Kidney Center</h1>
            <p style='margin: 5px 0 0 0; color: #0369A1 !important; font-size: 15px; font-weight: 600;'>المنظومة السحابية الموحدة لإدارة العيادات التخصصية وجلسات الغسيل الكلوي والدعم التقني المتكامل</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# تبويبات الأنظمة المشتركة في الواجهة الحديثة
main_tab1, main_tab2, main_tab3 = st.tabs([
    "📝 عيادات فحص المرضى والحجوزات", 
    "🩺 عيادة الأطباء والسجلات السحابية", 
    "⚙️ تكنولوجيا المعلومات والدعم الفني للعيادات (IT Modules)"
])

# =========================================================
# 1️⃣ عيادات فحص المرضى والحجوزات (التبويب الأول)
# =========================================================
with main_tab1:
    st.markdown("<h3 style='color: #0284C7;'>📥 حجز وتكويد ملف طبي لمريض جديد</h3>", unsafe_allow_html=True)
    with st.form("patient_booking_form", clear_on_submit=True):
        p1, p2 = st.columns(2)
        with p1: name = st.text_input("👤 اسم المريض ثلاثي (Patient Name):")
        with p2: phone = st.text_input("📞 رقم الهاتف المحمول:")
        
        doctor = st.selectbox("🩺 العيادة الطبية والاستشاري المسؤول:", [
            "أ.د. أحمد عبد الرحمن - استشاري أمراض وزرع الكلى",
            "أ.د. محمود الشافعي - استشاري غسيل الكلى والأوعية الدموية",
            "د. سارة عزمي - أخصائي أمراض الكلى ومتابعة وظائف الكلى"
        ])
        notes = st.text_area("📋 الملاحظات الطبية الأولية أو شكوى المريض:")
        
        submit_p = st.form_submit_button("🚀 ترحيل وإصدار تذكرة الفحص الطبية")
        if submit_p:
            if name.strip() and phone.strip():
                payload = {
                    "id": int(st.session_state.patient_next_id),
                    "patient_name": name,
                    "phone": phone,
                    "doctor_name": doctor,
                    "status": "Pending (في الانتظار) ⏳",
                    "notes": notes if notes.strip() else "فحص دوري لوظ
