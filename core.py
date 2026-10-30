# 1. تحميل البيانات والتحقق من المرجع المعتمد
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
REGIONS = dict(zip(
    ['الرياض','مكة المكرمة','المدينة المنورة','الشرقية','القصيم','عسير','تبوك','حائل','الحدود الشمالية','جازان','نجران','الباحة','الجوف'],
    ['Riyadh','Makkah','Madinah','Eastern Province','Qassim','Asir','Tabuk','Hail','Northern Borders','Jazan','Najran','Al Bahah','Al Jawf']))
E, B, G = 'نسبة الجهات %', 'نسبة المستفيدين %', 'فجوة التوزيع'
COLORS = {'high':'#FB8585','medium':'#F5C96A','low':'#37D4BF'}

def normalize(s):
    s = re.sub(r'[ـ\u064b-\u065f]', '', str(s)).strip()
    return re.sub(r'^(المنطقة|منطقة)\s+', '', s)

def load_data():
    d = pd.read_csv(BASE/'data/ATHAR_AI_Clusters.csv')
    needed = ['مناطق المملكة', E, B, G, 'المجموعة النهائية']
    if any(c not in d for c in needed):
        raise ValueError('أعمدة ملف النتائج غير مكتملة / Missing result columns')
    for c in [E,B,G,'المجموعة النهائية']:
        d[c] = pd.to_numeric(d[c], errors='coerce')
    if d[needed].isna().any().any() or not np.isfinite(d[[E,B,G,'المجموعة النهائية']]).all().all():
        raise ValueError('قيم مفقودة أو غير صالحة / Invalid values')
    d['region_ar'] = d['مناطق المملكة'].map(normalize)
    if len(d)!=13 or d.region_ar.duplicated().any() or set(d.region_ar)!=set(REGIONS):
        raise ValueError('مناطق البيانات لا تطابق المرجع / Regions mismatch')
    if not np.allclose(d[G],d[B]-d[E],rtol=0,atol=.02):
        raise ValueError('الفجوة لا تطابق المنهجية / Gap mismatch')
    if not all(abs(d[c].sum()-100)<.02 and d[c].between(0,100).all() for c in [E,B]):
        raise ValueError('الحصص غير صالحة / Invalid shares')
    d['priority'] = np.select([d[G].abs()>3,d[G].abs()>1],['high','medium'],default='low')
    if d.priority.value_counts().to_dict() != {'medium':5,'low':5,'high':3}:
        raise ValueError('الأولويات لا تطابق المرجع / Priority mismatch')
    ref=json.loads((BASE/'data/reference.json').read_text())
    for row in d.to_dict('records'):
        r=ref[row['region_ar']]
        if any(not np.isclose(row[c],r[c],rtol=0,atol=1e-8) for c in [E,B,G,'المجموعة النهائية']):
            raise ValueError('النتائج تغيرت عن المرجع / Approved reference changed')
    clean = pd.read_csv(BASE/'data/ATHAR_Cleaned_Data.csv')
    clean['region_ar'] = clean['region_key'].map(normalize)
    if len(clean)!=13 or clean.region_ar.duplicated().any():
        raise ValueError('ملف الأعداد لا يطابق المناطق / Count file region mismatch')
    clean=clean.set_index('region_ar').reindex(d.region_ar)
    for field,target in [('عدد الجهات',E),('الإجمالي',B)]:
        values=pd.to_numeric(clean[field],errors='coerce')
        if values.isna().any() or (values<0).any() or values.sum()<=0:
            raise ValueError('قيم الأعداد غير صالحة / Invalid counts')
        if not np.allclose(100*values.to_numpy()/values.sum(),d[target],rtol=0,atol=.000001):
            raise ValueError('حصص الأعداد تختلف عن النتائج / Count shares mismatch')
    return d

# 2. التفسير ومسارات الدراسة دون تغيير المؤشرات

def label(level, ar=True):
    return ({'high':'مرتفعة','medium':'متوسطة','low':'منخفضة'} if ar else {'high':'High','medium':'Medium','low':'Low'})[level]

def direction(g, ar=True):
    if g>0: return 'حصة المستفيدين أعلى من حصة الجهات' if ar else 'Beneficiary share exceeds organization share'
    if g<0: return 'حصة الجهات أعلى من حصة المستفيدين' if ar else 'Organization share exceeds beneficiary share'
    return 'الحصتان متساويتان' if ar else 'Both shares are equal'

def advice(row, ar=True):
    g,p=float(row[G]),row['priority']
    if p=='high' and g>0:
        return ('دراسة التغطية والطاقة الاستيعابية','فحص مواقع الخدمات والسعة وقوائم الانتظار، ثم دراسة التوسع أو الشراكات إذا ثبت الاحتياج.') if ar else ('Assess coverage and capacity','Check service locations, capacity and waiting lists; consider expansion or partnerships only if unmet needs are established.')
    if p=='high':
        return ('مراجعة توزيع الجهات وتخصصاتها','فحص تخصصات الجهات وانتشارها واستخدام خدماتها، دون افتراض وجود فائض خدمي.') if ar else ('Review organization distribution and specialties','Review specialties, locations and utilization without assuming a service surplus.')
    if p=='medium' and g>0:
        return ('فحص الوصول والتغطية المحلية','دراسة سهولة الوصول والتوزيع داخل المنطقة والتحقق من وجود فجوات خدمية فعلية.') if ar else ('Assess access and local coverage','Study access and within-region distribution to establish whether actual service gaps exist.')
    if p=='medium':
        return ('مراجعة التنسيق والتخصصات','مراجعة الشراكات وتكامل التخصصات ومدى ملاءمة الخدمات للمستفيدين داخل المنطقة.') if ar else ('Review coordination and specialties','Review partnerships, complementary specialties and suitability of services within the region.')
    return ('المتابعة والمراجعة الدورية','متابعة التغيرات وفحص الفروق داخل المنطقة وجودة الوصول دون افتراض اكتمال التغطية.') if ar else ('Monitor and review periodically','Monitor changes, local disparities and accessibility without assuming complete coverage.')

