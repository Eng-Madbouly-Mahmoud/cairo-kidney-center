import streamlit as st
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
from supabase import create_client, Client
import pandas as pd
import os

# =========================================================
# ⚙️ 1. إعدادات الصفحة الفاخرة والمخصصة لمركز دكتور رشاد برسوم
# =========================================================
st.set_page_config(
    page_title="مركز دكتور رشاد برسوم - إدارة التذاكر", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 2. هندسة الواجهة عبر الـ CSS المتقدم
st.markdown("""
    <style>
        :root { color-scheme: light !important; }
        .stApp { background-color: #F8FAFC; font-family: 'Segoe UI', "Cairo", sans-serif; }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 15px;
            background-color: #E2E8F0;
            padding: 10px;
            border-radius: 16px;
            direction: rtl;
        }
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            white-space: pre-wrap;
            background-color: #FFFFFF;
            border-radius: 12px;
            padding-left: 20px;
            padding-right: 20px;
            font-size: 17px !important;
            font-weight: 800 !important;
            color: #5C4033 !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.06);
            transition: all 0.3s ease;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0EA5E9 0%, #3E2723 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4);
            transform: scale(1.01);
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: "Cairo", sans-serif !important;
            color: #3E2723 !important;
            font-weight: 700 !important;
        }
        
        .stMarkdown p, .stMarkdown span, label {
            font-family: "Cairo", sans-serif !important;
            color: #2D1A12 !important;
            font-weight: 600 !important;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #38BDF8 0%, #0284C7 100%) !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            border-radius: 8px !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2);
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .ticket-card-open {
            background-color: #E0F2FE;
            border-right: 6px solid #5C4033;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .ticket-card-closed {
            background-color: #F1F5F9; 
            border-right: 6px solid #10B981;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# 🔑 3. محرك الاتصال بقاعدة البيانات السحابية
SUPABASE_URL = st.secrets["SUPABASE_URL"].strip().rstrip("/")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip()

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# =========================================================
# 📥 قنوات جلب وحفظ البيانات (المرضى وتذاكر الـ IT)
# =========================================================
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

def load_it_tickets():
    try:
        response = supabase.table("tickets").select("*").execute()
        return response.data or []
    except Exception as e:
        st.error(f"خطأ في جلب التذاكر: {e}")
        return []

def insert_it_ticket(new_ticket):
    try:
        supabase.table("tickets").insert(new_ticket).execute()
        return True
    except Exception as e:
        st.error(f"🛠️ خطأ في إرسال تذكرة الـ IT: {e}")
        return False

def close_it_ticket_in_db(ticket_id, engineer_name):
    try:
        # نقوم بالتحديث بناءً على عمود الـ status والـ id المضمونين في أي جدول تذاكر
        fields = {
            "status": "Closed"
        }
        supabase.table("tickets").update(fields).eq("id", ticket_id).execute()
        return True
    except Exception as e:
        st.error(f"خطأ أثناء إغلاق التذكرة: {e}")
        return False

# =========================================================
# 🎛️ 4. تهيئة الذاكرة التلقائية
# =========================================================
if 'appointments' not in st.session_state:
    st.session_state.appointments = load_appointments()

if 'it_tickets' not in st.session_state:
    st.session_state.it_tickets = load_it_tickets()

if 'active_close_id' not in st.session_state:
    st.session_state.active_close_id = None

# =========================================================
# 🏥 5. هيدر الواجهة
# =========================================================
col_logo, col_banner = st.columns([1, 4])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='font-size: 60px; text-align: center; margin: 0;'>🩺</h1>", unsafe_allow_html=True)

with col_banner:
    st.markdown("""
        <div style='background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%); padding: 22px; border-radius: 12px; border-right: 8px solid #5C4033;'>
            <h1 style='margin: 0; color: #3E2723 !important; font-size: 24px; font-weight: bold;'>مركز دكتور رشاد برسوم - المنظومة السحابية الموحدة</h1>
            <p style='margin: 5px 0 0 0; color: #5C4033 !important; font-size: 15px; font-weight: 600;'>إدارة العيادات التخصصية وجلسات الغسيل الكلوي والدعم التقني المتقدم</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

main_tab3, main_tab2, main_tab1 = st.tabs([
    "⚙️ تكنولوجيا المعلومات والدعم الفني (IT Support)", 
    "🩺 عيادة الأطباء والسجلات السحابية", 
    "📝 عيادات فحص المرضى والحجوزات"
])

# =========================================================
# 1️⃣ تكنولوجيا المعلومات والدعم الفني 
# =========================================================
with main_tab3:
    st.markdown("<h3 style='color: #3E2723;'>⚙️ تسجيل وتتبع بلاغات وأعطال الأجهزة الطبية</h3>", unsafe_allow_html=True)
    
    with st.form("it_ticket_form", clear_on_submit=True):
        t1, t2, t3 = st.columns(3)
        with t1: 
            reporter = st.text_input("👤 اسم المُبلغ:")
        with t2: 
            dept_input = st.text_input("🏥 القسم الطبي:", placeholder="مثال: الغسيل الكلوي، العيادات...")
        with t3: 
            device = st.text_input("💻 اسم الجهاز أو العطل التقني:")
        
        issue_desc = st.text_area("📋 تفاصيل المشكلة أو العطل التقني:")
        
        submit_ticket = st.form_submit_button("📢 إرسال بلاغ الدعم الفني وتوليد تذكرة سلسلة")
        
        if submit_ticket:
            if reporter and device:
                # دمج كافة الحقول والوصف المجهول داخل حقل الـ device لتجنب أي نقص في أعمدة السوبابيز
                combined_device_info = f"{device} ({dept_input}) - {issue_desc}"
                
                new_ticket = {
                    "reporter": reporter,
                    "device": combined_device_info,
                    "status": "Open"
                }
                if insert_it_ticket(new_ticket):
                    st.success("✅ تم تسجيل البلاغ بنجاح في قاعدة البيانات السحابية!")
                    st.session_state.it_tickets = load_it_tickets()
                    st.rerun()
            else:
                st.warning("⚠️ برجاء ملء الحقول الأساسية (اسم المبلغ واسم الجهاز).")

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # =========================================================
    # 🛠️ 6. مركز التحكم وإغلاق التذاكر الفنية الفعلي بكلمة مرور 2026
    # =========================================================
    st.markdown("<h3 style='color: #3E2723;'>🛠️ مركز التحكم وإغلاق التذاكر الفنية</h3>", unsafe_allow_html=True)
    
    tickets_list = load_it_tickets()
    
    if not tickets_list:
        st.info("ℹ️ لا توجد تذاكر مسجلة حالياً في النظام.")
    else:
        eng_name = st.text_input("👷 اسم المهندس المسؤول الحالي:", value="الدعم الفني")
        
        # فرز ذكي وآمن للتذاكر لمنع توقف الكود
        open_tickets = [t for t in tickets_list if str(t.get("status", "Open")).strip().lower() in ["open", "none", ""]]
        closed_tickets = [t for t in tickets_list if str(t.get("status", "")).strip().lower() == "closed"]
        
        tab_open, tab_closed = st.tabs([f"📥 تذاكر مفتوحة وقيد الانتظار ({len(open_tickets)})", f"✅ تذاكر تم حلها وإغلاقها ({len(closed_tickets)})"])
        
        with tab_open:
            if not open_tickets:
                st.success("🎉 ممتاز! لا توجد أي تذاكر مفتوحة حالياً.")
            else:
                # بوب آب الباسورد غير المرئي عند طلب إغلاق تذكرة
                if st.session_state.active_close_id:
                    st.markdown("#### 🔒 تأكيد الإغلاق الآمن للمهندسين")
                    password_input = st.text_input("الرجاء إدخال كلمة مرور المهندس للإغلاق:", type="password", key="secure_pwd_field")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✔️ تأكيد وإغلاق التذكرة الآن"):
                            if password_input == "2026":
