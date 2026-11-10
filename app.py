import streamlit as st
from datetime import datetime
import pandas as pd
from supabase import create_client, Client
from supabase.client import ClientOptions
import os

# =========================================================
# ⚙️ 1. إعدادات الصفحة والتصميم الاحترافي الفاخر
# =========================================================
st.set_page_config(
    page_title="الدكتور صلاح حسب الله - مركز الدعم الفني - شركة إتقان",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        :root { color-scheme: light !important; }
        .stApp { background-color: #F8FAFC; font-family: 'Cairo', sans-serif; direction: rtl; }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: #E2E8F0;
            padding: 8px;
            border-radius: 14px;
            direction: rtl;
        }
        .stTabs [data-baseweb="tab"] {
            height: 55px;
            background-color: #FFFFFF;
            border-radius: 10px;
            font-size: 16px !important;
            font-weight: 800 !important;
            color: #334155 !important;
            box-shadow: 0 3px 6px rgba(0,0,0,0.06);
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #8C6239 0%, #634323 100%) !important;
            color: #FFFFFF !important;
        }
        
        h1, h2, h3, h4, label {
            font-family: "Cairo", sans-serif !important;
            text-align: right;
            font-weight: 800 !important;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #8C6239 0%, #634323 100%) !important;
            color: #FFFFFF !important;
            font-size: 16px !important;
            font-weight: bold !important;
            border-radius: 10px !important;
            border: none !important;
            padding: 12px 24px;
            width: 100%;
        }

        .metric-card {
            background: #FFFFFF;
            padding: 20px;
            border-radius: 14px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.05);
            text-align: center;
            border-top: 5px solid #8C6239;
            margin-bottom: 10px;
        }

        .ticket-card-pro {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            border-right: 6px solid #8C6239;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            text-align: right;
        }
        .badge-pending { background: #FEF3C7; color: #D97706; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; }
        .badge-solved { background: #DCFCE7; color: #166534; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 🔒 إعدادات الاتصال وقاعدة البيانات سحابياً
# =========================================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(
        SUPABASE_URL, 
        SUPABASE_KEY,
        options=ClientOptions(
            postgrest_client_timeout=30,
            headers={"apiKey": SUPABASE_KEY}
        )
    )

supabase = get_supabase_client()

# =========================================================
# 📥 دالات التعامل مع جدول التذاكر
# =========================================================
def load_data():
    try:
        response = supabase.table("tickets").select("*").execute()
        if response.data:
            tickets = []
            for row in response.data:
                ticket = row.copy()
                ticket['ID'] = row.get('id', row.get('Id', ''))
                tickets.append(ticket)
            return tickets
        return []
    except Exception:
        return []

def insert_ticket(new_ticket):
    try:
        db_data = {
            "id": int(new_ticket["ID"]),
            "name": new_ticket["name"],
            "dept": new_ticket["dept"],
            "issue": new_ticket["issue"],
            "status": "Pending (قيد الانتظار)",
            "solved_by": "لم تُحل بعد ⏳",
            "created_at": new_ticket["created_at"],
            "updated_at": new_ticket["updated_at"]
        }
        supabase.table("tickets").insert(db_data).execute()
        return True
    except Exception:
        return False

def update_ticket_status_in_supabase(ticket_id, new_status, solved_by_user):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        db_data = {
            "status": new_status,
            "solved_by": solved_by_user,
            "updated_at": current_time
        }
        supabase.table("tickets").update(db_data).eq("id", int(ticket_id)).execute()
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء تحديث التذكرة: {e}")
        return False

# =========================================================
# 📥 دالات التعامل مع جدول الاشتراكات (subscriptions_devices)
# =========================================================
def load_subscriptions():
    cols_order = ["id", "الاشتراك", "النوع", "تاريخ_الاشتراك", "تاريخ_التجديد", "حالة_الاشتراك", "تاريخ_الانتهاء"]
    try:
        response = supabase.table("subscriptions_devices").select("*").order("id", desc=False).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df = df.fillna("")
            if "Id" in df.columns:
                df = df.rename(columns={"Id": "id"})
            existing_cols = [c for c in cols_order if c in df.columns]
            if len(existing_cols) > 1:
                return df[existing_cols]
            return df
        return pd.DataFrame(columns=cols_order)
    except Exception:
        return pd.DataFrame(columns=cols_order)

def save_edited_data_to_supabase(edited_df):
    try:
        response = supabase.table("subscriptions_devices").select("id").execute()
        old_ids = set([row['id'] for row in response.data]) if response.data else set()
        current_ids = set()
        
        for _, row in edited_df.iterrows():
            row_id = row.get("id")
            db_data = {
                "الاشتراك": str(row.get("الاشتراك", "")) if pd.notna(row.get("الاشتراك")) else "",
                "النوع": str(row.get("النوع", "")) if pd.notna(row.get("النوع")) else "",
                "تاريخ_الاشتراك": str(row.get("تاريخ_الاشتراك", "")) if pd.notna(row.get("تاريخ_الاشتراك")) else "",
                "تاريخ_التجديد": str(row.get("تاريخ_التجديد", "")) if pd.notna(row.get("تاريخ_التجديد")) else "",
                "حالة_الاشتراك": str(row.get("حالة_الاشتراك", "")) if pd.notna(row.get("حالة_الاشتراك")) else "",
                "تاريخ_الانتهاء": str(row.get("تاريخ_الانتهاء", "")) if pd.notna(row.get("تاريخ_الانتهاء")) else ""
            }
            
            if pd.notna(row_id) and str(row_id).strip() != "" and int(row_id) in old_ids:
                supabase.table("subscriptions_devices").update(db_data).eq("id", int(row_id)).execute()
                current_ids.add(int(row_id))
            else:
                if "id" in db_data: 
                    del db_data["id"]
                supabase.table("subscriptions_devices").insert(db_data).execute()
        
        deleted_ids = old_ids - current_ids
        for d_id in deleted_ids:
            if d_id is not None:
                supabase.table("subscriptions_devices").delete().eq("id", d_id).execute()
        return True
    except Exception as e:
        st.error(f"حدث خطأ أثناء حفظ التعديلات سحابياً: {e}")
        return False

def process_excel_upload(uploaded_file):
    try:
        excel_df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return

    required_cols = ["الاشتراك", "النوع", "تاريخ_الاشتراك", "تاريخ_التجديد", "حالة_الاشتراك", "تاريخ_الانتهاء"]
    missing_cols = [col for col in required_cols if col not in excel_df.columns]
    
    if missing_cols:
        st.error(f"❌ الملف المرفوع يفتقد إلى الأعمدة التالية: {missing_cols}")
        st.info("⚠️ يرجى التأكد من أن شيت الإكسيل يحتوي على نفس أسماء أعمدة الجدول السحابي.")
        return

    st.write("📊 معاينة البيانات المرفوعة:")
    st.dataframe(excel_df.head())
    
    if st.button("💾 تأكيد ورفع الملف إلى قاعدة البيانات السحابية", key="btn_confirm_excel"):
        if save_edited_data_to_supabase(excel_df):
            st.success("✅ تم رفع وتحديث شيت الإكسيل بنجاح في Supabase!")
            st.rerun()

# =========================================================
# ⚙️ تهيئة الجلسة
# =========================================================
if 'tickets' not in st.session_state:
    st.session_state.tickets = load_data()

if 'next_id' not in st.session_state:
    try:
        if st.session_state.tickets:
            ids = [int(t['ID']) for t in st.session_state.tickets if str(t.get('ID')).isdigit()]
            st.session_state.next_id = max(ids) + 1 if ids else 101
        else:
            st.session_state.next_id = 101
    except Exception:
        st.session_state.next_id = 101

# =========================================================
# 🖼️ الهيدر الرئيسي مع اللوجو (logo.jpg)
# =========================================================
col_logo, col_banner = st.columns([1, 4])

with col_logo:
    logo_filename = "logo.jpg"
    if os.path.exists(logo_filename):
        st.image(logo_filename, use_container_width=True)
    else:
        st.warning("⚠️ ملف اللوجو 'logo.jpg' غير موجود في مجلد المشروع.")

with col_banner:
    st.markdown("""
        <div style='background-color: #8C6239; padding: 25px; border-radius: 12px; margin-bottom: 5px;'>
            <h1 style='text-align: center; color: #F5EBE0; margin: 0; font-size: 30px; font-weight: bold;'>لوحة تكنولوجيا المعلومات والشبكات ⚙️</h1>
            <p style='text-align: center; color: #E3D5CA; margin: 5px 0 0 0; font-size: 14px;'>المكتب الذكي لإدارة ومتابعة البلاغات والبنية التحتية</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <div style='background-color: #D5BDAF; padding: 10px; border-radius: 8px; margin-bottom: 25px; text-align: center;'>
        <marquee direction='right' style='color: #4A3728; font-weight: bold; font-size: 16px; margin: 0;'>
            ⚖️ شركة إتقان للمحاماة والاستشارات القانونية ترحب بكم .. يرجى تسجيل بلاغات الأعطال بدقة لسرعة توجيه مهندس الـ IT إليكم فوراً 🛠️
        </marquee>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# 📑 التبويبات الرئيسية
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "📝 بوابة الموظفين والمستشارين (تسجيل عطل)", 
    "🖥️ لوحة الإدارة والتحكم المهنية (IT Admin)",
    "📊 جرد الاشتراكات والأسعار (Excel)"
])

# 1️⃣ التبويب الأول: تسجيل بلاغ جديد
with tab1:
    st.markdown("<h3 style='color: #8C6239;'>📥 تسجيل بلاغ عطل تقني جديد</h3>", unsafe_allow_html=True)
    with st.form("ticket_form", clear_on_submit=True):
        name = st.text_input("👤 اسم الموظف / المستشار بالكامل:")
        dept = st.selectbox("🏢 القسم / الإدارة التابع لها:", ["قسم الاداره العليا", "بنك مصر", "بنك الاهلي", "التجاري الدولي", "الادمن", "إدارة عامة", "أخرى"])
        issue = st.text_area("⚠️ وصف العطل أو المشكلة التقنية بالتفصيل:")
        submit = st.form_submit_button("🚀 إرسال التذكرة الفورية")
        
        if submit and name.strip() and issue.strip():
            current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            new_ticket = {
                "ID": int(st.session_state.next_id), 
                "name": name, 
                "dept": dept, 
                "issue": issue, 
                "status": "Pending (قيد الانتظار)", 
                "solved_by": "لم تُحل بعد ⏳", 
                "created_at": current_time, 
                "updated_at": "لم تُحدث بعد"
            }
            if insert_ticket(new_ticket):
                st.session_state.tickets = load_data()
                st.success(f"🎉 تم تسجيل بلاغك بنجاح! رقم التذكرة هو: #{st.session_state.next_id}")
                st.session_state.next_id += 1
                st.rerun()

# 2️⃣ التبويب الثاني: لوحة الإدارة والتحكم الاحترافية
with tab2:
    st.markdown("<h3 style='color: #8C6239;'>🔐 لوحة الإدارة والتحكم في التذاكر (خاص بمهندس الـ IT)</h3>", unsafe_allow_html=True)
    password = st.text_input("🔑 أدخل كلمة مرور الأدمن لفتح صلاحيات التعديل:", type="password", key="admin_pass")
    
    st.session_state.tickets = load_data()
    tickets_list = st.session_state.tickets
    
    # تصفية التذاكر باحترافية عالية
    pending_tickets = [t for t in tickets_list if "pending" in str(t.get("status", "")).lower() or "انتظار" in str(t.get("status", ""))]
    solved_tickets = [t for t in tickets_list if "solved" in str(t.get("status", "")).lower() or "closed" in str(t.get("status", "")).lower() or "تم" in str(t.get("status", ""))]

    # بطاقات مؤشرات الأداء الاحترافية (KPIs)
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""<div class="metric-card"><h4>⏳ قيد الانتظار (Pending)</h4><h2 style="color: #D97706; margin:0; font-size: 28px;">{len(pending_tickets)}</h2></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="metric-card"><h4>✅ المنجزة (Solved / Closed)</h4><h2 style="color: #166534; margin:0; font-size: 28px;">{len(solved_tickets)}</h2></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="metric-card"><h4>📊 إجمالي البلاغات</h4><h2 style="color: #8C6239; margin:0; font-size: 28px;">{len(tickets_list)}</h2></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # تبويبات فرعية داخل لوحة التحكم لعرض البلاغات بمرونة
    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        f"⏳ البلاغات قيد الانتظار ({len(pending_tickets)})", 
        f"✅ سجل البلاغات المنجزة ({len(solved_tickets)})", 
        f"📋 جدول جميع الأعطال ({len(tickets_list)})"
    ])

    with sub_tab1:
        if not pending_tickets:
            st.success("🎉 رائع! لا توجد أي بلاغات معلقة قيد الانتظار حالياً.")
        else:
            for t in pending_tickets:
                t_id = t.get('ID') or t.get('id')
                t_name = t.get('name')
                t_dept = t.get('dept')
                t_issue = t.get('issue')
                t_time = t.get('created_at')
                
                st.markdown(f"""
                    <div class="ticket-card-pro">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #8C6239;">🎫 تذكرة رقم #{t_id} - {t_dept}</h4>
                            <span class="badge-pending">⏳ قيد الانتظار</span>
                        </div>
                        <p style="margin: 10px 0 5px 0; color: #1E293B;"><strong>👤 المُبلّغ:</strong> {t_name}</p>
                        <p style="margin: 0 0 5px 0; color: #475569;"><strong>⚠️ وصف العطل:</strong> {t_issue}</p>
                        <p style="margin: 0; color: #94A3B8; font-size: 12px;"><strong>🕒 وقت الإرسال:</strong> {t_time}</p>
                    </div>
                """, unsafe_allow_html=True)

    with sub_tab2:
        if not solved_tickets:
            st.info("💡 لا توجد تذاكر منجزة حتى الآن.")
        else:
            for t in solved_tickets:
                t_id = t.get('ID') or t.get('id')
                t_name = t.get('name')
                t_dept = t.get('dept')
                t_issue = t.get('issue')
                t_status = t.get('status')
                t_solver = t.get('solved_by')
                t_update = t.get('updated_at')
                
                st.markdown(f"""
                    <div class="ticket-card-pro" style="border-right-color: #166534;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #166534;">🎫 تذكرة رقم #{t_id} - {t_dept}</h4>
                            <span class="badge-solved">✅ {t_status}</span>
                        </div>
                        <p style="margin: 10px 0 5px 0; color: #1E293B;"><strong>👤 المُبلّغ:</strong> {t_name}</p>
                        <p style="margin: 0 0 5px 0; color: #475569;"><strong>⚠️ وصف العطل:</strong> {t_issue}</p>
                        <p style="margin: 0 0 5px 0; color: #047857;"><strong>🛠️ تم الحل بواسطة:</strong> {t_solver} | <strong>🕒 وقت المعالجة:</strong> {t_update}</p>
                    </div>
                """, unsafe_allow_html=True)

    with sub_tab3:
        if tickets_list:
            st.dataframe(pd.DataFrame(tickets_list), use_container_width=True)
        else:
            st.info("💡 لا توجد تذاكر مسجلة.")

    # منطقة صلاحيات الأدمن والتحديث
    if password == "1234":
        st.success("🔓 تم التحقق بنجاح! صلاحيات تحديث حالة التذاكر مفعّلة.")
        st.markdown("---")
        st.markdown("<h4 style='color: #8C6239;'>🛠️ لوحة عمليات وإغلاق التذاكر:</h4>", unsafe_allow_html=True)
        
        if tickets_list:
            ticket_ids = [t['ID'] for t in tickets_list]
            selected_ticket_id = st.selectbox("اختر رقم التذكرة لتحديث حالتها:", ticket_ids)
            
            new_status = st.selectbox("الحالة الجديدة:", ["Pending (قيد الانتظار)", "Solved (تم حل المشكلة)", "Closed (مغلقة نهائياً)"])
            solved_by_input = st.text_input("اسم المهندس المسؤول:", value="مدبولي محمود")
            
            if st.button("💾 حفظ وتحديث حالة التذكرة سحابياً"):
                if update_ticket_status_in_supabase(selected_ticket_id, new_status, solved_by_input):
                    st.success(f"✅ تم تحديث التذكرة #{selected_ticket_id} بنجاح وحفظها في قاعدة البيانات!")
                    st.rerun()
    elif password != "":
        st.error("❌ كلمة المرور غير صحيحة. يمكنك الاستعراض فقط في وضع القراءة.")

# 3️⃣ التبويب الثالث: جرد الاشتراكات والأسعار (رفع ملفات Excel)
with tab3:
    st.markdown("<h3 style='color: #8C6239;'>📊 جرد ومتابعة الاشتراكات والأسعار والأجهزة</h3>", unsafe_allow_html=True)
    subscriptions_df = load_subscriptions()

    if not subscriptions_df.empty:
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.metric("📦 إجمالي البنود المسجلة", len(subscriptions_df))
        with col_kpi2:
            active_count = len(subscriptions_df[subscriptions_df["حالة_الاشتراك"].str.contains("ساري|مفعل|نشط|ضروري", case=False, na=False)])
            st.metric("🟢 الاشتراكات الفعالة", active_count)
        with col_kpi3:
            inactive_count = len(subscriptions_df) - active_count
            st.metric("⚪ البنود الأخرى", inactive_count)
        st.markdown("---")

    st.markdown("#### 📋 جدول الاشتراكات والأسعار الحالي:")
    if not subscriptions_df.empty:
        st.dataframe(subscriptions_df, use_container_width=True)
    else:
        st.info("💡 لا توجد بيانات مسجلة حالياً في جدول الاشتراكات.")

    st.markdown("---")
    st.markdown("#### 📁 تحديث أو استبدال البيانات عبر ملف Excel:")
    uploaded_excel = st.file_uploader(
        "اختر ملف Excel (.xlsx) يحتوي على الأعمدة المطابقة للجدول:",
        type=["xlsx"],
        key="excel_uploader_subscriptions"
    )

    if uploaded_excel is not None:
        process_excel_upload(uploaded_excel)
