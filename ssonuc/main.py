from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import pandas as pd
import os
from werkzeug.utils import secure_filename
import config

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Excel dosyalarının saklanacağı dizin
EXCEL_FOLDER = "excel_files"
os.makedirs(EXCEL_FOLDER, exist_ok=True)

# Yönetici doğrulama işlemi
def is_admin_authenticated(password):
    return password == config.ADMIN_PASSWORD

# Öğrenci doğrulama fonksiyonu
def validate_student(student_id, tc_no, course):
    course_file = os.path.join(EXCEL_FOLDER, f"{course.lower()}.xlsx")
    if not os.path.exists(course_file):
        return None
    
    df = pd.read_excel(course_file)
    student_data = df[(df["StudentID"] == int(student_id)) & (df["TCNo"] == int(tc_no))]
    
    return student_data.iloc[0] if not student_data.empty else None

# Ana sayfa - Giriş Formu
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        student_id = request.form.get("student_id")
        tc_no = request.form.get("tc_no")
        course = request.form.get("course")
        
        if not student_id or not tc_no or not course:
            flash("Lütfen tüm alanları doldurun.")
            return redirect(url_for("index"))
        
        result = validate_student(student_id, tc_no, course)
        
        if result is not None:
            return render_template("result.html", student=result, course=course)
        else:
            flash("Öğrenci bilgileri yanlış.")
            return redirect(url_for("index"))
    
    courses = [f.replace(".xlsx", "").capitalize() for f in os.listdir(EXCEL_FOLDER) if f.endswith(".xlsx")]
    return render_template("index.html", courses=courses)

# Yönetici Giriş Sayfası
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        
        if is_admin_authenticated(password):
            return redirect(url_for("admin_panel"))
        else:
            flash("Yanlış şifre.")
            return redirect(url_for("admin_login"))
    
    return render_template("admin_login.html")

# Yönetici Paneli - Dosya Yükleme ve Silme
@app.route("/admin_panel", methods=["GET", "POST"])
def admin_panel():
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file.filename.endswith(".xlsx"):
                filename = secure_filename(file.filename)
                file.save(os.path.join(EXCEL_FOLDER, filename))
                flash(f"{filename} başarıyla yüklendi.")
            else:
                flash("Sadece .xlsx dosyaları yüklenebilir.")
        return redirect(url_for("admin_panel"))
    
    # Excel dosyalarını listele
    excel_files = os.listdir(EXCEL_FOLDER)
    return render_template("admin_panel.html", files=excel_files)

# Excel dosyası silme işlemi
@app.route("/delete_file/<filename>", methods=["POST"])
def delete_file(filename):
    file_path = os.path.join(EXCEL_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f"{filename} başarıyla silindi.")
    else:
        flash(f"{filename} bulunamadı.")
    return redirect(url_for("admin_panel"))

# Flask uygulamasını çalıştır
if __name__ == "__main__":
    app.run(debug=True)

