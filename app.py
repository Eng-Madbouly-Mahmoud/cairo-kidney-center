import streamlit as st
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
from supabase import create_client, Client
import pandas as pd
import os

# =========================================================
# ⚙️ 1. إعدادات الصفحة
# =========================================================
st.set_page_config(
    page_title="مستشفى القاهرة للكلى - مركز دكتور رشاد برسوم", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 2. تنسيقات CSS احترافية وتصميم تذاكر IT عصرية
st.markdown("""
    <style>
        :root { color-scheme: light !important; }
        .stApp { background-color: #F8FAFC; font-family: 'Segoe UI', "Cairo", sans-serif; direction: rtl; }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: #E2E8F0;
            padding: 8px;
            border-radius: 14px;
            direction: rtl;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: #FFFFFF;
            border-radius: 10px;
            font-size: 16px !important;
            font-weight: 700 !important;
            color: #334155 !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
            color: #FFFFFF !important;
        }
        
        h1, h2, h3, h4, label {
            font-family: "Cairo", sans-serif !important;
            color: #1E293B !important;
            font-weight: 700 !important;
            text-align: right;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 10px 24px;
            width: 100%;
        }

        /* تصميم بطاقات التذاكر الاحترافية */
        .it-ticket-card {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            border-right: 6px solid #0284C7;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            text-align: right;
        }
        .ticket-badge {
            background: #E0F2FE;
            color: #0369A1;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 🔑 3. الربط بقاعدة بيانات Supabase
# =========================================================
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"].strip().rstrip("/")
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip()
except Exception:
    st.error("⚠️ لم يتم العثور على مفاتيح الربط في Secrets. يرجى ضبط SUPABASE_URL و SUPABASE_KEY.")
    st.stop()

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# =========================================================
# 📥 دوال قواعد البيانات
# =========================================================
def load_appointments():
    try:
        res = supabase.table("appointments").select("*").order("id", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"خطأ في جلب المواعيد: {e}")
        return []

def insert_appointment(data):
    try:
        supabase.table("appointments").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"خطأ في حفظ الحجز: {e}")
        return False

def load_it_tickets():
    try:
        res = supabase.table("tickets").select("*").order("id", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"خطأ في جلب التذاكر: {e}")
        return []

def insert_it_ticket(data):
    try:
        supabase.table("tickets").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"خطأ في تسجيل التذكرة: {e}")
        return False

def close_it_ticket_in_db(ticket_id, eng_name):
    try:
        update_data = {
            "status": "Closed",
            "closed_by": eng_name,
            "closed_at": datetime.now().isoformat()
        }
        supabase.table("tickets").update(update_data).eq("id", ticket_id).execute()
        return True
    except Exception as e:
        st.error(f"خطأ أثناء إغلاق التذكرة: {e}")
        return False

# تهيئة الذاكرة
if 'it_tickets' not in st.session_state:
    st.session_state.it_tickets = load_it_tickets()
if 'appointments' not in st.session_state:
    st.session_state.appointments = load_appointments()

# =========================================================
# 🏥 الهيدر الرئيسي
# =========================================================
col_logo, col_banner = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png")
    else:
        st.markdown("<h1 style='text-align: center;'>🩺</h1>", unsafe_allow_html=True)

with col_banner:
    st.markdown("""
        <div style='background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%); padding: 18px; border-radius: 12px; border-right: 8px solid #0369A1; text-align: right;'>
            <h2 style='margin: 0; color: #0C4A6E !important;'>مستشفى القاهرة للكلى - مركز دكتور رشاد برسوم</h2>
            <p style='margin: 5px 0 0 0; color: #0369A1 !important; font-size: 15px;'>إدارة العيادات التخصصية، جلسات الغسيل الكلوي، والدعم الفني الذكي</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# التبويبات الثلاثة
tab_it, tab_records, tab_booking = st.tabs([
    "⚙️ تكنولوجيا المعلومات والدعم الفني (IT Support)",
    "🩺 عيادة الأطباء والسجلات السحابية",
    "📝 حجز مواعيد الفحص والعيادات"
])

# =========================================================
# 1️⃣ تبويب الدعم الفني
# =========================================================
with tab_it:
    st.markdown("### 📢 تسجيل بلاغ عطل فني أو صيانة جهاز")
    
    with st.form("it_ticket_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            reporter = st.text_input("👤 اسم المُبلّغ:")
        with c2:
            dept = st.text_input("🏥 القسم أو الوحدة:", placeholder="مثل: وحدة الغسيل الكلوي، الاستقبال...")
        with c3:
            device = st.text_input("💻 اسم الجهاز أو الأداة:")
            
        issue = st.text_area("📋 تفاصيل المشكلة أو العطل بدقة:")
        submit_btn = st.form_submit_button("🚀 إرسال البلاغ لقسم الدعم الفني")
        
        if submit_btn:
            if reporter and device and issue:
                ticket_data = {
                    "reporter": reporter,
                    "dept": dept,
                    "device": device,
                    "issue": issue,
                    "status": "Open"
                }
                if insert_it_ticket(ticket_data):
                    st.success("✅ تم حفظ البلاغ بنجاح في قاعدة البيانات!")
                    st.session_state.it_tickets = load_it_tickets()
                    st.rerun()
            else:
                st.warning("⚠️ يرجى ملء اسم المُبلّغ، اسم الجهاز، وتفاصيل المشكلة على الأقل.")

    st.markdown("---")
    st.markdown("### 🛠️ لوحة متابعة وإغلاق التذاكر الفنية")
    
    tickets_list = load_it_tickets()
    open_tickets = [t for t in tickets_list if str(t.get("status", "Open")).lower() == "open"]
    closed_tickets = [t for t in tickets_list if str(t.get("status", "")).lower() == "closed"]

    sub_tab1, sub_tab2 = st.tabs([f"📥 البلاغات المفتوحة ({len(open_tickets)})", f"✅ البلاغات المنجزة ({len(closed_tickets)})"])

    with sub_tab1:
        if not open_tickets:
            st.success("🎉 لا توجد أي أعطال مفتوحة حالياً، كل الأجهزة تعمل بكفاءة!")
        else:
            eng_name = st.text_input("👷 اسم مهندس الدعم الفني المعالج:", value="مهندس الـ IT", key="eng_name_input")
            st.markdown("<br>", unsafe_allow_html=True)
            
            for t in open_tickets:
                ticket_dept = t.get('dept') or t.get('department') or 'عام'
                ticket_issue = t.get('issue') or t.get('issue_desc') or 'لا توجد تفاصيل'
                
                st.markdown(f"""
                    <div class="it-ticket-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #0284C7;">🎫 تذكرة رقم #{t.get('id')} - {t.get('device')}</h4>
                            <span class="ticket-badge">القسم: {ticket_dept}</span>
                        </div>
                        <p style="margin: 12px 0 6px 0; color: #334155;"><strong>👤 المُبلّغ:</strong> {t.get('reporter')}</p>
                        <p style="margin: 0 0 10px 0; color: #475569;"><strong>📋 تفاصيل العطل:</strong> {ticket_issue}</p>
                        <p style="margin: 0; color: #94A3B8; font-size: 12px;"><strong>🕒 وقت البلاغ:</strong> {str(t.get('created_at', ''))[:16]}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                c_pwd, c_btn = st.columns([2, 1])
                with c_pwd:
                    pwd = st.text_input("رمز الأمان لإغلاق التذكرة:", type="password", key=f"pwd_{t['id']}")
                with c_btn:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("✔️ إغلاق التذكرة", key=f"close_btn_{t['id']}"):
                        if pwd == "2026":
                            if close_it_ticket_in_db(t["id"], eng_name):
                                st.success(f"تم إغلاق التذكرة #{t['id']} بنجاح!")
                                st.session_state.it_tickets = load_it_tickets()
                                st.rerun()
                        else:
                            st.error("❌ رمز الأمان غير صحيح.")
                st.markdown("---")

    with sub_tab2:
        if not closed_tickets:
            st.info("لا توجد تذاكر مغلقة حتى الآن.")
        else:
            formatted_closed = []
            for t in closed_tickets:
                formatted_closed.append({
                    "رقم البلاغ": t.get("id"),
                    "المُبلّغ": t.get("reporter"),
                    "الجهاز": t.get("device"),
                    "القسم": t.get("dept") or t.get("department"),
                    "تفاصيل العطل": t.get("issue") or t.get("issue_desc"),
                    "المهندس المسؤول": t.get("closed_by"),
                    "تاريخ الإغلاق": str(t.get("closed_at", ""))[:16]
                })
            df_closed = pd.DataFrame(formatted_closed)
            st.dataframe(df_closed, use_container_width=True)

# =========================================================
# 2️⃣ تبويب سجلات المرضى والعيادات
# =========================================================
with tab_records:
    st.markdown("### 📋 سجلات المرضى والمواعيد المسجلة")
    apps = load_appointments()
    if apps:
        df_apps = pd.DataFrame(apps)[["id", "patient_name", "phone", "clinic_type", "notes", "created_at"]]
        df_apps.columns = ["رقم الملف", "اسم المريض", "رقم الهاتف", "العيادة / الخدمة", "ملاحظات طبية", "تاريخ التسجيل"]
        st.dataframe(df_apps, use_container_width=True)
    else:
        st.info("لا توجد مواعيد مسجلة حتى الآن.")

# =========================================================
# 3️⃣ تبويب حجز موعد جديد
# =========================================================
with tab_booking:
    st.markdown("### 📝 حجز كشف أو جلسة غسيل جديدة")
    with st.form("book_appointment_form", clear_on_submit=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            p_name = st.text_input("اسم المريض الثلاثي:")
            p_clinic = st.selectbox("نوع الكشف / القسم:", ["وحدة الغسيل الكلوي", "عيادة الكلى التخصصية", "فحوصات الباطنة", "متابعة ما بعد الزراعة"])
        with col_p2:
            p_phone = st.text_input("رقم الهاتف للتواصل:")
            p_notes = st.text_area("تاريخ الحالة أو ملاحظات التحويل:")
            
        submit_app = st.form_submit_button("💾 تأكيد وحفظ الحجز السحابي")
        if submit_app:
            if p_name and p_phone:
                app_data = {
                    "patient_name": p_name,
                    "phone": p_phone,
                    "clinic_type": p_clinic,
                    "notes": p_notes,
                    "status": "Confirmed"
                }
                if insert_appointment(app_data):
                    st.success("✅ تم حفظ ملف الحجز بنجاح!")
                    st.session_state.appointments = load_appointments()
                    st.rerun()
            else:
                st.warning("⚠️ يرجى إدخال اسم المريض ورقم الهاتف.")
