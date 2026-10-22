import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import io

st.set_page_config(page_title='ATHAR | أثر', page_icon='✦', layout='wide', initial_sidebar_state='expanded')
BASE = Path(__file__).resolve().parent
@st.cache_data
def load_data():
    return pd.read_csv(BASE / 'data' / 'ATHAR_AI_Clusters.csv')

df = load_data()
required = ['مناطق المملكة', 'نسبة الجهات %', 'نسبة المستفيدين %', 'فجوة التوزيع']
missing = [c for c in required if c not in df.columns]
if missing:
    st.error('Missing required columns: ' + ', '.join(missing))
    st.stop()
for c in required[1:]:
    df[c] = pd.to_numeric(df[c], errors='coerce')
if df[required].isna().any().any() or df['مناطق المملكة'].duplicated().any():
    st.error('Data quality validation failed. Please inspect the source CSV.')
    st.stop()

REGIONS = {'الرياض':'Riyadh','مكة المكرمة':'Makkah','المدينة المنورة':'Madinah','الشرقية':'Eastern Province','القصيم':'Qassim','عسير':'Asir','تبوك':'Tabuk','حائل':'Hail','الحدود الشمالية':'Northern Borders','جازان':'Jazan','نجران':'Najran','الباحة':'Al Bahah','الجوف':'Al Jawf'}
TEXT = {
 'ar': {'home':'الرئيسية','geo':'التحليل الجغرافي','priority':'أولويات المناطق','compare':'مقارنة المناطق','ml':'التحليل الذكي','assistant':'مساعد أثر','title':'أثر | منصة دعم القرار','subtitle':'رؤى تحليلية لتوزيع الجهات والمستفيدين في مناطق المملكة','regions':'المناطق السعودية','high':'أولوية مرتفعة','medium':'أولوية متوسطة','other':'دون فجوة سالبة','entities':'نسبة الجهات','beneficiaries':'نسبة المستفيدين','gap':'فجوة التوزيع','select':'اختر المنطقة','chart':'توزيع الجهات والمستفيدين','gapchart':'الفجوة حسب المنطقة (نقطة مئوية)','compare_select':'اختر منطقتين','download':'تنزيل البيانات المعروضة (CSV)','method':'المنهجية والقيود','ask':'اختر سؤالًا للمساعد','q1':'ما المناطق ذات الأولوية المرتفعة؟','q2':'ما أكبر فجوة سالبة؟','q3':'ما أعلى فجوة موجبة؟','q4':'ما نتائج التجميع الذكي؟','q5':'ما حدود هذه المؤشرات؟','note':'الفجوة = نسبة المستفيدين − نسبة الجهات، بوحدة النقطة المئوية. التصنيف مؤشر نسبي للمراجعة ولا يثبت نقص الخدمات.','clusters':'المجموعات الناتجة عن K-Means','ai_note':'اختيرت مجموعتان في التحليل السابق وفق Silhouette = 0.7008. هذه مجموعات إحصائية وليست قياسًا مباشرًا للاحتياج.','info':'بيانات سعودية؛ راجع ملفات المصادر والتوثيق قبل اتخاذ أي قرار.','priority_rule':'قاعدة عرض تفسيرية: مرتفعة إذا الفجوة ≤ −1، متوسطة إذا −1 < الفجوة < 0، وغير سالبة خلاف ذلك.','no_cluster':'عمود المجموعات غير متوفر في ملف النتائج.','not_chat':'هذا مساعد تحليلي قائم على أسئلة محددة وإجابات محسوبة، وليس نموذجًا لغويًا عامًا.'},
 'en': {'home':'Home','geo':'Regional Analysis','priority':'Regional Priorities','compare':'Compare Regions','ml':'AI Analysis','assistant':'ATHAR Assistant','title':'ATHAR | Decision Intelligence','subtitle':'Evidence-based regional insights into organizations and beneficiaries in Saudi Arabia','regions':'Saudi Regions','high':'High Priority','medium':'Medium Priority','other':'No Negative Gap','entities':'Organizations Share','beneficiaries':'Beneficiaries Share','gap':'Distribution Gap','select':'Select Region','chart':'Organizations and Beneficiaries Distribution','gapchart':'Regional Gap (percentage points)','compare_select':'Select two regions','download':'Download displayed data (CSV)','method':'Methodology & Limitations','ask':'Choose a question','q1':'Which regions are high priority?','q2':'Which region has the largest negative gap?','q3':'Which region has the largest positive gap?','q4':'What are the clustering results?','q5':'What are the limitations?','note':'Gap = beneficiary share − organization share, measured in percentage points. This relative indicator does not establish unmet service needs.','clusters':'K-Means clusters','ai_note':'Two clusters were selected in earlier analysis (Silhouette = 0.7008). Statistical groups are not direct measures of service need.','info':'Saudi datasets; consult source documentation before making decisions.','priority_rule':'Interpretive display rule: high if gap ≤ −1, medium if −1 < gap < 0, otherwise no negative gap.','no_cluster':'Cluster assignment column is unavailable in the results file.','not_chat':'This is a question-based analytical assistant, not a general-purpose language model.'}
}
with st.sidebar:
    st.markdown('## ✦ ATHAR | أثر')
    language = st.radio('Language / اللغة', ['العربية','English'], horizontal=True)
