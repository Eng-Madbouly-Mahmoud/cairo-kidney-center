import streamlit as st
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
from supabase import create_client, Client
import pandas as pd
import os

# =========================================================
# ⚙️ 1. إعدادات الصفحة والتصميم الاحترافي (خطوط واضحة)
# =========================================================
st.set_page_config(
    page_title="مركز القاهرة لأمراض الكلى", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        :root { color-scheme: light !important; }
        .stApp { background-color: #F8FAFC; font-family: 'Segoe UI', "Cairo", sans-serif; direction: rtl; }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #E2E8F0;
            padding: 8px;
            border-radius: 14px;
            direction: rtl;
        }
        .stTabs [data-baseweb="tab"] {
            height: 55px;
            background-color: #FFFFFF;
            border-radius: 10px;
            font-size: 18px !important;
            font-weight: 800 !important;
            color: #1E293B !important;
            box-shadow: 0 3px 6px rgba(0,0,0,0.08);
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
            color: #FFFFFF !important;
        }
        
        h1, h2, h3, h4, label {
            font-family: "Cairo", sans-serif !important;
            text-align: right;
            font-weight: 800 !important;
        }
        
        h2 { font-size: 24px !important; color: #0C4A6E !important; }
        h3 { font-size: 22px !important; color: #1E293B !important; }
        
        .stTextInput label, .stSelectbox label, .stTextArea label {
            font-size: 17px !important;
            font-weight: bold !important;
            color: #0F172A !important;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
            color: #FFFFFF !important;
            font-size: 17px !important;
            font-weight: bold !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 12px 24px;
            width: 100%;
        }

        .metric-card {
            background: #FFFFFF;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            text-align: center;
            border-top: 5px solid #0284C7;
        }

        .it-ticket-card {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            border-right: 6px solid #0284C7;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            text-align: right;
        }
        .ticket-badge {
            background: #E0F2FE;
            color: #0369A1;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 🔑 2. الربط بقاعدة بيانات Supabase
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

# =========================================================
# 🏥 الهيدر الرئيسي للمستشفى (اللوجو الصحيح)
# =========================================================
col_logo, col_banner = st.columns([1, 4])
with col_logo:
    possible_logos = ["logo.jpg", "لوجو.jpg", "logo_2.jpg", "لوجو_2.jpg", "logo.png", "لوجو.png"]
    found_logo = next((f for f in possible_logos if os.path.exists(f)), None)
    
    if found_logo:
        st.image(found_logo, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 50px;'>🩺</h1>", unsafe_allow_html=True)

with col_banner:
    st.markdown("""
        <div style='background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%); padding: 22px; border-radius: 14px; border-right: 10px solid #0369A1; text-align: right;'>
            <h1 style='margin: 0; color: #0C4A6E !important; font-size: 28px;'>مركز القاهرة لأمراض الكلى</h1>
            <p style='margin: 8px 0 0 0; color: #0369A1 !important; font-size: 16px; font-weight: bold;'>نظام إدارة الدعم الفني وتكنولوجيا المعلومات (IT Helpdesk)</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# التبويبات الرئيسية
tab_it, tab_records, tab_booking = st.tabs([
    "⚙️ قسم تكنولوجيا المعلومات والدعم الفني",
    "🩺 عيادة الأطباء والسجلات السحابية",
    "📝 حجز مواعيد الفحص والعيادات"
])

# =========================================================
# 1️⃣ تبويب الدعم الفني (IT Helpdesk)
# =========================================================
with tab_it:
    tickets_list = load_it_tickets()
    
    # تصنيف دقيق ومرن للبلاغات بناءً على قيمة status في قاعدة البيانات
    open_tickets = [t for t in tickets_list if str(t.get("status", "Open")).strip().lower() in ["open", "pending", "قيد الانتظار", "active", ""]]
    closed_tickets = [t for t in tickets_list if str(t.get("status", "")).strip().lower() in ["closed", "done", "تم الحل", "completed"]]

    # نموذج تسجيل بلاغ جديد
    st.markdown("### 📢 تسجيل بلاغ عطل أو مشكلة تقنية جديدة")
    with st.form("it_ticket_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            reporter = st.text_input("👤 اسم المُبلّغ / الطبيب / الموظف:")
        with c2:
            dept = st.selectbox("🏥 القسم أو الوحدة:", [
                "وحدة الغسيل الكلوي (الدور الأول)", 
                "وحدة الغسيل الكلوي (الدور الثاني)", 
                "عيادة الكلى التخصصية", 
                "الاستقبال والطوارئ", 
                "المعمل وتحاليل الدم", 
                "قسم الأشعة", 
                "الصيدلية", 
                "الإدارة والحسابات"
            ])
        with c3:
            device = st.selectbox("💻 تصنيف الجهاز أو النظام:", [
                "جهاز كمبيوتر مكتبي (PC)", 
                "محطة عمل الغسيل الكلوي", 
                "طابعة مستندات / باركود", 
                "شبكة الإنترنت / الواي فاي", 
                "شاشة العرض الطبية", 
                "برنامج السيستم / السجلات الطبية", 
                "أجهزة أخرى"
            ])
            
        issue = st.text_area("📋 تفاصيل المشكلة أو العطل بدقة:")
        submit_btn = st.form_submit_button("🚀 إرسال البلاغ الفوري لقسم الـ IT")
        
        if submit_btn:
            if reporter and issue:
                ticket_data = {
                    "reporter": reporter,
                    "dept": dept,
                    "device": device,
                    "issue": issue,
                    "status": "Open"
                }
                if insert_it_ticket(ticket_data):
                    st.success("✅ تم إرسال البلاغ بنجاح وجاري العمل عليه من قبل الفريق!")
                    st.rerun()
            else:
                st.warning("⚠️ يرجى إدخال اسم المُبلّغ وتفاصيل المشكلة.")

    st.markdown("---")
    
    # 🔐 لوحة التحكم الخاصة بالمهندسين
    st.markdown("### 🛠️ بوابة تحكم مهندسي الـ IT (متابعة وإغلاق البلاغات)")
    
    admin_pass = st.text_input("🔒 أدخل رمز الأمان السري الخاص بالمهندسين للتحكم:", type="password", placeholder="أدخل الباسورد هنا...")
    
    if admin_pass == "2026":
        st.success("🔓 تم تسجيل الدخول بنجاح لصلاحيات مهندسي الدعم الفني.")
        
        # إحصائيات سريعة (KPIs)
        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown(f"""<div class="metric-card"><h4>📥 البلاغات المفتوحة</h4><h2 style="color: #0284C7; margin:0; font-size: 28px;">{len(open_tickets)}</h2></div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""<div class="metric-card"><h4>✅ البلاغات المنجزة</h4><h2 style="color: #10B981; margin:0; font-size: 28px;">{len(closed_tickets)}</h2></div>""", unsafe_allow_html=True)
        with k3:
            st.markdown(f"""<div class="metric-card"><h4>📊 إجمالي البلاغات</h4><h2 style="color: #475569; margin:0; font-size: 28px;">{len(tickets_list)}</h2></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        sub_tab1, sub_tab2, sub_tab3 = st.tabs([
            f"📥 البلاغات المفتوحة ({len(open_tickets)})", 
            f"✅ سجل البلاغات المنجزة ({len(closed_tickets)})",
            f"📋 جدول جميع الأعطال ({len(tickets_list)})"
        ])

        with sub_tab1:
            if not open_tickets:
                st.success("🎉 ممتاز! لا توجد أي أعطال مفتوحة حالياً، جميع الأجهزة تعمل بكفاءة.")
            else:
                selected_engineer = st.selectbox("👷 اختر اسم مهندس الدعم الفني القائم بالحل:", ["م/ مدبولي محمود", "م/ مارسيلينو مجدي"])
                st.markdown("<br>", unsafe_allow_html=True)
                
                for t in open_tickets:
                    ticket_id = t.get('id')
                    ticket_dept = t.get('dept') or 'عام'
                    ticket_device = t.get('device') or 'جهاز'
                    ticket_issue = t.get('issue') or t.get('issue_desc') or 'لا توجد تفاصيل'
                    ticket_reporter = t.get('reporter')
                    ticket_time = str(t.get('created_at', ''))[:16]
                    
                    st.markdown(f"""
                        <div class="it-ticket-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                <h4 style="margin: 0; color: #0284C7; font-size: 18px;">🎫 تذكرة رقم #{ticket_id} - {ticket_device}</h4>
                                <span class="ticket-badge">القسم: {ticket_dept}</span>
                            </div>
                            <p style="margin: 12px 0 6px 0; color: #334155; font-size: 15px;"><strong>👤 المُبلّغ:</strong> {ticket_reporter}</p>
                            <p style="margin: 0 0 10px 0; color: #475569; font-size: 15px;"><strong>📋 تفاصيل العطل:</strong> {ticket_issue}</p>
                            <p style="margin: 0; color: #94A3B8; font-size: 13px;"><strong>🕒 وقت البلاغ:</strong> {ticket_time}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"✔️ إغلاق التذكرة #{ticket_id} بواسطة ({selected_engineer})", key=f"close_btn_{ticket_id}"):
                        if close_it_ticket_in_db(ticket_id, selected_engineer):
                            st.success(f"تم إغلاق التذكرة #{ticket_id} بنجاح بواسطة المهندس ({selected_engineer})!")
                            st.rerun()
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
                        "القسم": t.get("dept"),
                        "الجهاز / النظام": t.get("device"),
                        "تفاصيل العطل": t.get("issue") or t.get("issue_desc"),
                        "المهندس المعالج": t.get("closed_by") or "غير محدد",
                        "وقت الإغلاق": str(t.get("closed_at", ""))[:16]
                    })
                df_closed = pd.DataFrame(formatted_closed)
                st.dataframe(df_closed, use_container_width=True)

                csv_data = df_closed.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 تحميل تقرير الصيانة والبلاغات المنجزة (CSV)",
                    data=csv_data,
                    file_name=f"IT_Maintenance_Report_{datetime.now().strftime('%Y-%m-%d')}.csv",
                    mime="text/csv"
                )

        with sub_tab3:
            st.markdown("### 📊 عرض كافة الأعطال والبلاغات (السجل الشامل)")
            if tickets_list:
                formatted_all = []
                for t in tickets_list:
                    formatted_all.append({
                        "رقم البلاغ": t.get("id"),
                        "المُبلّغ": t.get("reporter"),
                        "القسم": t.get("dept"),
                        "الجهاز / النظام": t.get("device"),
                        "تفاصيل العطل": t.get("issue") or t.get("issue_desc"),
                        "الحالة": "مفتوحة 📥" if str(t.get("status", "Open")).strip().lower() in ["open", "pending", ""] else "منجزة ✅",
                        "المهندس المعالج": t.get("closed_by") or "قيد الانتظار",
                        "وقت البلاغ": str(t.get("created_at", ""))[:16]
                    })
                df_all = pd.DataFrame(formatted_all)
                st.dataframe(df_all, use_container_width=True)
                
                csv_all = df_all.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 تحميل تقرير شامل لجميع الأعطال (CSV)",
                    data=csv_all,
                    file_name=f"All_IT_Tickets_{datetime.now().strftime('%Y-%m-%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("لا توجد أي بلاغات مسجلة في قاعدة البيانات حتى الآن.")

    elif admin_pass != "":
        st.error("❌ رمز الأمان غير صحيح. يرجى إدخال الباسورد المخصص لمهندسي الدعم الفني.")
    else:
        st.info("🔒 لوحة تحكم المهندسين محمية. يرجى إدخال رمز الأمان بالأعلى لعرض التذاكر وإدارتها.")

# =========================================================
# 2️⃣ تبويب سجلات المرضى والعيادات
# =========================================================
with tab_records:
    st.markdown("### 📋 سجلات المرضى والمواعيد المسجلة بالسحابة")
    apps = load_appointments()
    if apps:
        df_apps = pd.DataFrame(apps)[["id", "patient_name", "phone", "clinic_type", "notes", "created_at"]]
        df_apps.columns = ["رقم الملف", "اسم المريض", "رقم الهاتف", "العيادة / الخدمة", "ملاحظات طبية", "تاريخ التسجيل"]
        st.dataframe(df_apps, use_container_width=True)
        
        csv_apps = df_apps.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل سجلات المرضى والمواعيد (CSV)",
            data=csv_apps,
            file_name=f"Patients_Appointments_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )
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
                    st.rerun()
            else:
                st.warning("⚠️ يرجى إدخال اسم المريض ورقم الهاتف.")
