# 1. إنشاء موجز PDF عربي أو إنجليزي بالقيم المعتمدة
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import arabic_reshaper
from bidi.algorithm import get_display
from core import BASE,E,B,G,label,direction,advice,LIMIT_AR,LIMIT_EN,NEEDS_AR,NEEDS_EN,REGIONS

pdfmetrics.registerFont(TTFont('Athar',str(BASE/'assets/DejaVuSans.ttf')))

def make_pdf(d,ar=True,region=None):
    buf=BytesIO();c=canvas.Canvas(buf,pagesize=A4);w,h=A4
    c.setTitle('ATHAR - Regional Brief' if region else 'ATHAR - Executive Summary')
    y=h-100;number=0
    def shape(s):
        import re
        if not ar:return s
        s=re.sub(r'[+−-]?\d+(?:\.\d+)?%?', lambda m:'\u202a'+m.group()+'\u202c',s)
        return get_display(arabic_reshaper.reshape(s))
    def newpage():
        nonlocal y,number
        number+=1
        c.setFillColor(HexColor('#071422'));c.rect(0,0,w,h,fill=1,stroke=0)
        c.setFillColor(HexColor('#61E4CF'));c.setFont('Athar',18);c.drawString(42,h-48,'ATHAR | '+shape('أثر'))
        c.setFillColor(HexColor('#AFC3D2'));c.setFont('Athar',8);c.drawString(42,30,'By Yasser Alsahli | 2026');c.drawRightString(w-42,30,str(number));y=h-88
    def text(s,size=10,color='#EAF4FA'):
        nonlocal y
        words=str(s).split();line='';lines=[]
        for word in words:
            test=(line+' '+word).strip()
            if pdfmetrics.stringWidth(shape(test),'Athar',size)>w-84:
                if line:lines.append(line)
                line=word
            else:line=test
        if line:lines.append(line)
        for line in lines:
            if y<65:c.showPage();newpage()
            c.setFillColor(HexColor(color));c.setFont('Athar',size)
            if ar:c.drawRightString(w-42,y,shape(line))
            else:c.drawString(42,y,line)
            y-=size*1.85
        y-=7
    newpage()
    text(('موجز المنطقة' if region else 'الملخص التنفيذي') if ar else ('Regional brief' if region else 'Executive summary'),19,'#61E4CF')
    text('13 منطقة | 3 مرتفعة | 5 متوسطة | 5 منخفضة' if ar else '13 regions | 3 high | 5 medium | 5 low')
    subset=d[d.region_ar==region] if region else d[d.priority=='high'].sort_values(G,key=lambda s:s.abs(),ascending=False)
    for _,r in subset.iterrows():
        text(r.region_ar if ar else REGIONS[r.region_ar],15,'#61E4CF')
        text((f'حصة الجهات: {r[E]:.2f}% | حصة المستفيدين: {r[B]:.2f}%' if ar else f'Organization share: {r[E]:.2f}% | Beneficiary share: {r[B]:.2f}%'))
        text((f'الفجوة: {r[G]:+.2f} نقطة مئوية | أولوية المراجعة: {label(r.priority)}' if ar else f'Gap: {r[G]:+.2f} pp | Review priority: {label(r.priority,False)}'))
        text(direction(r[G],ar));p,a=advice(r,ar);text(p,12);text(a)
    text('البيانات المطلوبة قبل القرار' if ar else 'Evidence required before action',13,'#61E4CF');text(NEEDS_AR if ar else NEEDS_EN)
    text('المنهجية والقيود' if ar else 'Methodology and limitations',13,'#61E4CF')
    text('الفجوة تساوي حصة المستفيدين ناقص حصة الجهات. حسب القيمة المطلقة: مرتفعة تتجاوز ثلاث نقاط؛ متوسطة تتجاوز نقطة وحتى ثلاث نقاط؛ منخفضة نقطة أو أقل. التصنيف قبل التقريب.' if ar else 'Gap = beneficiary share minus organization share. Absolute thresholds: high >3; medium >1 to 3; low ≤1. Classification precedes rounding.')
    text(LIMIT_AR if ar else LIMIT_EN)
    text('المصدر والتوثيق' if ar else 'Source and documentation',13,'#61E4CF')
    text('ATHAR_AI_Clusters.csv | ATHAR_Cleaned_Data.csv',9)
    text('ملفا المشروع المرفقان هما مصدر القيم المعروضة. روابط المصادر الأصلية وتواريخ رصدها غير مرفقة في هذه النسخة. تاريخ بناء المنصة: 2026-10-30، وليس تاريخ البيانات.' if ar else 'The supplied project files support displayed values. Original source URLs and observation dates are not supplied in this version. Platform build: 2026-10-30; this is not the data date.',9)
    c.save();return buf.getvalue()
