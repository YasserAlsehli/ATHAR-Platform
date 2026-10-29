import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# 1. إعداد المنصة وتحميل البيانات
st.set_page_config(
    page_title="ATHAR | أثر",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE = Path(__file__).resolve().parent

@st.cache_data
def load_data():
    return pd.read_csv(BASE / "data" / "ATHAR_AI_Clusters.csv")

df = load_data()

required = [
    "مناطق المملكة",
    "نسبة الجهات %",
    "نسبة المستفيدين %",
    "فجوة التوزيع"
]

missing = [c for c in required if c not in df.columns]
if missing:
    st.error("Missing columns: " + ", ".join(missing))
    st.stop()

for c in required[1:]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

if (
    df[required].isna().any().any()
    or df["مناطق المملكة"].duplicated().any()
    or len(df) != 13
):
    st.error("Data quality validation failed.")
    st.stop()

# 2. التحقق من المنهجية الجديدة
calculated_gap = (
    df["نسبة المستفيدين %"] - df["نسبة الجهات %"]
)

if not np.allclose(
    df["فجوة التوزيع"],
    calculated_gap,
    atol=0.02
):
    st.error("Distribution gap does not match the approved method.")
    st.stop()

# 3. تصنيف الأولويات المعتمد
df["priority"] = np.select(
    [
        df["فجوة التوزيع"].abs() > 3,
        df["فجوة التوزيع"].abs() > 1
    ],
    ["high", "medium"],
    default="low"
)

counts = df["priority"].value_counts()

if (
    counts.get("high", 0) != 3
    or counts.get("medium", 0) != 5
    or counts.get("low", 0) != 5
):
    st.error("Priority results do not match the validated dataset.")
    st.stop()

# 4. أسماء المناطق
REGIONS = {
    "الرياض": "Riyadh",
    "مكة المكرمة": "Makkah",
    "المدينة المنورة": "Madinah",
    "الشرقية": "Eastern Province",
    "القصيم": "Qassim",
    "عسير": "Asir",
    "تبوك": "Tabuk",
    "حائل": "Hail",
    "الحدود الشمالية": "Northern Borders",
    "جازان": "Jazan",
    "نجران": "Najran",
    "الباحة": "Al Bahah",
    "الجوف": "Al Jawf"
}

# 5. نصوص المنصة بالعربية والإنجليزية
TEXT = {
    "ar": {
        "home": "الرئيسية",
        "geo": "التحليل الجغرافي",
        "priority": "أولويات المناطق",
        "compare": "مقارنة المناطق",
        "ml": "التحليل الذكي",
        "assistant": "مساعد أثر",
        "executive": "الملخص التنفيذي",
        "story": "قصة أثر",
        "recommendations": "التوصيات الاستراتيجية",
        "title": "أثر | منصة دعم القرار",
        "subtitle": "رؤى تحليلية لتوزيع الجهات والمستفيدين في مناطق المملكة",
        "regions": "المناطق السعودية",
        "high": "أولوية مرتفعة",
        "medium": "أولوية متوسطة",
        "low": "أولوية منخفضة",
        "entities": "نسبة الجهات",
        "beneficiaries": "نسبة المستفيدين",
        "gap": "فجوة التوزيع",
        "select": "اختر المنطقة",
        "chart": "توزيع الجهات والمستفيدين",
        "gapchart": "الفجوة حسب المنطقة (نقطة مئوية)",
        "compare_select": "اختر منطقتين",
        "download": "تنزيل البيانات المعروضة (CSV)",
        "method": "المنهجية والقيود",
        "ask": "اختر سؤالًا للمساعد",
        "q1": "ما المناطق ذات الأولوية المرتفعة؟",
        "q2": "ما أكبر فجوة سالبة؟",
        "q3": "ما أعلى فجوة موجبة؟",
        "q4": "ما نتائج التجميع الذكي؟",
        "q5": "ما حدود هذه المؤشرات؟",
        "note": (
            "الفجوة = نسبة المستفيدين − نسبة الجهات، "
            "بوحدة النقطة المئوية. مستوى الأولوية يعتمد "
            "على القيمة المطلقة للفجوة، ولا يثبت نقص الخدمات."
        ),
        "priority_rule": (
            "مرتفعة: |الفجوة| > 3، "
            "متوسطة: 1 < |الفجوة| ≤ 3، "
            "منخفضة: |الفجوة| ≤ 1."
        ),
        "ai_note": (
            "K-Means تحليل استكشافي مستقل عن تصنيف الأولويات. "
            "المجموعات الإحصائية لا تقيس الاحتياج أو جودة الخدمات."
        ),
        "info": "راجع المصادر والتوثيق قبل اتخاذ أي قرار.",
        "no_cluster": "عمود المجموعات غير متوفر.",
        "not_chat": (
            "مساعد تحليلي يعتمد على نتائج البيانات "
            "والمنهجية المعتمدة، وليس نموذجًا لغويًا عامًا."
        )
    },
    "en": {
        "home": "Home",
        "geo": "Regional Analysis",
        "priority": "Regional Priorities",
        "compare": "Compare Regions",
        "ml": "AI Analysis",
        "assistant": "ATHAR Assistant",
        "executive": "Executive Summary",
        "story": "ATHAR Story",
        "recommendations": "Strategic Recommendations",
        "title": "ATHAR | Decision Intelligence",
        "subtitle": "Regional insights into organizations and beneficiaries in Saudi Arabia",
        "regions": "Saudi Regions",
        "high": "High Priority",
        "medium": "Medium Priority",
        "low": "Low Priority",
        "entities": "Organizations Share",
        "beneficiaries": "Beneficiaries Share",
        "gap": "Distribution Gap",
        "select": "Select Region",
        "chart": "Organizations and Beneficiaries Distribution",
        "gapchart": "Regional Gap (percentage points)",
        "compare_select": "Select two regions",
        "download": "Download displayed data (CSV)",
        "method": "Methodology & Limitations",
        "ask": "Choose a question",
        "q1": "Which regions are high priority?",
        "q2": "Which region has the largest negative gap?",
        "q3": "Which region has the largest positive gap?",
        "q4": "What are the clustering results?",
        "q5": "What are the limitations?",
        "note": (
            "Gap = beneficiary share minus organization share, "
            "in percentage points. Priority uses the absolute gap "
            "and does not establish unmet service needs."
        ),
        "priority_rule": (
            "High: |gap| > 3; "
            "Medium: 1 < |gap| ≤ 3; "
            "Low: |gap| ≤ 1."
        ),
        "ai_note": (
            "K-Means is exploratory and independent of priority levels. "
            "Clusters do not measure needs or service quality."
        ),
        "info": "Review sources and documentation before making decisions.",
        "no_cluster": "Cluster assignment column is unavailable.",
        "not_chat": (
            "A data-driven analytical assistant, "
            "not a general-purpose language model."
        )
    }
}

# 6. اللغة والقائمة الجانبية
with st.sidebar:
    st.markdown("## ✦ ATHAR | أثر")
    language = st.radio(
        "Language / اللغة",
        ["العربية", "English"],
        horizontal=True
    )

lang = "ar" if language == "العربية" else "en"
rtl = lang == "ar"
t = TEXT[lang]

def normalize_region(value):
    import re
    name = re.sub(r"[ـ\u064b-\u065f]", "", str(value)).strip()
    name = re.sub(r"^المنطقة\s+", "", name)
    name = re.sub(r"^منطقة\s+", "", name)
    return name

df["region_ar"] = df["مناطق المملكة"].map(normalize_region)
df["region"] = df["region_ar"].map(
    lambda s: s if rtl else REGIONS.get(s, s)
)

priority_labels = {
    "high": t["high"],
    "medium": t["medium"],
    "low": t["low"]
}
df["priority_label"] = df["priority"].map(priority_labels)

COLORS = {
    "high": "#F87171",
    "medium": "#FBBF24",
    "low": "#2DD4BF"
}

# 7. التصميم الأصلي للمنصة
st.markdown("""
<style>
.stApp {
    background: linear-gradient(125deg,#071426,#102b43);
    color: #EAF4FA;
}
[data-testid="stSidebar"] {
    background: #0B1B30;
}
[data-testid="stMetric"] {
    background: #14334b;
    border: 1px solid #2a536a;
    border-radius: 16px;
    padding: 18px;
}
[data-testid="stMetricValue"] {
    color: #48e3ce;
}
h1,h2,h3 {
    color: #f1f8ff !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    pages = [
        "home",
        "geo",
        "priority",
        "compare",
        "ml",
        "assistant",
        "executive",
        "story",
        "recommendations"
    ]
    page = st.radio(
        "Navigation / التنقل",
        pages,
        format_func=lambda x: t[x]
    )
    st.divider()
    st.caption("ATHAR © 2026")
    st.caption("By: Yasser Alsahli")

st.markdown(
    f'<div dir="{"rtl" if rtl else "ltr"}" '
    f'style="text-align:{"right" if rtl else "left"}">'
    f'<h1>✦ {t["title"]}</h1><p>{t["subtitle"]}</p></div>',
    unsafe_allow_html=True
)
st.divider()

# 8. الرسوم البيانية الأصلية
def bars(frame):
    data = frame.sort_values("نسبة المستفيدين %")
    fig = go.Figure()

    for field, label, color in [
        ("نسبة الجهات %", t["entities"], "#38BDF8"),
        ("نسبة المستفيدين %", t["beneficiaries"], "#2DD4BF")
    ]:
        fig.add_trace(go.Bar(
            y=data["region"],
            x=data[field],
            name=label,
            orientation="h",
            marker_color=color,
            hovertemplate="%{y}: %{x:.2f}%<extra></extra>"
        ))

    fig.update_layout(
        barmode="group",
        height=max(440, 36 * len(data) + 160),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="%",
        yaxis_title="",
        margin=dict(l=10, r=10, t=40, b=20),
        legend=dict(orientation="h", y=1.12)
    )
    st.plotly_chart(fig, use_container_width=True)

def gap_chart(frame):
    data = frame.sort_values("فجوة التوزيع")
    fig = go.Figure(go.Bar(
        y=data["region"],
        x=data["فجوة التوزيع"],
        orientation="h",
        marker_color=[COLORS[x] for x in data["priority"]],
        hovertemplate="%{y}: %{x:+.2f} pp<extra></extra>"
    ))

    fig.update_layout(
        height=max(440, 36 * len(data) + 160),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title=t["gap"] + " (pp)",
        yaxis_title="",
        margin=dict(l=10, r=10, t=20, b=20)
    )
    fig.add_vline(x=0, line_color="#DDE7EF")
    st.plotly_chart(fig, use_container_width=True)

# 9. الجداول والتصدير
def table(frame):
    display = frame[
        [
            "region",
            "نسبة الجهات %",
            "نسبة المستفيدين %",
            "فجوة التوزيع",
            "priority_label"
        ]
    ].copy()

    display.columns = [
        t["regions"],
        t["entities"] + " (%)",
        t["beneficiaries"] + " (%)",
        t["gap"] + " (pp)",
        t["priority"]
    ]

    for c in display.columns[1:4]:
        display[c] = display[c].round(2)

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )
    st.download_button(
        t["download"],
        display.to_csv(index=False).encode("utf-8-sig"),
        file_name="ATHAR_Regional_View.csv",
        mime="text/csv"
    )

# 10. تفسير اتجاه الفجوة
def interpret_gap(value):
    if value > 0:
        return (
            "حصة المستفيدين أعلى من حصة الجهات"
            if rtl else
            "Beneficiary share exceeds organization share"
        )
    if value < 0:
        return (
            "حصة الجهات أعلى من حصة المستفيدين"
            if rtl else
            "Organization share exceeds beneficiary share"
        )
    return (
        "الحصتان متساويتان"
        if rtl else
        "Both shares are equal"
    )

# 11. التوصيات وفق المنهجية الجديدة
def region_advice(row):
    gap = float(row["فجوة التوزيع"])
    level = row["priority"]

    if level == "high" and gap > 0:
        return (
            "أولوية مرتفعة لدراسة التغطية"
            if rtl else "High priority: assess coverage",
            "فجوة موجبة كبيرة؛ حصة المستفيدين أعلى نسبيًا."
            if rtl else "Large positive gap; beneficiary share is higher.",
            "التحقق من الطاقة الاستيعابية، ومواقع الخدمات، وقوائم الانتظار، ثم دراسة التوسع أو الشراكات إذا ثبت الاحتياج."
            if rtl else "Validate capacity, locations and waiting lists before considering expansion or partnerships."
        )

    if level == "high" and gap < 0:
        return (
            "أولوية مرتفعة لمراجعة توزيع الجهات"
            if rtl else "High priority: review organization distribution",
            "فجوة سالبة كبيرة؛ حصة الجهات أعلى نسبيًا."
            if rtl else "Large negative gap; organization share is higher.",
            "فحص تخصصات الجهات وانتشارها واستفادتها الفعلية، دون افتراض وجود فائض في الخدمات."
            if rtl else "Review specialization, geographic coverage and utilization without assuming a service surplus."
        )

    if level == "medium" and gap > 0:
        return (
            "أولوية متوسطة لفحص الوصول للخدمات"
            if rtl else "Medium priority: assess accessibility",
            "فجوة موجبة متوسطة تستدعي مراجعة التغطية."
            if rtl else "Moderate positive gap warrants coverage review.",
            "دراسة سهولة الوصول والتغطية المحلية وتحديد ما إذا كانت هناك فجوات خدمية فعلية."
            if rtl else "Study accessibility and local coverage to establish whether service gaps exist."
        )

    if level == "medium" and gap < 0:
        return (
            "أولوية متوسطة لتحسين التنسيق"
            if rtl else "Medium priority: improve coordination",
            "فجوة سالبة متوسطة في الحصص النسبية."
            if rtl else "Moderate negative difference in relative shares.",
            "مراجعة التخصصات والشراكات والتوزيع داخل المنطقة ومدى ملاءمة الخدمات للمستفيدين."
            if rtl else "Review specialties, partnerships and within-region service distribution."
        )

    return (
        "أولوية منخفضة للمراجعة الدورية"
        if rtl else "Low priority: periodic review",
        "الفجوة النسبية محدودة وفق حدود المنهجية."
        if rtl else "The relative gap is small under the approved thresholds.",
        "الاستمرار في المتابعة وفحص التفاوتات داخل المنطقة وجودة الوصول دون افتراض اكتمال التغطية."
        if rtl else "Continue monitoring within-region differences and accessibility without assuming adequate coverage."
    )

# 12. شرح المنهجية والقيود
def explain_metrics():
    title = (
        "📖 كيف نقرأ المؤشرات؟"
        if rtl else "📖 How to read the indicators"
    )
    with st.expander(title):
        st.write(
            "**نسبة الجهات:** حصة المنطقة من إجمالي الجهات."
            if rtl else
            "**Organization share:** regional share of listed organizations."
        )
        st.write(
            "**نسبة المستفيدين:** حصة المنطقة من إجمالي المستفيدين."
            if rtl else
            "**Beneficiary share:** regional share of listed beneficiaries."
        )
        st.write(t["note"])
        st.write(t["priority_rule"])
        st.write(t["ai_note"])

def evidence_boundary():
    st.warning(
        "البيانات تكشف اختلاف الحصص النسبية، لكنها لا تثبت نقص الخدمات أو فائضها أو جودة التغطية."
        if rtl else
        "Relative shares do not establish shortages, surpluses or service quality."
    )

# 13. الصفحة الرئيسية
if page == "home":
    a, b, c, d = st.columns(4)
    a.metric(t["regions"], len(df))
    b.metric(t["high"], counts.get("high", 0))
    c.metric(t["medium"], counts.get("medium", 0))
    d.metric(t["low"], counts.get("low", 0))

    st.subheader(t["chart"])
    bars(df)
    st.info(t["note"])

# 14. التحليل الجغرافي
elif page == "geo":
    region = st.selectbox(t["select"], df["region"].tolist())
    selected = df.loc[df["region"] == region].iloc[0]

    a, b, c = st.columns(3)
    a.metric(t["entities"], f'{selected["نسبة الجهات %"]:.2f}%')
    b.metric(t["beneficiaries"], f'{selected["نسبة المستفيدين %"]:.2f}%')
    c.metric(t["gap"], f'{selected["فجوة التوزيع"]:+.2f} pp')

    st.write(
        f'**{selected["priority_label"]}** — '
        f'{interpret_gap(selected["فجوة التوزيع"])}'
    )

    st.subheader(t["gapchart"])
    gap_chart(df)
    st.info(t["note"])

# 15. أولويات المناطق
elif page == "priority":
    st.subheader(t["priority"])
    selected = st.selectbox(
        "Filter / تصفية",
        ["all", "high", "medium", "low"],
        format_func=lambda x: (
            "الكل" if rtl else "All"
        ) if x == "all" else priority_labels[x]
    )

    filtered = (
        df if selected == "all"
        else df.loc[df["priority"] == selected]
    )
    gap_chart(filtered)
    table(filtered)
    st.caption(t["priority_rule"])
    st.info(t["note"])

# 16. مقارنة المناطق
elif page == "compare":
    choices = st.multiselect(
        t["compare_select"],
        df["region"].tolist(),
        default=df["region"].tolist()[:2],
        max_selections=2
    )

    if len(choices) == 2:
        subset = df.loc[df["region"].isin(choices)]
        bars(subset)
        table(subset)
    else:
        st.info(t["compare_select"])

# 17. التحليل الذكي
elif page == "ml":
    st.subheader(t["ml"])
    st.info(t["ai_note"])

    cluster_col = next(
        (
            c for c in [
                "المجموعة النهائية",
                "المجموعة",
                "Cluster",
                "cluster"
            ] if c in df.columns
        ),
        None
    )

    if cluster_col:
        cluster_counts = (
            df.groupby(cluster_col)
            .size()
            .reset_index(name="count")
        )

        fig = px.bar(
            cluster_counts,
            x=cluster_col,
            y="count",
            text="count",
            template="plotly_dark",
            color_discrete_sequence=["#2DD4BF"]
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)

        display = df[
            ["region", cluster_col, "فجوة التوزيع", "priority_label"]
        ].copy()
        display["فجوة التوزيع"] = display["فجوة التوزيع"].round(2)
        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "التجميع الإحصائي مستقل عن الأولويات المعتمدة."
            if rtl else
            "Statistical clusters are separate from approved priority levels."
        )
    else:
        st.warning(t["no_cluster"])

# 18. مساعد أثر وفق المنهجية الجديدة
elif page == "assistant":
    st.subheader("✦ ATHAR AI")
    st.caption(t["not_chat"])

    questions = [t[f"q{i}"] for i in range(1, 6)]
    q = st.selectbox(t["ask"], questions)
    qnum = questions.index(q) + 1

    if qnum == 1:
        high = (
            df.loc[df["priority"] == "high"]
            .assign(abs_gap=lambda x: x["فجوة التوزيع"].abs())
            .sort_values("abs_gap", ascending=False)
        )
        for _, r in high.iterrows():
            st.write(
                f'**{r["region"]}** — '
                f'{r["فجوة التوزيع"]:+.2f} pp'
            )

    elif qnum in (2, 3):
        idx = (
            df["فجوة التوزيع"].idxmin()
            if qnum == 2
            else df["فجوة التوزيع"].idxmax()
        )
        row = df.loc[idx]
        st.metric(
            row["region"],
            f'{row["فجوة التوزيع"]:+.2f} pp'
        )
        st.write(row["priority_label"])

    elif qnum == 4:
        st.write(t["ai_note"])
        cluster_col = next(
            (
                c for c in [
                    "المجموعة النهائية",
                    "المجموعة",
                    "Cluster",
                    "cluster"
                ] if c in df.columns
            ),
            None
        )
        if cluster_col:
            st.dataframe(
                df.groupby(cluster_col)
                .size()
                .rename("Regions"),
                use_container_width=True
            )
        else:
            st.warning(t["no_cluster"])

    else:
        st.info(t["note"])
        st.write(t["priority_rule"])

    st.info(t["note"])

if page in ["home", "geo", "priority", "compare", "ml"]:
    explain_metrics()
    evidence_boundary()

# 19. الملخص التنفيذي الجديد
if page == "executive":
    st.header(
        "الملخص التنفيذي | دقيقة واحدة"
        if rtl else "Executive summary | One minute"
    )

    st.write(
        "**المشكلة:** تفاوت الحصص الجغرافية للجهات والمستفيدين."
        if rtl else
        "**Problem:** Regional differences in organization and beneficiary shares."
    )

    st.write(
        "**المنهجية:** حساب الفجوة بالنقاط المئوية وتصنيف الأولوية حسب قيمتها المطلقة."
        if rtl else
        "**Method:** Calculate the percentage-point gap and classify priority by its absolute magnitude."
    )

    a, b, c, d = st.columns(4)
    a.metric(t["regions"], len(df))
    b.metric(t["high"], counts.get("high", 0))
    c.metric(t["medium"], counts.get("medium", 0))
    d.metric(t["low"], counts.get("low", 0))

    high = (
        df.loc[df["priority"] == "high"]
        .assign(abs_gap=lambda x: x["فجوة التوزيع"].abs())
        .sort_values("abs_gap", ascending=False)
    )

    st.subheader(
        "المناطق ذات الأولوية المرتفعة"
        if rtl else "High-priority regions"
    )
    for _, r in high.iterrows():
        st.write(
            f'**{r["region"]}:** '
            f'{r["فجوة التوزيع"]:+.2f} pp'
        )

    st.write(
        "**النتيجة:** ثلاث مناطق ذات أولوية مرتفعة للمراجعة، وخمس متوسطة، وخمس منخفضة."
        if rtl else
        "**Finding:** Three high-priority, five medium-priority and five low-priority regions."
    )

    st.write(
        "**التوصية:** تختلف إجراءات المراجعة حسب حجم الفجوة واتجاهها؛ ولا يُعتمد التوسع أو إعادة توزيع الموارد دون بيانات التغطية الفعلية."
        if rtl else
        "**Recommendation:** Investigations should reflect gap magnitude and direction; expansion or reallocation requires actual coverage evidence."
    )

    evidence_boundary()
    explain_metrics()

# 20. قصة أثر وفق المنهجية الجديدة
elif page == "story":
    st.header(
        "قصة أثر: من السؤال إلى القرار"
        if rtl else "ATHAR Story: From Question to Decision"
    )

    if rtl:
        steps = [
            ("1. التحدي", "هل تتوازن الحصص الجغرافية للجهات والمستفيدين؟"),
            ("2. البيانات", "مقارنة الحصص النسبية في 13 منطقة سعودية."),
            ("3. حساب الفجوة", "نسبة المستفيدين ناقص نسبة الجهات بالنقاط المئوية."),
            ("4. تحديد الأولوية", "تصنيف المناطق حسب القيمة المطلقة للفجوة إلى مرتفعة ومتوسطة ومنخفضة."),
            ("5. النتائج", "3 مناطق مرتفعة، و5 متوسطة، و5 منخفضة."),
            ("6. التوصيات", "اقتراح مسارات دراسة مختلفة للفجوات الموجبة والسالبة."),
            ("7. القرار", "التحقق من السعة والتغطية والاحتياج الفعلي قبل التدخل.")
        ]
    else:
        steps = [
            ("1. Challenge", "Do regional shares of organizations and beneficiaries align?"),
            ("2. Data", "Compare relative shares across 13 Saudi regions."),
            ("3. Gap", "Beneficiary share minus organization share in percentage points."),
            ("4. Priority", "Classify absolute gaps as high, medium or low."),
            ("5. Results", "Three high, five medium and five low priority regions."),
            ("6. Recommendations", "Different study pathways for positive and negative gaps."),
            ("7. Decision", "Verify capacity, coverage and actual needs before action.")
        ]

    for heading, body in steps:
        st.subheader(heading)
        st.write(body)

    evidence_boundary()

# 21. التوصيات الاستراتيجية الجديدة
elif page == "recommendations":
    st.header(t["recommendations"])

    st.caption(
        "توصيات استكشافية مرتبطة بالمنهجية الجديدة وليست قرارات تنفيذية."
        if rtl else
        "Exploratory recommendations based on the approved methodology, not implementation mandates."
    )

    region = st.selectbox(
        t["select"],
        df["region"].tolist(),
        key="recommendation_region"
    )
    row = df.loc[df["region"] == region].iloc[0]

    a, b, c = st.columns(3)
    a.metric(t["entities"], f'{row["نسبة الجهات %"]:.2f}%')
    b.metric(t["beneficiaries"], f'{row["نسبة المستفيدين %"]:.2f}%')
    c.metric(t["gap"], f'{row["فجوة التوزيع"]:+.2f} pp')

    st.write(f'**{row["priority_label"]}**')

    title, reason, action = region_advice(row)
    st.subheader(title)

    evidence = (
        interpret_gap(row["فجوة التوزيع"])
        + f' ({row["فجوة التوزيع"]:+.2f} pp).'
    )

    data_needed = (
        "مواقع الخدمات، تخصصات الجهات، الطاقة الاستيعابية، أعداد المستفيدين الفريدين، قوائم الانتظار وسهولة الوصول."
        if rtl else
        "Service locations, specialties, capacity, unique beneficiaries, waiting lists and accessibility."
    )

    decision = (
        "التحقق من الاحتياج والتغطية ميدانيًا قبل التوسع أو إعادة توزيع الموارد."
        if rtl else
        "Validate needs and actual coverage before expansion or resource reallocation."
    )

    card_items = [
        (
            "🔎 1. ماذا اكتشفنا؟"
            if rtl else "🔎 1. What did we find?",
            evidence
        ),
        (
            "💡 2. ماذا نقترح؟"
            if rtl else "💡 2. What do we suggest?",
            reason + " " + action
        ),
        (
            "📋 3. ما البيانات التي نحتاجها؟"
            if rtl else "📋 3. What data do we need?",
            data_needed
        ),
        (
            "⚖️ 4. ما القرار المناسب؟"
            if rtl else "⚖️ 4. What decision should be considered?",
            decision
        )
    ]

    left, right = st.columns(2)
    for i, (heading, body) in enumerate(card_items):
        with (left if i % 2 == 0 else right):
            with st.container(border=True):
                st.markdown("#### " + heading)
                st.write(body)

    st.subheader(
        "جميع المناطق"
        if rtl else "All Regions"
    )

    recs = []
    for _, r in (
        df.assign(abs_gap=df["فجوة التوزيع"].abs())
        .sort_values("abs_gap", ascending=False)
        .iterrows()
    ):
        rt, rr, ra = region_advice(r)
        recs.append({
            "المنطقة" if rtl else "Region": r["region"],
            "الفجوة (نقطة مئوية)" if rtl else "Gap (pp)": round(r["فجوة التوزيع"], 2),
            "الأولوية" if rtl else "Priority": r["priority_label"],
            "مسار الدراسة" if rtl else "Study pathway": rt,
            "الإجراء المقترح" if rtl else "Suggested action": ra
        })

    rec_df = pd.DataFrame(recs)
    st.dataframe(
        rec_df,
        hide_index=True,
        use_container_width=True
    )
    st.download_button(
        t["download"],
        rec_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="ATHAR_Recommendations.csv",
        mime="text/csv"
    )

    evidence_boundary()
    explain_metrics()

# 22. توثيق المنهجية
with st.expander(t["method"]):
    st.write(t["note"])
    st.write(t["priority_rule"])
    st.write(t["ai_note"])
    st.write(t["info"])

st.divider()
st.caption(
    "ATHAR © 2026 | Intelligent Regional Insights | By: Yasser Alsahli"
)