lang = 'ar' if language == 'العربية' else 'en'
t = TEXT[lang]
rtl = lang == 'ar'
df['region'] = df['مناطق المملكة'].map(lambda s: s if rtl else REGIONS.get(s, s))
df['priority'] = np.select([df['فجوة التوزيع'] <= -1, df['فجوة التوزيع'] < 0], ['high','medium'], default='other')
priority_labels = {'high':t['high'],'medium':t['medium'],'other':t['other']}
df['priority_label'] = df['priority'].map(priority_labels)
COLORS = {'high':'#F87171','medium':'#FBBF24','other':'#2DD4BF'}

st.markdown('''<style>
.stApp {background:linear-gradient(125deg,#071426,#102b43);color:#EAF4FA}
[data-testid="stSidebar"] {background:#0B1B30}
[data-testid="stMetric"] {background:#14334b;border:1px solid #2a536a;border-radius:16px;padding:18px}
[data-testid="stMetricValue"] {color:#48e3ce}
h1,h2,h3 {color:#f1f8ff!important}
</style>''',unsafe_allow_html=True)
with st.sidebar:
    pages = ['home','geo','priority','compare','ml','assistant']
    page = st.radio('Navigation / التنقل', pages, format_func=lambda x:t[x])
    st.divider()
    st.caption('ATHAR © 2026')
    st.caption('By: Yasser Alsahli')

st.markdown(f'<div dir="{"rtl" if rtl else "ltr"}" style="text-align:{"right" if rtl else "left"}"><h1>✦ {t["title"]}</h1><p>{t["subtitle"]}</p></div>',unsafe_allow_html=True)
st.divider()

def bars(frame, field1='نسبة الجهات %', field2='نسبة المستفيدين %'):
    data = frame.sort_values('نسبة المستفيدين %')
    fig = go.Figure()
    for field,label,color in [(field1,t['entities'],'#38BDF8'),(field2,t['beneficiaries'],'#2DD4BF')]:
        fig.add_trace(go.Bar(y=data['region'],x=data[field],name=label,orientation='h',marker_color=color,hovertemplate='%{y}: %{x:.2f}%<extra></extra>'))
    fig.update_layout(barmode='group',height=max(440,36*len(data)+160),template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis_title='%',yaxis_title='',margin=dict(l=10,r=10,t=40,b=20),legend=dict(orientation='h',y=1.12))
    st.plotly_chart(fig,use_container_width=True)

