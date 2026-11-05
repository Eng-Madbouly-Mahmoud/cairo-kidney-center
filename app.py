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
    page_title="مركز دكتور رشاد برسوم - تحت الإنشاء", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 2. هندسة الواجهة عبر الـ CSS المتقدم (تكبير التابّات والخطوط بشكل احترافي)
st.markdown("""
    <style>
        :root { color-scheme: light !important; }
        .stApp { background-color: #F8FAFC; font-family: 'Segoe UI', "Cairo", sans-serif; }
        
        /* تكبير وتوسيع التابّات (Tabs) لتكون بارزة وعصرية جداً */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            background-color: #E2E8F0;
            padding: 12px;
            border-radius: 16px;
            direction: rtl;
        }
        .stTabs [data-baseweb="tab"] {
            height: 65px;
            white-space: pre-wrap;
            background-color: #FFFFFF;
            border-radius: 12px;
            padding-left: 25px;
            padding-right: 25px;
            font-size: 19px !important;
            font-weight: 800 !important;
            color: #1E3A8A !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.06);
            transition: all 0.3s ease;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0284C7 0%, #1E3A8A 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.4);
            transform: scale(1.01);
        }
        
        /* تحسين خطوط العناوين والنصوص الداخلية */
        h1, h2, h3, h4, .stMarkdown p, .stMarkdown span {
            font-family: "Cairo", sans-serif !important;
        }
        
        /* تجميل الأزرار */
        .stButton > button {
            background: linear-gradient(135deg, #38BDF8 0%, #0284C7 100%) !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 16px !important;
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

def update_appointment_in_db(app_id, fields):
    try:
        supabase.table("appointments").update(fields).eq("id", app_id).execute()
        return True
    except Exception:
        return False

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
        st.error(f"خطأ في إرسال تذكرة الـ IT: {e}")
        return False

# =========================================================
# 🎛️ 4. تهيئة الذاكرة التلقائية وترقيم الملفات والبلاغات
# =========================================================
if 'appointments' not in st.session_state:
    st.session_state.appointments = load_appointments()

if 'it_tickets' not in st.session_state:
    st.session_state.it_tickets = load_it_tickets()

if 'patient_next_id' not in st.session_state:
    if st.session_state.appointments:
        st.session_state.patient_next_id = max([int(a['id']) for a in st.session_state.appointments]) + 1
    else:
        st.session_state.patient_next_id = 5001

if 'it_next_id' not in st.session_state:
    if st.session_state.it_tickets:
        st.session_state.it_next_id = max([int(t['id']) for t in st.session_state.it_tickets]) + 1
    else:
        st.session_state.it_next_id = 101

# =========================================================
# 🏥 5. هيدر الواجهة (عرض اللوجو واسم مركز دكتور رشاد برسوم)
# =========================================================
col_logo, col_banner = st.columns([1, 4])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='font-size: 80px; text-align: center; margin: 0;'>🩺</h1>", unsafe_allow_html=True)

with col_banner:
    st.markdown("""
        <div style='background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%); padding: 22px; border-radius: 12px; border-right: 8px solid #0284C7;'>
            <h1 style='margin: 0; color: #1E3A8A !important; font-size: 26px; font-weight: bold;'>مركز دكتور رشاد برسوم - (تحت الإنشاء)</h1>
            <p style='margin: 5px 0 0 0; color: #0369A1 !important; font-size: 16px; font-weight: 600;'>المنظومة السحابية الموحدة لإدارة العيادات التخصصية وجلسات الغسيل الكلوي والدعم التقني</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 📑 التابّات الرئيسية (جعل تكنولوجيا المعلومات كأول تبويب على اليسار)
main_tab3, main_tab2, main_tab1 = st.tabs([
    "⚙️ تكنولوجيا المعلومات والدعم الفني (IT Support)", 
    "🩺 عيادة الأطباء والسجلات السحابية", 
    "📝 عيادات فحص المرضى والحجوزات"
])

# =========================================================
# 1️⃣ تكنولوجيا المعلومات والدعم الفني (التبويب الأول على اليسار - تذاكر الأعطال)
# =========================================================
with main_tab3:
    st.markdown("<h3 style='color: #0284C7;'>⚙️ تسجيل وتتبع بلاغات وأعطال الأجهزة الطبية</h3>", unsafe_allow_html=True)
    
    with st.form("it_ticket_form", clear_on_submit=True):
        t1, t2 = st.columns(2)
        with t1: reporter = st.text_input("👤 اسم المُبلغ أو القسم الطبي:")
        with t2: device = st.text_input("💻 اسم الجهاز أو العطل التقني:")
        
        issue_desc = st.text_area("📋 تفاصيل المشكلة أو العطل التقني:")
        submit_it = st.form_submit_button("🚀 إرسال بلاغ الدعم الفني وتوليد تذكرة مسلسلة")
        
        if submit_it:
            if reporter.strip() and device.strip():
                # تم دمج بيانات الجهاز والمشكلة في عمود 'issue' المتوافق مع الجدول لتفادي أي أخطاء
                full_issue_text = f"الجهاز: {device} | التفاصيل: {issue_desc if issue_desc.strip() else 'لا توجد تفاصيل'}"
                ticket_payload = {
                    "id": int(st.session_state.it_next_id),
                    "name": reporter,
                    "issue": full_issue_text,
                    "status": "Pending (قيد الانتظار) ⏳",
                    "created_at": datetime.now().strftime("%Y-%m-%d %I:%M %p")
                }
                if insert_it_ticket(ticket_payload):
                    st.session_state.it_tickets = load_it_tickets()
                    st.success(f"🛠️ تم إصدار وتثبيت تذكرة الدعم الفني المسلسلة برقم: #{st.session_state.it_next_id}")
                    st.session_state.it_next_id += 1
                    st.rerun()
            else:
                st.error("❌ يرجى ملء اسم المُبلغ واسم الجهاز لإرسال البلاغ.")
                
    st.markdown("---")
    st.markdown("#### 📋 سجل تذاكر البلاغات والاتصالات الفنية المسلسلة:")
    st.session_state.it_tickets = load_it_tickets()
    if st.session_state.it_tickets:
        df_tickets = pd.DataFrame(st.session_state.it_tickets)
        st.dataframe(df_tickets, use_container_width=True)
    else:
        st.info("لا توجد بلاغات تقنية مسجلة حالياً.")

# =========================================================
# 2️⃣ عيادة الأطباء والسجلات السحابية (التبويب الثاني - محمي بكلمة مرور 1234)
# =========================================================
with main_tab2:
    st.markdown("<h3 style='color: #1E3A8A;'>🖥️ شاشة مراقبة وتحديث الفحوصات الطبية للأطباء</h3>", unsafe_allow_html=True)
    pass_doctor = st.text_input("🔑 أدخل كلمة مرور الإدارة الطبية المعتمدة للعيادة (1234):", type="password", key="doc_pass")
    
    if pass_doctor == "1234":
        st.success("🔓 تم مصادقة الصلاحية الطبية الحساسة.")
        st.session_state.appointments = load_appointments()
        
        if st.session_state.appointments:
            df_app = pd.DataFrame(st.session_state.appointments)
            st.dataframe(df_app, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### 🩺 تحديث حالة الفحص الطبي وإصدار الروشتة السحابية:")
            p_ids = [int(a['id']) for a in st.session_state.appointments]
            
            with st.form("doctor_update_form"):
                sel_id = st.selectbox("اختر رقم الملف الطبي للمريض:", p_ids)
                new_status = st.selectbox("الحالة الطبية الحالية:", ["Examined (تم الفحص وصرف العلاج) ✅", "In Progress (داخل غرفة الكشف الحين) ⚙️"])
                medicines = st.text_input("العلاج والروشتة أو تحديث التشخيص الطبي:")
                
                submit_doc = st.form_submit_button("🔄 تحديث وحفظ الملف الطبي للمريض فوراً")
                if submit_doc:
                    fields = {
                        "status": new_status,
                        "notes": medicines if medicines.strip() else "متابعة مستقرة",
                        "updated_at": datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    }
                    if update_appointment_in_db(sel_id, fields):
                        st.success("✅ تم تحديث بيانات المريض بنجاح في قاعدة البيانات السحابية.")
                        st.session_state.appointments = load_appointments()
                        st.rerun()
                    else:
                        st.error("❌ حدث خطأ أثناء التحديث السحابي.")
        else:
            st.info("لا توجد حجوزات مسجلة حالياً.")
    elif pass_doctor:
        st.error("❌ كلمة المرور غير صحيحة.")

# =========================================================
# 3️⃣ عيادات فحص المرضى والحجوزات (التبويب الثالث - محمي بكلمة مرور 1234)
# =========================================================
with main_tab1:
    st.markdown("<h3 style='color: #0284C7;'>📥 حجز وتكويد ملف طبي لمريض جديد</h3>", unsafe_allow_html=True)
    
    pass_booking = st.text_input("🔑 أدخل كلمة مرور الحجوزات الطبية (1234):", type="password", key="booking_pass")
    
    if pass_booking == "1234":
        st.success("🔓 تمت مصادقة صلاحية الحجز بنجاح.")
        with st.form("patient_booking_form", clear_on_submit=True):
            p1, p2 = st.columns(2)
            with p1: name = st.text_input("👤 اسم المريض ثلاثي (Patient Name):")
            with p2: phone = st.text_input("📞 رقم الهاتف المحمول:")
            
            doctor = st.selectbox("🩺 الطبيب المعالج المسؤول:", [
                "د. رفيق فلتس - استشاري أمراض وزرع الكلى",
                "د. رشاد برسوم - استشاري أمراض الكلى"
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
                        "notes": notes if notes.strip() else "فحص دوري لوظائف الكلى",
                        "created_at": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                        "updated_at": "لم تُحدث بعد"
                    }
                    if insert_appointment(payload):
                        st.session_state.appointments = load_appointments()
                        st.success(f"🎉 تم حجز التذكرة بنجاح! رقم الملف الطبي الموحد للمريض هو: #{st.session_state.patient_next_id}")
                        st.session_state.patient_next_id += 1
                        st.rerun()
                else:
                    st.error("❌ يرجى ملء اسم المريض ورقم الهاتف المحمول لإتمام الحجز السحابي.")
    elif pass_booking:
        st.error("❌ كلمة المرور غير صحيحة. يرجى إدخال (1234) لفتح نظام الحجز.")
    else:
        st.info("ℹ️ يرجى إدخال كلمة المرور المعتمدة (1234) لفتح نموذج الحجز وتكويد المرضى.")
