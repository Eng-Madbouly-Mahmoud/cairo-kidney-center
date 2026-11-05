import streamlit as st
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
from supabase import create_client, Client
import pandas as pd
import io
import os

# 🔑 جلب إعدادات الاتصال الآمنة والديناميكية عبر نظام الحماية (Secrets)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# تهيئة عميل Supabase لمرة واحدة في الجلسة
@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# 📥 دالة جلب بيانات الحجوزات الطبية من السحاب
def load_appointments():
    try:
        response = supabase.table("appointments").select("*").order("id", desc=False).execute()
        return response.data or []
    except Exception:
        return []

# 💾 دالة حفظ حجز طبي جديد في السحاب
def insert_appointment(new_app):
    try:
        db_data = {
            "id": int(new_app["id"]),
            "patient_name": new_app["patient_name"],
            "phone": new_app["phone"],
            "doctor_name": new_app["doctor_name"],
            "status": "Pending (قيد الانتظار)",
            "notes": new_app["notes"],
            "created_at": new_app["created_at"],
            "updated_at": "لم تُحدث بعد"
        }
        supabase.table("appointments").insert(db_data).execute()
        return True
    except Exception as e:
        st.error(f"خطأ في حفظ الحجز السحابي: {e}")
        return False

# 🔄 دالة تحديث حالة الحجز (تم الكشف / إلغاء / تأجيل)
def update_appointment_in_db(app_id, updated_fields):
    try:
        supabase.table("appointments").update(updated_fields).eq("id", app_id).execute()
        return True
    except Exception as e:
        st.error(f"خطأ في تحديث البيانات الطبية: {e}")
        return False

# تهيئة مخزن البيانات وجلب البيانات من السحاب لضمان المزامنة الثابتة
if 'appointments' not in st.session_state:
    st.session_state.appointments = load_appointments()

# ضبط الترقيم التلقائي للملفات الطبية والحجوزات
if 'next_id' not in st.session_state:
    if st.session_state.appointments:
        max_id = max([int(a['id']) for a in st.session_state.appointments])
        st.session_state.next_id = max_id + 1
    else:
        st.session_state.next_id = 1001

# ⚙️ إعدادات الصفحة بنمط الهوية الطبية لمركز الكلى
st.set_page_config(page_title="Cairo Kidney Center - مركز القاهرة لأمراض الكلى", page_icon="🏥", layout="wide")