def gap_chart(frame):
    data = frame.sort_values('فجوة التوزيع')
    fig = go.Figure(go.Bar(y=data['region'],x=data['فجوة التوزيع'],orientation='h',marker_color=[COLORS[x] for x in data['priority']],hovertemplate='%{y}: %{x:+.2f} pp<extra></extra>'))
    fig.update_layout(height=max(440,36*len(data)+160),template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',xaxis_title=t['gap']+' (pp)',yaxis_title='',margin=dict(l=10,r=10,t=20,b=20))
    fig.add_vline(x=0,line_color='#DDE7EF')
    st.plotly_chart(fig,use_container_width=True)

def table(frame):
    display = frame[['region','نسبة الجهات %','نسبة المستفيدين %','فجوة التوزيع','priority_label']].copy()
    display.columns = [t['regions'],t['entities']+' (%)',t['beneficiaries']+' (%)',t['gap']+' (pp)',t['priority']]
    for c in display.columns[1:4]: display[c] = display[c].round(2)
    st.dataframe(display,use_container_width=True,hide_index=True)
    csv = display.to_csv(index=False).encode('utf-8-sig')
    st.download_button(t['download'],data=csv,file_name='ATHAR_Regional_View.csv',mime='text/csv')

if page == 'home':
    a,b,c,d = st.columns(4)
    a.metric(t['regions'],len(df))
    b.metric(t['high'],int((df['priority']=='high').sum()))
    c.metric(t['medium'],int((df['priority']=='medium').sum()))
    d.metric(t['other'],int((df['priority']=='other').sum()))
    st.subheader(t['chart']); bars(df)
    st.info(t['note'])
elif page == 'geo':
    region = st.selectbox(t['select'],df['region'].tolist())
    selected = df.loc[df['region']==region].iloc[0]
    a,b,c = st.columns(3)
    a.metric(t['entities'],f'{selected["نسبة الجهات %"]:.2f}%')
    b.metric(t['beneficiaries'],f'{selected["نسبة المستفيدين %"]:.2f}%')
    c.metric(t['gap'],f'{selected["فجوة التوزيع"]:+.2f} pp')
    st.subheader(t['gapchart']); gap_chart(df)
    st.info(t['note'])
elif page == 'priority':
    st.subheader(t['priority'])
    filter_options = ['all','high','medium','other']
    selected = st.selectbox('Filter / تصفية',filter_options,format_func=lambda x:('الكل' if rtl else 'All') if x=='all' else priority_labels[x])
    filtered = df if selected=='all' else df.loc[df['priority']==selected]
    gap_chart(filtered); table(filtered)
    st.caption(t['priority_rule']); st.info(t['note'])
elif page == 'compare':
    choices = st.multiselect(t['compare_select'],df['region'].tolist(),default=df['region'].tolist()[:2],max_selections=2)
    if len(choices)==2:
        subset = df.loc[df['region'].isin(choices)]
        bars(subset); table(subset)
    else:
        st.info(t['compare_select'])
elif page == 'ml':
    st.subheader(t['ml']); st.info(t['ai_note'])
    cluster_col = next((c for c in ['المجموعة النهائية','المجموعة','Cluster','cluster'] if c in df.columns),None)
    if cluster_col:
        cluster_counts = df.groupby(cluster_col).size().reset_index(name='count')
        fig = px.bar(cluster_counts,x=cluster_col,y='count',text='count',template='plotly_dark',color_discrete_sequence=['#2DD4BF'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig,use_container_width=True)
        display = df[['region',cluster_col,'فجوة التوزيع']].copy()
        display['فجوة التوزيع'] = display['فجوة التوزيع'].round(2)
        st.dataframe(display,use_container_width=True,hide_index=True)
    else:
        st.warning(t['no_cluster'])
elif page == 'assistant':
    st.subheader('✦ ATHAR AI')
    st.caption(t['not_chat'])
    q = st.selectbox(t['ask'],[t[f'q{i}'] for i in range(1,6)])
    qnum = [t[f'q{i}'] for i in range(1,6)].index(q)+1
    if qnum==1:
        high = df[df['priority']=='high'].sort_values('فجوة التوزيع')
        st.write(', '.join(f'{r.region} ({r["فجوة التوزيع"]:+.2f} pp)' for _,r in high.iterrows()))
    elif qnum in (2,3):
        row = df.loc[df['فجوة التوزيع'].idxmin() if qnum==2 else df['فجوة التوزيع'].idxmax()]
        st.metric(row['region'],f'{row["فجوة التوزيع"]:+.2f} pp')
    elif qnum==4:
        st.write(t['ai_note'])
        cluster_col = next((c for c in ['المجموعة النهائية','المجموعة','Cluster','cluster'] if c in df.columns),None)
        if cluster_col: st.dataframe(df.groupby(cluster_col).size().rename('Regions'),use_container_width=True)
    else: st.info(t['note']+' '+t['priority_rule'])
    st.info(t['note'])

with st.expander(t['method']):
    st.write(t['note'])
    st.write(t['priority_rule'])
    st.write(t['info'])
    st.caption('K-Means: 2 clusters; Silhouette 0.7008 (previous analysis).')
st.divider()
st.caption('ATHAR © 2026 | Intelligent Regional Insights | By: Yasser Alsahli')
