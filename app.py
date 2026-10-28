# 1. استيراد المكتبات وإعداد منصة أثر
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="ATHAR | أثر",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. قراءة بيانات أثر النهائية
BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "data" / "ATHAR_AI_Clusters.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

try:
    df = load_data()
except Exception as e:
    st.error(f"تعذر تحميل البيانات: {e}")
    st.stop()

# 3. التحقق من الأعمدة والمنهجية
required = [
    "مناطق المملكة",
    "نسبة الجهات %",
    "نسبة المستفيدين %",
    "فجوة التوزيع"
]

missing = [c for c in required if c not in df.columns]
if missing:
    st.error("أعمدة مفقودة: " + ", ".join(missing))
    st.stop()

for c in required[1:]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

if df[required].isna().any().any():
    st.error("توجد قيم مفقودة أو غير رقمية في البيانات.")
    st.stop()

if len(df) != 13 or df["مناطق المملكة"].duplicated().any():
    st.error("يجب أن تحتوي البيانات على 13 منطقة فريدة.")
    st.stop()

calculated_gap = (
    df["نسبة المستفيدين %"] - df["نسبة الجهات %"]
)

if not np.allclose(
    df["فجوة التوزيع"], calculated_gap, atol=0.02
):
    st.error("فجوة التوزيع لا تطابق المنهجية المعتمدة.")
    st.stop()

# 4. اعتماد تصنيف الأولويات الجديد
df["القيمة المطلقة للفجوة"] = df["فجوة التوزيع"].abs()

df["الأولوية"] = np.select(
    [
        df["القيمة المطلقة للفجوة"] > 3,
        df["القيمة المطلقة للفجوة"] > 1
    ],
    ["مرتفعة", "متوسطة"],
    default="منخفضة"
)

counts = df["الأولوية"].value_counts()

if (
    counts.get("مرتفعة", 0) != 3
    or counts.get("متوسطة", 0) != 5
    or counts.get("منخفضة", 0) != 5
):
    st.error("تصنيفات الأولوية لا تطابق النتائج النهائية.")
    st.stop()

# 5. إعداد اللغات والألوان
with st.sidebar:
    st.title("✦ ATHAR | أثر")
    language = st.radio(
        "Language / اللغة",
        ["العربية", "English"]
    )

ar = language == "العربية"

def tr(arabic, english):
    return arabic if ar else english

priority_en = {
    "مرتفعة": "High",
    "متوسطة": "Medium",
    "منخفضة": "Low"
}

colors = {
    "مرتفعة": "#F87171",
    "متوسطة": "#FBBF24",
    "منخفضة": "#2DD4BF"
}

# 6. تصميم واجهة المنصة
st.markdown("""
<style>
.stApp {
    background: linear-gradient(125deg, #071426, #102b43);
    color: #EAF4FA;
}
[data-testid="stSidebar"] {
    background: #0B1B30;
}
[data-testid="stMetric"] {
    background: #14334b;
    border: 1px solid #2a536a;
    border-radius: 16px;
    padding: 16px;
}
[data-testid="stMetricValue"] {
    color: #48e3ce;
}
h1, h2, h3 {
    color: #f1f8ff !important;
}
</style>
""", unsafe_allow_html=True)

# 7. أقسام المنصة
pages = {
    "home": tr("الرئيسية", "Home"),
    "geo": tr("التحليل الجغرافي", "Regional Analysis"),
    "priority": tr("أولويات المناطق", "Regional Priorities"),
    "compare": tr("مقارنة المناطق", "Compare Regions"),
    "ai": tr("التحليل الذكي", "AI Analysis"),
    "assistant": tr("مساعد أثر", "ATHAR Assistant"),
    "recommendations": tr("التوصيات", "Recommendations")
}

with st.sidebar:
    page = st.radio(
        tr("التنقل", "Navigation"),
        list(pages),
        format_func=lambda x: pages[x]
    )
    st.divider()
    st.caption("ATHAR © 2026")
    st.caption("By Yasser Al-Sahli")

st.title(tr(
    "✦ أثر | منصة دعم القرار",
    "✦ ATHAR | Decision Support Platform"
))

st.caption(tr(
    "تحليل التوازن الجغرافي بين الجهات والمستفيدين من ذوي الإعاقة في المملكة العربية السعودية",
    "Regional distribution analysis of nonprofit organizations and beneficiaries with disabilities in Saudi Arabia"
))

st.divider()

# 8. دوال الرسوم والتوصيات
def distribution_chart(data):
    plot_df = data.melt(
        id_vars="مناطق المملكة",
        value_vars=[
            "نسبة الجهات %",
            "نسبة المستفيدين %"
        ],
        var_name="المؤشر",
        value_name="النسبة"
    )

    fig = px.bar(
        plot_df,
        x="مناطق المملكة",
        y="النسبة",
        color="المؤشر",
        barmode="group",
        title=tr(
            "توزيع الجهات والمستفيدين",
            "Distribution of Organizations and Beneficiaries"
        ),
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)