# =========================================================
# 🎨 حقن هوية وتنسيقات CSS الدقيقة (الأبيض * اللبني الطبي)
# =========================================================
st.markdown("""
    <style>
        /* إجبار الوضع الفاتح وتثبيت الألوان الاحترافية للمراكز الطبية */
        :root {
            color-scheme: light !important;
        }
        .stApp {
            background-color: #FFFFFF;
        }
        /* تنسيق النصوص لتكون واضحة باللون الكحلي والرمادي الداكن */
        .stMarkdown p, .stMarkdown b, .stMarkdown span, h1, h2, h3 {
            color: #1E3A8A !important;
            font-family: "Cairo", sans-serif;
        }
        /* تخصيص الأزرار لتطابق اللون اللبني الهادئ */
        .stButton > button {
            background-color: #7DD3FC !important;
            color: #0F172A !important;
            font-weight: bold;
            border-radius: 6px;
            border: 1px solid #38BDF8;
        }
        .stButton > button:hover {
            background-color: #38BDF8 !important;
            color: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 🏥 الهيدر الرئيسي وعرض اللوجو المزامر من الـ GitHub
# =========================================================
col_header1, col_header2 = st.columns([1, 4])

with col_header1:
    # التحقق من وجود صورة اللوجو بجانب الكود في الجيت هب وعرضها تلقائياً
    if os.path.exists("logo.png"):
        st.image("logo.png", width=140)
    else:
        # عرض أيقونة طبية مؤقتة في حال عدم رفع الصورة بعد
        st.markdown("<h1 style='font-size: 80px; margin: 0;'>🏥</h1>", unsafe_allow_html=True)

with col_header2:
    st.markdown("""
        <div style='background-color: #E0F2FE; padding: 15px; border-radius: 10px; border-right: 6px solid #0284C7; margin-top: 10px;'>
            <h1 style='margin: 0; color: #0369A1 !important; font-size: 28px;'>مركز القاهرة لأمراض الكلى - Cairo Kidney Center</h1>
            <p style='margin: 5px 0 0 0; color: #075985 !important; font-weight: 500;'>المنظومة الطبية الذكية المتقدمة لإدارة الحجوزات وسجلات المرضى</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# تبويبات النظام الطبي الجديد
tab1, tab2 = st.tabs(["📝 بوابة حجز المواعيد والعيادات", "🖥️ لوحة الإدارة والسجلات الطبية للأطباء"])

# 📝 بوابة حجز المواعيد والعيادات (التبويب الأول)
with tab1:
    st.markdown("<h3 style='color: #0369A1 !important;'>📥 تسجيل مريض جديد وتحديد العيادة</h3>", unsafe_allow_html=True)
    
    with st.form("appointment_form", clear_on_submit=True):
        p_name = st.text_input("👤 اسم المريض بالكامل (Patient Name):")
        p_phone = st.text_input("📞 رقم الهاتف للتواصل (Phone Number):")
        doc_name = st.selectbox("🩺 الطبيب الاستشاري المعالج (Consultant Doctor):", [
            "أ.د. أحمد عبد الرحمن - استشاري أمراض وزرع الكلى",
            "أ.د. محمود الشافعي - استشاري غسيل الكلى والأوعية الدموية",
            "د. سارة عزمي - أخصائي أمراض الكلى ومتابعة وظائف الكلى"
        ])
        notes = st.text_area("📋 التاريخ المرضي أو ملاحظات الحجز (Clinical Notes):")
        
        submit_booking = st.form_submit_button("🚀 تأكيد الحجز وإصدار التذكرة الطبية")
        
        if submit_booking:
            if p_name.strip() and p_phone.strip():
                current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                
                app_payload = {
                    "id": int(st.session_state.next_id),
                    "patient_name": p_name,
                    "phone": p_phone,
                    "doctor_name": doc_name,
                    "notes": notes if notes.strip() else "لا توجد ملاحظات إضافية",
                    "created_at": current_time
                }
                
                if insert_appointment(app_payload):
                    st.session_state.appointments = load_appointments()
                    st.success(f"🎉 تم تسجيل الحجز بنجاح! رقم الملف الطبي للمريض هو: #{st.session_state.next_id}")
                    st.session_state.next_id += 1
                    st.rerun()
            else:
                st.error("❌ خطأ: يرجى كتابة اسم المريض ورقم الهاتف أولاً لإتمام الحجز السحابي!")

# 🖥️ لوحة الإدارة والسجلات الطبية للأطباء (التبويب الثاني)
with tab2:
    st.markdown("<h3 style='color: #0369A1 !important;'>🖥️ شاشة الأطباء ومتابعة حالات العيادات اليومية</h3>", unsafe_allow_html=True)
    admin_password = st.text_input("🔑 أدخل كلمة المرور الطبية للوصول للبيانات:", type="password")
    
    if admin_password == "1234":
        st.success("🔓 تم التصريح بالدخول للملفات الطبية الحساسة للمركز.")
        st.session_state.appointments = load_appointments()
        
        # عرض وتحميل التقارير الطبية بصيغة Excel منظم
        if st.session_state.appointments:
            st.markdown("### 📊 بيان وجدول الحجوزات الشامل للمركز")
            df_app = pd.DataFrame(st.session_state.appointments)
            df_display = df_app[["id", "patient_name", "phone", "doctor_name", "status", "notes", "created_at", "updated_at"]].copy()
            df_display.columns = ["رقم الملف الطبي", "اسم المريض", "رقم الهاتف", "الطبيب المعالج", "الحالة الحالية", "التشخيص/الملاحظات", "تاريخ الحجز", "آخر تحديث للفحص"]
            
            st.dataframe(df_display, use_container_width=True)
            
            # محرك استخراج Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name='سجل العيادات اليومي')
            
            st.download_button(
                label="📥 تحميل سجل كشف المرضى اليومي كملف Excel منظم",
                data=buffer.getvalue(),
                file_name=f"Cairo_Kidney_Center_Report_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.markdown("---")
            
            # تحديث حالات المرضى (تم الكشف / قيد الانتظار) من قبل الطبيب
            st.markdown("### 🩺 تحديث الملف الطبي للمريض ومتابعة الفحص:")
            app_ids = [int(a['id']) for a in st.session_state.appointments]
            
            with st.form("update_appointment_form"):
                selected_id = st.selectbox("اختر رقم الملف الطبي للمريض:", app_ids)
                new_status = st.selectbox("تحديث حالة الحالة الصحية إلى:", [
                    "Examined (تم توقيع الكشف الطبي) ✅",
                    "In Progress (داخل غرفة الفحص الآن) ⚙️",
                    "Cancelled (تم إلغاء الحجز) ❌"
                ])
                doctor_updates = st.text_input("العلاج الموصوف أو تحديث التشخيص:")
                submit_update = st.form_submit_button("🔄 ترحيل وتحديث السجل السحابي للمريض")
                
                if submit_update:
                    update_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    fields = {
                        "status": new_status,
                        "notes": doctor_updates if doctor_updates.strip() else "لم تتغير الملاحظات",
                        "updated_at": update_time
                    }
                    if update_appointment_in_db(selected_id, fields):
                        st.session_state.appointments = load_appointments()
                        st.success(f"🎉 تم تحديث السجل الطبي للملف #{selected_id} بنجاح سحابياً!")
                        st.rerun()
        else:
            st.info("ℹ️ لا توجد حجوزات أو مرضى مسجلين في قائمة الانتظار اليوم.")
