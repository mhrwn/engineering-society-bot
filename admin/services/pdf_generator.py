#!/usr/bin/env python3
"""
سرویس تولید گزارش‌های PDF با استفاده از reportlab
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
import os
from datetime import datetime
from config import Config
import logging

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    def __init__(self):
        self.font_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts')
        self.setup_fonts()
    
    def setup_fonts(self):
        """تنظیم فونت‌های فارسی"""
        try:
            # بررسی وجود فونت فارسی
            farsi_font_path = os.path.join(self.font_path, 'farsi_font.ttf')
            if os.path.exists(farsi_font_path):
                pdfmetrics.registerFont(TTFont('Farsi', farsi_font_path))
                self.farsi_font = 'Farsi'
                logger.info("✅ فونت فارسی با موفقیت بارگذاری شد")
            else:
                self.farsi_font = 'Helvetica'
                logger.warning("⚠️ فونت فارسی یافت نشد، از فونت پیش‌فرض استفاده می‌شود")
        except Exception as e:
            self.farsi_font = 'Helvetica'
            logger.warning(f"⚠️ خطا در بارگذاری فونت فارسی: {e} - از فونت پیش‌فرض استفاده می‌شود")
    
    def create_event_report(self, events_data, registrations_data, output_path=None):
        """ایجاد گزارش PDF برای رویدادها"""
        try:
            if not output_path:
                reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
                os.makedirs(reports_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(reports_dir, f"event_report_{timestamp}.pdf")
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # ایجاد استایل‌های سفارشی
            farsi_style = ParagraphStyle(
                'FarsiStyle',
                parent=styles['Normal'],
                fontName=self.farsi_font,
                fontSize=10,
                alignment=2  # راست‌چین
            )
            
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontName=self.farsi_font,
                fontSize=16,
                alignment=1,  # وسط‌چین
                spaceAfter=30
            )
            
            elements = []
            
            # عنوان گزارش
            title = Paragraph("گزارش رویدادها", title_style)
            elements.append(title)
            
            # اطلاعات انجمن
            society_info = Paragraph(Config.SOCIETY_NAME, farsi_style)
            elements.append(society_info)
            
            university_info = Paragraph(Config.UNIVERSITY, farsi_style)
            elements.append(university_info)
            
            date_info = Paragraph(f"تاریخ تولید: {datetime.now().strftime('%Y-%m-%d %H:%M')}", farsi_style)
            elements.append(date_info)
            
            elements.append(Spacer(1, 20))
            
            # آمار کلی
            if events_data:
                stats_text = f"""
                آمار کلی:
                تعداد کل رویدادها: {events_data.get('total_events', 0)}
                رویدادهای فعال: {events_data.get('active_events', 0)}
                کل ثبت نام ها: {events_data.get('total_registrations', 0)}
                میانگین ثبت نام: {events_data.get('avg_registrations', 0):.1f}
                """
                
                stats_paragraph = Paragraph(stats_text, farsi_style)
                elements.append(stats_paragraph)
                elements.append(Spacer(1, 15))
            
            # جدول رویدادها
            if events_data and events_data.get('events'):
                events_title = Paragraph("لیست رویدادها:", farsi_style)
                elements.append(events_title)
                elements.append(Spacer(1, 10))
                
                # ایجاد داده‌های جدول
                table_data = [['عنوان', 'تاریخ', 'ظرفیت', 'ثبت نام', 'وضعیت']]
                
                for event in events_data['events'][:8]:  # فقط 8 رویداد اول
                    status = "فعال" if event.get('is_active') else "غیرفعال"
                    table_data.append([
                        str(event.get('title', 'بدون عنوان'))[:20],
                        str(event.get('date', 'نامشخص'))[:10],
                        str(event.get('capacity', 0)),
                        str(event.get('registrations_count', 0)),
                        status
                    ])
                
                # ایجاد جدول
                table = Table(table_data, colWidths=[70*mm, 30*mm, 20*mm, 20*mm, 20*mm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), self.farsi_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), self.farsi_font),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 20))
            
            # ثبت‌نام‌های اخیر
            if registrations_data:
                reg_title = Paragraph("آخرین ثبت نام ها:", farsi_style)
                elements.append(reg_title)
                elements.append(Spacer(1, 10))
                
                reg_data = [['نام کاربر', 'رویداد', 'تاریخ']]
                
                for reg in registrations_data[:10]:  # فقط 10 ثبت‌نام اول
                    reg_data.append([
                        str(reg.get('user_name', 'نامشخص'))[:15],
                        str(reg.get('event_title', 'بدون عنوان'))[:20],
                        str(reg.get('registration_date', 'نامشخص'))[:10]
                    ])
                
                reg_table = Table(reg_data, colWidths=[50*mm, 70*mm, 30*mm])
                reg_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), self.farsi_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('FONTNAME', (0, 1), (-1, -1), self.farsi_font),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                ]))
                
                elements.append(reg_table)
            
            # ساخت PDF
            doc.build(elements)
            logger.info(f"✅ گزارش PDF در {output_path} ایجاد شد")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ خطا در تولید گزارش PDF: {e}")
            return None

# نمونه جهانی
pdf_generator = PDFReportGenerator()