def gap_chart(data):
    ordered = data.sort_values("فجوة التوزيع")
    fig = px.bar(
        ordered,
        x="فجوة التوزيع",
        y="مناطق المملكة",
        color="الأولوية",
        color_discrete_map=colors,
        orientation="h",
        title=tr(
            "فجوة التوزيع بالنقاط المئوية",
            "Distribution Gap in Percentage Points"
        ),
        template="plotly_dark"
    )
    fig.add_vline(x=0, line_color="white")
    st.plotly_chart(fig, use_container_width=True)


def advice(row):
    gap = row["فجوة التوزيع"]
    level = row["الأولوية"]

    if level == "مرتفعة":
        if gap > 0:
            return tr(
                "دراسة مدى كفاية التغطية والخدمات والشراكات في المنطقة، والتحقق من الاحتياج الفعلي قبل التوسع.",
                "Investigate service coverage, capacity and partnerships before considering expansion."
            )
        return tr(
            "مراجعة توزيع الجهات وتخصصاتها ومدى توافق خدماتها مع الاحتياج الفعلي.",
            "Review organization distribution, specialization and alignment with actual needs."
        )

    if level == "متوسطة":
        return tr(
            "إجراء مراجعة تفصيلية للمؤشرات ومتابعة التوازن الجغرافي.",
            "Conduct a detailed indicator review and monitor regional balance."
        )

    return tr(
        "المحافظة على المتابعة الدورية والتحقق من جودة البيانات.",
        "Maintain periodic monitoring and validate data quality."
    )


def show_table(data):
    columns = [
        "مناطق المملكة",
        "نسبة الجهات %",
        "نسبة المستفيدين %",
        "فجوة التوزيع",
        "الأولوية"
    ]
    st.dataframe(
        data[columns],
        use_container_width=True,
        hide_index=True
    )


# 9. الصفحة الرئيسية
if page == "home":
    st.header(tr("نظرة عامة", "Overview"))

    a, b, c, d = st.columns(4)
    a.metric(tr("المناطق", "Regions"), len(df))
    b.metric(tr("مرتفعة", "High"), counts.get("مرتفعة", 0))
    c.metric(tr("متوسطة", "Medium"), counts.get("متوسطة", 0))
    d.metric(tr("منخفضة", "Low"), counts.get("منخفضة", 0))

    st.info(tr(
        "الفجوة = نسبة المستفيدين − نسبة الجهات. تقاس بالنقاط المئوية، ويعتمد ترتيب الأولوية على القيمة المطلقة للفجوة.",
        "Gap = beneficiary share minus organization share, in percentage points. Priority is determined by the absolute gap."
    ))

    distribution_chart(df)
    gap_chart(df)

# 10. التحليل الجغرافي
elif page == "geo":
    st.header(pages[page])

    region = st.selectbox(
        tr("اختر المنطقة", "Select Region"),
        df["مناطق المملكة"].tolist()
    )
    row = df.loc[
        df["مناطق المملكة"] == region
    ].iloc[0]

    a, b, c = st.columns(3)
    a.metric(
        tr("نسبة الجهات", "Organizations Share"),
        f"{row['نسبة الجهات %']:.2f}%"
    )
    b.metric(
        tr("نسبة المستفيدين", "Beneficiaries Share"),
        f"{row['نسبة المستفيدين %']:.2f}%"
    )
    c.metric(
        tr("الفجوة", "Gap"),
        f"{row['فجوة التوزيع']:+.2f} pp"
    )

    st.subheader(tr("التفسير", "Interpretation"))
    st.write(advice(row))
    distribution_chart(df)

# 11. أولويات المناطق
elif page == "priority":
    st.header(pages[page])

    selected = st.multiselect(
        tr("مستوى الأولوية", "Priority Level"),
        ["مرتفعة", "متوسطة", "منخفضة"],
        default=["مرتفعة", "متوسطة", "منخفضة"]
    )

    filtered = df[df["الأولوية"].isin(selected)]
    filtered = filtered.sort_values(
        "القيمة المطلقة للفجوة",
        ascending=False
    )

    show_table(filtered)
    gap_chart(filtered)

    st.caption(tr(
        "مرتفعة: أكبر من 3 | متوسطة: أكبر من 1 إلى 3 | منخفضة: 1 أو أقل.",
        "High: >3 | Medium: >1 to 3 | Low: ≤1 percentage point."
    ))

# 12. مقارنة المناطق
elif page == "compare":
    st.header(pages[page])

    selected = st.multiselect(
        tr("اختر منطقتين", "Select Two Regions"),
        df["مناطق المملكة"].tolist(),
        max_selections=2
    )

    if len(selected) == 2:
        subset = df[
            df["مناطق المملكة"].isin(selected)
        ]
        show_table(subset)
        distribution_chart(subset)
        gap_chart(subset)
    else:
        st.info(tr(
            "اختر منطقتين للمقارنة.",
            "Select two regions to compare."
        ))

