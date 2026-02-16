# دليل تشغيل Med-Gemma على Google Colab

هذا الدليل يشرح كيفية تشغيل نظام Med-Gemma على بيئة Google Colab السحابية للاستفادة من كروت الشاشة القوية (GPU) مجاناً.

## المتطلبات المسبقة
1. حساب Google (Gmail).
2. حساب على [Hugging Face](https://huggingface.co/).
3. الموافقة على شروط استخدام موديل Gemma (إذا لزم الأمر) وإنشاء Access Token.

## خطوات التشغيل

### 1. تجهيز الملفات
1. ارفع مجلد المشروع (`medgemma`) بالكامل إلى **My Drive** في Google Drive الخاص بك.
   - يفضل أن يكون المسار: `My Drive/MedGemma`.

### 2. فتح Notebook

هناك طريقتان لفتح الملف:

#### الطريقة الأولى (الأكثر ضماناً): من Google Drive مباشرة
1. اذهب لمجلد المشروع في Google Drive.
2. انقر بـ **يمين الفأرة** على ملف `medgemma_colab.ipynb`.
3. اختر **Open with** (فتح باستخدام) > **Google Colaboratory**.
   - *إذا لم تجد الخيار، اختر "Connect more apps" وابحث عن Colaboratory وقم بتثبيته.*

#### الطريقة الثانية: من داخل Colab
1. اذهب إلى [Google Colab](https://colab.research.google.com/).
2. اختر **Open Notebook** ثم **Google Drive**.
3. ابحث عن اسم المجلد `medgemma` أو اسم الملف `medgemma_colab`.
4. إذا لم يظهر، جرب تبويب **Upload** وارفع الملف مباشرة من جهازك إلى كولاب.

### 3. إعداد البيئة (Runtime)
1. من القائمة العلوية في Colab، اختر `Runtime` > `Change runtime type`.
2. اختر `T4 GPU` من خيارات Hardware accelerator.
3. اضغط `Save`.

### 4. تشغيل الخلايا
قم بتشغيل الخلايا (Cells) واحدة تلو الأخرى بالترتيب:

1. **Mount Drive**: ستربط Colab بملفاتك على درايف.
2. **Setup Path**: تأكد أن `PROJECT_PATH` يشير لمكان المجلد الصحيح.
3. **Install Requirements**: سيقوم بتحميل المكتبات اللازمة.
4. **Hugging Face Login**: أدخل التوكن الخاص بك (Read Token) ليتمكن النظام من تحميل الموديل.
5. **Run App**: سيقوم بتشغيل السيرفر.

### 5. الدخول للتطبيق
عند ظهور رسالة `Running on public URL: https://xxxx.gradio.live`، اضغط على الرابط لفتح التطبيق في متصفحك.

---
## مشاكل شائعة
- **Out of Memory (OOM)**: إذا توقف التشغيل بسبب الذاكرة، تأكد من أنك لا تشغل جلسات Colab أخرى، واعد تشغيل Runtime.
- **Model not found**: تأكد من قبولك لشروط Gemma على Hugging Face وأن التوكن صحيح.
