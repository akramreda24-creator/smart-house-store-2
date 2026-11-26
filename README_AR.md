# Smart House Store — مشروع Django أولي

## المتطلبات
- Python 3.10 أو أحدث
- اتصال بالإنترنت لتثبيت الحزم أول مرة

## التشغيل على Windows
افتح CMD داخل مجلد المشروع ثم نفّذ:

```cmd
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

افتح الموقع:
- المتجر: http://127.0.0.1:8000/
- لوحة الإدارة الجديدة: http://127.0.0.1:8000/dashboard/\n- لوحة Django الأصلية (احتياطية): http://127.0.0.1:8000/admin/

## إضافة المنتجات
سجّل الدخول إلى لوحة الإدارة، ثم افتح المنتجات وأضف الاسم والسعر والوصف والصورة والمخزون. فعّل "ظاهر في المتجر" لنشر المنتج، و"منتج مميز" لإظهاره في قسم المنتجات المميزة.

## ملاحظات مهمة قبل النشر
- غيّر SECRET_KEY إلى قيمة سرية من متغيرات البيئة.
- اجعل DEBUG=False واضبط ALLOWED_HOSTS.
- استخدم PostgreSQL وخادم WSGI/ASGI وHTTPS.
- أضف سياسة خصوصية وشروط بيع وشحن واسترجاع.
- هذه نسخة تأسيسية؛ يجب اختبار المخزون والدفع والشحن قبل الاستخدام التجاري الفعلي.