LIMIT_AR='الفجوة تقارن الحصص النسبية؛ لا تثبت نقص الخدمات أو فائضها أو جودتها. القرار التنفيذي يحتاج أدلة عن التغطية والاحتياج الفعلي.'
LIMIT_EN='The gap compares relative shares; it does not establish service shortages, surpluses or quality. Operational decisions require actual coverage and needs evidence.'
NEEDS_AR='مواقع الخدمات، تخصصات الجهات، الطاقة الاستيعابية، أعداد المستفيدين الفريدين، قوائم الانتظار وسهولة الوصول.'
NEEDS_EN='Service locations, specialties, capacity, unique beneficiaries, waiting lists and accessibility.'

# 3. مساعد محلي موثق للأسئلة الشائعة وسياق المنطقة

def local_answer(q, d, selected, ar=True):
    qn=normalize(q).lower()
    names=[r for r,en in REGIONS.items() if r in qn or en.lower() in qn]
    rows=d[d.region_ar.isin(names or [selected])]
    if any(k in qn for k in ['k-means','kmeans','تجميع','مجموع','cluster']):
        counts=d.groupby('المجموعة النهائية').size().to_dict()
        return (f'التجميع المحفوظ: {counts}. أرقام المجموعات معرفات وليست ترتيبًا للأفضل أو الأكثر احتياجًا. متغيرات التدريب وإعداداته غير مرفقة؛ لا يمكن تفسير أسباب التشكيل من هذا الملف وحده. المصدر: ATHAR_AI_Clusters.csv، قسم التحليل الذكي.' if ar else f'Saved cluster sizes: {counts}. IDs are not quality or needs rankings. Training variables and settings are not supplied. Source: ATHAR_AI_Clusters.csv, AI Analysis.')
    if any(k in qn for k in ['مصدر','source','تاريخ','date','جود','نقص','فائض','حدود','limit']):
        return (LIMIT_AR+' مصدر الأرقام المعروضة: ATHAR_AI_Clusters.csv؛ تواريخ البيانات وروابط المصادر الأصلية تحتاج التوثيق المرفق بالدفتر.' if ar else LIMIT_EN+' Displayed values: ATHAR_AI_Clusters.csv. Original source links and data dates require notebook documentation.')
    if any(k in qn for k in ['منهج','حساب','نقطة','مئوي','method','formula','absolute','تصنيف']):
        return ('الفجوة = نسبة المستفيدين − نسبة الجهات، بالنقاط المئوية. الأولوية حسب القيمة المطلقة: مرتفعة >3؛ متوسطة >1 وحتى 3؛ منخفضة ≤1. مقدار الفجوة يحدد الأولوية وإشارتها تحدد الاتجاه. المصدر: المنهجية المعتمدة.' if ar else 'Gap = beneficiary share minus organization share, in percentage points. Absolute-gap thresholds: high >3; medium >1 to 3; low ≤1. Magnitude sets priority; sign gives direction. Source: approved methodology.')
    if any(k in qn for k in ['عدد المناطق','كم منطقة','how many regions']):
        return ('13 منطقة: 3 مرتفعة و5 متوسطة و5 منخفضة. المصدر: ATHAR_AI_Clusters.csv.' if ar else '13 regions: 3 high, 5 medium, 5 low. Source: ATHAR_AI_Clusters.csv.')
    if any(k in qn for k in ['أكبر','اكبر','largest','اعلى','أعلى']) and any(k in qn for k in ['سالب','negative']):
        rows=d.loc[[d[G].idxmin()]]
    elif any(k in qn for k in ['أكبر','اكبر','largest','اعلى','أعلى']) and any(k in qn for k in ['موجب','positive']):
        rows=d.loc[[d[G].idxmax()]]
    elif any(k in qn for k in ['مرتف','high','أكبر','اكبر','largest','اعلى','أعلى']):
        rows=d[d.priority=='high'].sort_values(G,key=lambda s:s.abs(),ascending=False)
    recognized=bool(names) or any(k in qn for k in ['منطق','فجوة','فجوه','أولو','اولوي','قارن','توص','قرار','نتيج','اشرح','region','gap','priorit','compar','recommend','decision','explain','مرتف','high','أكبر','اكبر','largest','هذه','هذي','this'])
    if not recognized:
        return ('لا تتوفر لدي إجابة موثقة عن هذا السؤال في الوضع المحلي. اسأل عن فجوة منطقة أو أولويتها أو المقارنة أو المنهجية؛ المحادثة اللغوية الأوسع تحتاج تفعيل الخدمة في الإعدادات.' if ar else 'No supported answer is available in local mode. Ask about regional gaps, priorities, comparisons or methodology. Broader language understanding requires the configured model service.')
    out=[]
    for _,r in rows.iterrows():
        name=r.region_ar if ar else REGIONS[r.region_ar]
        path,action=advice(r,ar)
        out.append(f'{name}: {r[B]:.2f}% − {r[E]:.2f}% = {r[G]:+.2f} '+('نقطة مئوية؛ أولوية مراجعة ' if ar else 'pp; review priority: ')+label(r.priority,ar)+f'. {direction(r[G],ar)}. {path}: {action}')
    return '\n\n'.join(out)+'\n\n'+(LIMIT_AR+' المصدر: ATHAR_AI_Clusters.csv، بطاقة المنطقة.' if ar else LIMIT_EN+' Source: ATHAR_AI_Clusters.csv, regional decision card.')
