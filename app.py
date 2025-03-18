from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import pandas as pd
from flask import Response
from flask import Flask, send_file  # تأكد من استيراد send_file
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = 'secret123'  # مفتاح الجلسة لتأمين الكوكيز
# إنشاء قاعدة البيانات والجداول
def init_db():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()

    # جدول المشاريع
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    التسلسل INTEGER,
                    المحافظة TEXT,
                    المشروع TEXT UNIQUE,
                    مدرج_في_وزارة_التخطيط TEXT,
                    مؤشر_لدى_وزارة_المالية TEXT,
                    الكلفة_الكلية REAL,
                    الاستثناء_من_أساليب_التعاقد TEXT,
                    استثناء TEXT,
                    الإعلان DATE,
                    دراسة_سيرة_ذاتية BOOLEAN,
                    الدعوات BOOLEAN,
                    الوثيقة_القياسية BOOLEAN,
                    التخويل BOOLEAN,
                    تاريخ_غلق_الدعوات DATE,
                    لجان_الفتح BOOLEAN,
                    لجنة_تحليل BOOLEAN,
                    قرار_لجنة_التحليل_الى_دائرة_العقود BOOLEAN,
                    لجنة_المراجعة والمصادقة BOOLEAN,
                    الإحالة BOOLEAN,
                    مسودة_العقد BOOLEAN,
                    توقيع_العقد BOOLEAN,
                    ملاحظات TEXT
                )''')

    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')

    # إضافة مستخدم افتراضي إذا لم يكن موجودًا
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  ('admin', generate_password_hash('admin123')))

    conn.commit()
    conn.close()

# دالة للاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('projects.db')
    conn.row_factory = sqlite3.Row
    return conn

# صفحة تسجيل الدخول
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('home'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')

    return render_template('login.html')

# صفحة تسجيل المستخدمين
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('يرجى إدخال اسم مستخدم وكلمة مرور.', 'danger')
            return redirect(url_for('register'))

        conn = get_db_connection()
        c = conn.cursor()

        try:
            hashed_password = generate_password_hash(password)
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('اسم المستخدم موجود بالفعل. اختر اسمًا آخر.', 'warning')
        finally:
            conn.close()

    return render_template('register.html')

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('تم تسجيل الخروج.', 'info')
    return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))

    projects = get_projects()  # استرجاع المشاريع
    return render_template('home.html', projects=projects)  # تمرير المشاريع إلى القالب

# دالة لاسترجاع المشاريع من قاعدة البيانات
def get_projects():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM projects")
    projects = c.fetchall()
    conn.close()
    return projects

# إضافة مشروع
@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        البيانات = {
            'التسلسل': request.form.get('التسلسل', '').strip(),
            'المحافظة': request.form.get('المحافظة', '').strip(),
            'المشروع': request.form.get('المشروع', '').strip(),
            'مدرج_في_وزارة_التخطيط': request.form.get('مدرج_في_وزارة_التخطيط', '').strip(),
            'مؤشر_لدى_وزارة_المالية': request.form.get('مؤشر_لدى_وزارة_المالية', '').strip(),
            'الكلفة_الكلية': request.form.get('الكلفة_الكلية', '').strip(),
            'الاستثناء_من_أساليب_التعاقد': request.form.get('الاستثناء_من_أساليب_التعاقد', '').strip(),
            'استثناء': request.form.get('استثناء', '').strip(),
            'الإعلان': request.form.get('الإعلان', '').strip(),
            'تاريخ_غلق_الدعوات': request.form.get('تاريخ_غلق_الدعوات', '').strip(),
            'لجنة_تحليل': request.form.get('لجنة_تحليل', '').strip(),
            'قرار_لجنة_التحليل_الى_دائرة_العقود': request.form.get('قرار_لجنة_التحليل_الى_دائرة_العقود', '').strip(),
            'لجنة_المراجعة والمصادقة': request.form.get('لجنة_المراجعة والمصادقة', '').strip(),
            'الإحالة': request.form.get('الإحالة', '').strip(),
            'مسودة_العقد': request.form.get('مسودة_العقد', '').strip(),
            'توقيع_العقد': request.form.get('توقيع_العقد', '').strip(),
            'ملاحظات': request.form.get('ملاحظات', '').strip(),
            'دراسة_سيرة_ذاتية': 'صح' if request.form.get('دراسة_سيرة_ذاتية') else '',
            'الدعوات': 'صح' if request.form.get('الدعوات') else '',
            'الوثيقة_القياسية': 'صح' if request.form.get('الوثيقة_القياسية') else '',
            'التخويل': 'صح' if request.form.get('التخويل') else '',
            'لجان_الفتح': 'صح' if request.form.get('لجان_الفتح') else ''
        }

        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''INSERT INTO projects (
                            التسلسل, المحافظة, المشروع, مدرج_في_وزارة_التخطيط, مؤشر_لدى_وزارة_المالية, 
                            الكلفة_الكلية, الاستثناء_من_أساليب_التعاقد, استثناء, الإعلان, 
                            تاريخ_غلق_الدعوات, لجنة_تحليل, قرار_لجنة_التحليل_الى_دائرة_العقود, 
                            لجنة_المراجعة_والمصادقة, الإحالة, مسودة_العقد, توقيع_العقد, ملاحظات, 
                            دراسة_سيرة_ذاتية, الدعوات, الوثيقة_القياسية, التخويل, لجان_الفتح
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      tuple(البيانات.values()))

            conn.commit()
            flash('تمت إضافة المشروع بنجاح!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة المشروع: {str(e)}', 'danger')
        finally:
            conn.close()

    return render_template('add_project.html')


# دالة الاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('projects.db')
    conn.row_factory = sqlite3.Row  # يجعل النتائج على شكل قاموس
    return conn
@app.route('/edit_project', methods=['GET', 'POST'])
def edit_project():
    مشاريع = []

    if request.method == 'POST':
        اسم_المشروع = request.form.get('اسم_المشروع', '').strip()
        print(f"🔍 البحث عن المشروع: {اسم_المشروع}")

        if اسم_المشروع:
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row  # تمكين الوصول إلى البيانات بالقاموس
            try:
                c = conn.cursor()
                query = """
                    SELECT * FROM projects 
                    WHERE LOWER(TRIM(المشروع)) LIKE LOWER(?)
                """
                c.execute(query, ('%' + اسم_المشروع + '%',))
                مشاريع = c.fetchall()

                if not مشاريع:
                    flash("⚠️ لا توجد نتائج مطابقة للبحث.", "warning")
                else:
                    print(f"✅ تم العثور على {len(مشاريع)} مشروع.")
            except sqlite3.Error as e:
                flash(f"⚠️ خطأ في تنفيذ الاستعلام: {e}", "danger")
            finally:
                conn.close()

            مشاريع = [dict(row) for row in مشاريع]  # تحويل إلى قائمة قواميس

    return render_template('edit_project.html', مشاريع=مشاريع)


@app.route('/update_project', methods=['POST'])
def update_project():
    if request.method == 'POST':
        project_id = request.form.get('project_id')

        # 🔹 استرجاع كافة الحقول مع التأكد من أنها ليست None
        اسم_المشروع = request.form.get('المشروع', '').strip()
        المحافظة = request.form.get('المحافظة', '').strip()
        مدرج_في_وزارة_التخطيط = request.form.get('مدرج_في_وزارة_التخطيط', '').strip()
        مؤشر_لدى_وزارة_المالية = request.form.get('مؤشر_لدى_وزارة_المالية', '').strip()
        الكلفة_الكلية = request.form.get('الكلفة_الكلية', '0').strip()
        الاستثناء_من_أساليب_التعاقد = request.form.get('الاستثناء_من_أساليب_التعاقد', '').strip()
        استثناء = request.form.get('استثناء', '').strip()
        الإعلان = request.form.get('الإعلان', '').strip()
        تاريخ_غلق_الدعوات = request.form.get('تاريخ_غلق_الدعوات', '').strip()
        لجنة_تحليل = request.form.get('لجنة_تحليل', '').strip()
        قرار_لجنة_التحليل_الى_دائرة_العقود = request.form.get('قرار_لجنة_التحليل_الى_دائرة_العقود', '').strip()
        لجنة_المراجعة_والمصادقة = request.form.get('لجنة_المراجعة_والمصادقة', '').strip()
        الإحالة = request.form.get('الإحالة', '').strip()
        مسودة_العقد = request.form.get('مسودة_العقد', '').strip()
        توقيع_العقد = request.form.get('توقيع_العقد', '').strip()
        ملاحظات = request.form.get('ملاحظات', '').strip()

        # 🔹 الحقول التي تُرجع قيم `True` أو `False`
        دراسة_سيرة_ذاتية = bool(request.form.get('دراسة_سيرة_ذاتية'))
        الدعوات = bool(request.form.get('الدعوات'))
        الوثيقة_القياسية = bool(request.form.get('الوثيقة_القياسية'))
        التخويل = bool(request.form.get('التخويل'))
        لجان_الفتح = bool(request.form.get('لجان_الفتح'))

        if project_id and اسم_المشروع and الكلفة_الكلية:
            conn = get_db_connection()
            try:
                c = conn.cursor()
                c.execute("""
                    UPDATE projects 
                    SET المشروع = ?, المحافظة = ?, مدرج_في_وزارة_التخطيط = ?, 
                        مؤشر_لدى_وزارة_المالية = ?, الكلفة_الكلية = ?, الاستثناء_من_أساليب_التعاقد = ?, 
                        استثناء = ?, الإعلان = ?, تاريخ_غلق_الدعوات = ?, لجنة_تحليل = ?, 
                        قرار_لجنة_التحليل_الى_دائرة_العقود = ?, لجنة_المراجعة_والمصادقة = ?, 
                        الإحالة = ?, مسودة_العقد = ?, توقيع_العقد = ?, ملاحظات = ?, 
                        دراسة_سيرة_ذاتية = ?, الدعوات = ?, الوثيقة_القياسية = ?, التخويل = ?, لجان_الفتح = ?
                    WHERE id = ?
                """, (اسم_المشروع, المحافظة, مدرج_في_وزارة_التخطيط,
                      مؤشر_لدى_وزارة_المالية, الكلفة_الكلية, الاستثناء_من_أساليب_التعاقد,
                      استثناء, الإعلان, تاريخ_غلق_الدعوات, لجنة_تحليل,
                      قرار_لجنة_التحليل_الى_دائرة_العقود, لجنة_المراجعة_والمصادقة,
                      الإحالة, مسودة_العقد, توقيع_العقد, ملاحظات,
                      دراسة_سيرة_ذاتية, الدعوات, الوثيقة_القياسية, التخويل, لجان_الفتح,
                      project_id))
                conn.commit()
                flash("✅ تم تعديل المشروع بنجاح!", "success")
            except sqlite3.Error as e:
                flash(f"⚠️ خطأ في تعديل المشروع: {e}", "danger")
            finally:
                conn.close()
        else:
            flash("⚠️ جميع الحقول المطلوبة يجب أن تكون مملوءة.", "warning")

    return redirect(url_for('edit_project'))
@app.route('/reports', methods=['GET', 'POST'])
def reports():
    المشاريع = []

    if request.method == 'POST':
        اسم_المشروع = request.form.get('اسم_المشروع', '').strip()
        print(f"🔍 البحث عن المشروع: {اسم_المشروع}")

        if اسم_المشروع:
            conn = get_db_connection()
            try:
                c = conn.cursor()
                query = """
                    SELECT * FROM projects 
                    WHERE LOWER(TRIM(المشروع)) LIKE LOWER(?)
                """
                c.execute(query, ('%' + اسم_المشروع + '%',))
                المشاريع = c.fetchall()
                if not المشاريع:
                    print("⚠️ لا توجد نتائج مطابقة للبحث.")
                else:
                    print(f"✅ تم العثور على {len(المشاريع)} مشروع.")
            except sqlite3.Error as e:
                print(f"⚠️ خطأ في تنفيذ الاستعلام: {e}")
            finally:
                conn.close()

            المشاريع = [dict(مشروع) for مشروع in المشاريع]
    return render_template('reports.html', المشاريع=المشاريع)

@app.route('/reports1', methods=['GET', 'POST'])
def reports1():
    المشاريع = []

    if request.method == 'POST':
        المحافظة = request.form.get('المحافظة', '').strip()

        if المحافظة:
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("SELECT * FROM projects WHERE المحافظة = ?", (المحافظة,))
                المشاريع = c.fetchall()

                # طباعة عدد النتائج
                print(f"عدد النتائج: {len(المشاريع)}")
                if not المشاريع:
                    print("لا توجد نتائج.")

            except sqlite3.Error as e:
                print(f"Database error: {e}")
            finally:
                conn.close()

    return render_template('reports1.html', المشاريع=المشاريع)

# حذف مشروع
@app.route('/delete_project', methods=['GET', 'POST'])
def delete_project():
    if 'username' not in session:
        flash('يجب تسجيل الدخول أولاً!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        project_name = request.form.get('project_name', '').strip()

        if project_name:
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("SELECT * FROM projects WHERE المشروع = ?", (project_name,))
                project = c.fetchone()

                if project:
                    c.execute("DELETE FROM projects WHERE المشروع = ?", (project_name,))
                    conn.commit()
                    flash(f'تم حذف المشروع "{project_name}" بنجاح!', 'success')
                    return redirect(url_for('delete_project'))
                else:
                    flash(f'المشروع "{project_name}" غير موجود!', 'danger')
            except Exception as e:
                flash(f'حدث خطأ أثناء الحذف: {str(e)}', 'danger')
            finally:
                conn.close()
        else:
            flash('يرجى إدخال اسم المشروع!', 'danger')

    return render_template('delete_project.html')
@app.route('/upload_excel', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ملف غير موجود', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('يرجى اختيار ملف', 'danger')
            return redirect(request.url)

        try:
            # قراءة ملف Excel باستخدام Pandas
            df = pd.read_excel(file)

            # تحويل البيانات إلى قائمة من القواميس
            المشاريع = df.to_dict(orient='records')

            # تمرير البيانات إلى النموذج
            return render_template('your_template.html', المشاريع=المشاريع)
        except Exception as e:
            flash(f'حدث خطأ: {e}', 'danger')
            return redirect(request.url)

    return render_template('your_template.html')
import pandas as pd
from flask import Response, flash, redirect, url_for
from io import BytesIO

@app.route('/export_excel', methods=['GET'])
def export_excel():
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect('projects.db')

        # قراءة البيانات من الجدول
        df = pd.read_sql_query("SELECT * FROM projects", conn)

        # إغلاق الاتصال
        conn.close()

        # تصدير البيانات إلى ملف Excel
        output_file = 'projects.xlsx'
        df.to_excel(output_file, index=False, engine='openpyxl')

        # إرسال الملف للمستخدم
        return send_file(output_file, as_attachment=True)


# تشغيل التطبيق
if __name__ == '__main__':
    init_db()
    app.run(debug=True)