# 13. التحليل الذكي
elif page == "ai":
    st.header(pages[page])

    st.info(tr(
        "تعتمد الأولويات المعتمدة على فجوة التوزيع، وليس على التجميع الآلي.",
        "Approved priorities are based on distribution gaps, not clustering."
    ))

    cluster_columns = [
        c for c in df.columns
        if "cluster" in c.lower() or "مجموعة" in c
    ]

    if cluster_columns:
        cluster_col = cluster_columns[0]
        st.subheader(tr(
            "التجميع الاستكشافي",
            "Exploratory Clustering"
        ))
        st.dataframe(
            df[["مناطق المملكة", cluster_col]],
            use_container_width=True,
            hide_index=True
        )
        st.caption(tr(
            "هذه المجموعات وصفية ولا تحدد مستوى الأولوية. يلزم توثيق تقييم النموذج قبل اعتماد نتائجه.",
            "These clusters are descriptive and do not determine priority. Model validation is required."
        ))
    else:
        st.write(tr(
            "لا توجد نتائج تجميع محفوظة في البيانات الحالية.",
            "No clustering results are available in the current data."
        ))

# 14. مساعد أثر
elif page == "assistant":
    st.header(pages[page])

    questions = {
        "high": tr(
            "ما المناطق ذات الأولوية المرتفعة؟",
            "Which regions are high priority?"
        ),
        "positive": tr(
            "ما أعلى فجوة موجبة؟",
            "Which region has the highest positive gap?"
        ),
        "negative": tr(
            "ما أكبر فجوة سالبة؟",
            "Which region has the largest negative gap?"
        ),
        "method": tr(
            "كيف نحسب الأولويات؟",
            "How are priorities calculated?"
        )
    }

    question = st.selectbox(
        tr("اختر سؤالًا", "Choose a Question"),
        list(questions),
        format_func=lambda x: questions[x]
    )

    if question == "high":
        show_table(df[df["الأولوية"] == "مرتفعة"])
    elif question == "positive":
        row = df.loc[df["فجوة التوزيع"].idxmax()]
        st.write(
            f"{row['مناطق المملكة']}: "
            f"{row['فجوة التوزيع']:+.2f} pp"
        )
    elif question == "negative":
        row = df.loc[df["فجوة التوزيع"].idxmin()]
        st.write(
            f"{row['مناطق المملكة']}: "
            f"{row['فجوة التوزيع']:+.2f} pp"
        )
    else:
        st.write(tr(
            "نطرح نسبة الجهات من نسبة المستفيدين، ثم نستخدم القيمة المطلقة للفجوة لتحديد الأولوية.",
            "Subtract organization share from beneficiary share, then use the absolute gap to determine priority."
        ))

    st.caption(tr(
        "مساعد تحليلي يعتمد على إجابات محسوبة من البيانات.",
        "A rule-based analytical assistant using the dataset."
    ))

# 15. التوصيات الاستراتيجية
elif page == "recommendations":
    st.header(pages[page])

    region = st.selectbox(
        tr("اختر المنطقة", "Select Region"),
        df["مناطق المملكة"].tolist()
    )

    row = df.loc[
        df["مناطق المملكة"] == region
    ].iloc[0]

    st.metric(
        tr("فجوة التوزيع", "Distribution Gap"),
        f"{row['فجوة التوزيع']:+.2f} pp"
    )

    st.subheader(tr(
        "الإجراء المقترح",
        "Suggested Action"
    ))
    st.write(advice(row))

    st.subheader(tr(
        "البيانات المطلوبة قبل القرار",
        "Additional Evidence Needed"
    ))
    st.write(tr(
        "الطاقة الاستيعابية، مواقع الخدمات، تخصصات الجهات، أعداد المستفيدين الفريدين، قوائم الانتظار وسهولة الوصول.",
        "Service capacity, locations, specialization, unique beneficiaries, waiting lists and accessibility."
    ))

    st.warning(tr(
        "الفجوة النسبية مؤشر للمراجعة وليست دليلًا قاطعًا على نقص الخدمات أو وجود فائض.",
        "Relative gaps are screening indicators, not proof of service shortages or surpluses."
    ))

    recs = df.copy()
    recs["التوصية"] = recs.apply(advice, axis=1)
    st.dataframe(
        recs[[
            "مناطق المملكة",
            "فجوة التوزيع",
            "الأولوية",
            "التوصية"
        ]],
        use_container_width=True,
        hide_index=True
    )

# 16. توثيق المنهجية وتحميل البيانات
with st.expander(tr(
    "المنهجية والقيود",
    "Methodology and Limitations"
)):
    st.write(tr(
        "تُحسب الفجوة بطرح نسبة الجهات من نسبة المستفيدين. تستخدم القيمة المطلقة للفجوة لترتيب أولويات المراجعة، دون اعتبارها مقياسًا مباشرًا لكفاية الخدمات.",
        "The gap is beneficiary share minus organization share. Absolute gaps rank review priorities, without directly measuring service adequacy."
    ))
    st.write(tr(
        "تتطلب القرارات النهائية التحقق من جودة البيانات والتغطية الفعلية والخدمات المتاحة.",
        "Final decisions require validating data quality, actual coverage and available services."
    ))

csv = df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    tr("تحميل البيانات", "Download Data"),
    data=csv,
    file_name="ATHAR_Regional_Results.csv",
    mime="text/csv"
)

st.divider()
st.caption("ATHAR © 2026 | By Yasser Al-Sahli")
