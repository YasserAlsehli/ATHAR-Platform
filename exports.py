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

# 2. خط مضمّن لدعم العربية دون الاعتماد على ملفات الاستضافة
import base64
import zlib
from functools import lru_cache
