# =========================================================
#                  IMPORTS & DEPENDENCIES
# =========================================================
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    request,
    Response,
)
from flask_mysqldb import MySQL
import random
import MySQLdb
from MySQLdb import IntegrityError
import random
import smtplib
import socket
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
#                    FORM IMPORTS
# =========================================================
from institute_login_form import InstituteLoginForm
from institute_data_add_student_form import InstituteAddStudent
from institute_data_view_student_form import InstituteViewStudent
from institute_data_update_student_form import InstituteUpdateStudent
from final_update_student_form import FinalUpdateStudent
from institute_data_delete_student_form import InstituteDeleteStudent
from final_delete_student_form import FinalDeleteStudent
from institute_data_add_teacher_form import InstituteAddTeacher
from institute_data_view_teacher_form import InstituteViewTeacher
from institute_data_update_teacher_form import InstituteUpdateTeacher
from final_update_teacher_form import FinalUpdateTeacher
from institute_data_delete_teacher_form import InstituteDeleteTeacher
from final_delete_teacher_form import FinalDeleteTeacher
from teacher_login_form import TeacherLoginForm
from teacher_signup_otp_password import TeacherSignupForm
from teacher_forgot_password_form import TeacherForgotForm
from subject_notes import SubjectNotesForm
from select_class_by_teacher_form import SelectClassForm
from student_login_form import StudentLoginForm
from student_signup_otp_password import StudentSignupForm
from student_forgot_password_form import StudentForgotForm
from institute_add_notice_form import InstituteAddNotice
from institute_update_notice_form import UpdateNoticeSearchForm
from final_update_notice_form import FinalUpdateNoticeForm
from institute_delete_notice_form import DeleteNoticeSearchForm, ConfirmDeleteForm


# =========================================================
#                   APP INITIALIZATION
# =========================================================
app = Flask(__name__)
app.secret_key = "any-random-secret-key"

# =========================================================
#               DATABASE CONFIGURATION
# =========================================================
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Mohit@7894"
app.config["MYSQL_DB"] = "institute_db"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


# =========================================================
#                   EMAIL OTP FUNCTION
# =========================================================
def send_otp_email(to_email, otp):
    try:
        sender_email = "kmbbcetplus@gmail.com"
        app_password = "zywxldycqqqdzzzk"

        msg = MIMEText(
            f"""
        Dear User,

        Your One-Time Password (OTP) for verification is:

            {otp}

        This OTP is valid for 5 minutes.

        For security reasons:
        • Do not share this OTP with anyone.
        • Our team will never ask for your OTP.
        • If you did not request this OTP, please ignore this email.

        Thank you,
        College Authentication System , KMBBCET-plus
        """
        )

        msg["Subject"] = "Login Verification OTP (Valid for 5 Minutes)"

        msg["From"] = sender_email
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()

        return True  # success

    except socket.gaierror:
        return "Network error: Unable to connect to mail server."

    except smtplib.SMTPAuthenticationError:
        return "Email authentication failed. Check app password."

    except smtplib.SMTPException:
        return "SMTP error occurred while sending OTP."

    except Exception:
        return "Unexpected error occurred while sending OTP."


# =========================================================
#                     HOME ROUTE
# =========================================================
from datetime import datetime


@app.route("/")
def hello():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute(
        """
        SELECT * FROM notices 
        WHERE is_active = 1 
        ORDER BY created_at DESC
    """
    )

    notices = cursor.fetchall()
    now = datetime.now()

    cursor.close()

    return render_template("homepage.html", notices=notices, now=now)


@app.route("/about")
def about():
    return render_template("about.html")


# =========================================================
#                 LOGIN OPTION PAGE
# =========================================================
@app.route("/loginoption")
def loginoption():
    # Page to choose Student / Institute / Teacher login
    return render_template("loginoption.html")


# =========================================================
#                     STUDENT LOGIN
# =========================================================
@app.route("/studentlogin", methods=["GET", "POST"])
def student_login():

    form = StudentLoginForm()

    if form.validate_on_submit():

        regd_no = form.regd.data
        password = form.password.data

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM student_login WHERE regd_no=%s", (regd_no,))
        user = cur.fetchone()
        cur.close()

        # ✅ Check if user exists
        if user and check_password_hash(user["password"], password):
            session["student_logged_in"] = True
            session["student_regd"] = regd_no
            return redirect(url_for("student_data"))
        else:
            flash("Invalid Registration No or Password", "danger")

    return render_template("student_login.html", form=form)


# =========================================================
#                 STUDENT REGISTRATION
# =========================================================
@app.route("/student_signup", methods=["GET", "POST"])
def student_signup():

    form = StudentSignupForm()

    if request.method == "POST":

        # ---------------- STEP 1 ----------------
        if not session.get("signup_otp"):

            regd = form.regd.data
            email = form.email.data

            if not regd or not email:
                flash("Please enter Registration No and Email", "danger")
                return render_template("student_signup.html", form=form)

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cur.execute(
                "SELECT * FROM students WHERE regd_no=%s AND email=%s", (regd, email)
            )
            teacher = cur.fetchone()

            if not teacher:
                flash("Registration number or email not found!", "danger")
                cur.close()
                return render_template("student_signup.html", form=form)

            cur.execute("SELECT * FROM student_login WHERE regd_no=%s", (regd,))
            if cur.fetchone():
                flash("Account already exists. Please login.", "warning")
                cur.close()
                return redirect(url_for("student_login"))

            otp = str(random.randint(100000, 999999))

            session["signup_otp"] = otp
            session["signup_regd"] = regd
            session["signup_email"] = email
            session["otp_expiry"] = (datetime.utcnow() + timedelta(minutes=5)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            send_otp_email(email, otp)

            cur.close()

            flash("OTP sent successfully! Valid for 5 minutes.", "success")
            return redirect(url_for("student_signup"))

        # ---------------- STEP 2 ----------------
        elif not session.get("otp_verified"):

            entered_otp = form.otp.data

            if not entered_otp:
                flash("Please enter OTP", "danger")
                return redirect(url_for("student_signup"))

            expiry_time = datetime.strptime(
                session.get("otp_expiry"), "%Y-%m-%d %H:%M:%S"
            )

            if datetime.utcnow() > expiry_time:
                session.clear()
                flash("OTP expired! Please try again.", "danger")
                return redirect(url_for("student_signup"))

            if entered_otp == session.get("signup_otp"):
                session["otp_verified"] = True
                flash("OTP Verified Successfully!", "success")
            else:
                flash("Invalid OTP!", "danger")

            return redirect(url_for("student_signup"))

        # ---------------- STEP 3 ----------------
        elif session.get("otp_verified"):

            password = form.password.data
            confirm_password = form.confirm_password.data

            if not password or not confirm_password:
                flash("Please enter password fields", "danger")
                return redirect(url_for("student_signup"))

            if password != confirm_password:
                flash("Passwords do not match!", "danger")
                return redirect(url_for("student_signup"))

            cur = mysql.connection.cursor()

            hashed_password = generate_password_hash(password)

            cur.execute(
                "INSERT INTO student_login (regd_no, email, password) VALUES (%s, %s, %s)",
                (
                    session.get("signup_regd"),
                    session.get("signup_email"),
                    hashed_password,
                ),
            )

            mysql.connection.commit()
            cur.close()

            session.clear()
            flash("Account Created Successfully!", "success")
            return redirect(url_for("student_login"))

    return render_template("student_signup.html", form=form)


@app.route("/student_signup/start")
def student_signup_start():
    session.clear()
    return redirect(url_for("student_signup"))


# =========================================================
#               STUDENT FORGOT PASSWORD
# =========================================================
@app.route("/student_forgot_password", methods=["GET", "POST"])
def student_forgot_password():

    form = StudentForgotForm()

    if request.method == "POST":

        # ---------------- STEP 1: ENTER REGD ----------------
        if not session.get("fp_otp"):

            regd = form.regd.data

            if not regd:
                flash("Please enter Registration Number", "danger")
                return redirect(url_for("student_forgot_password"))

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cur.execute("SELECT email FROM students WHERE regd_no=%s", (regd,))
            student = cur.fetchone()

            if not student:
                flash("Registration number not found!", "danger")
                cur.close()
                return redirect(url_for("student_forgot_password"))

            email = student["email"]

            otp = str(random.randint(100000, 999999))

            session["fp_regd"] = regd
            session["fp_email"] = email
            session["fp_otp"] = otp
            session["fp_expiry"] = (datetime.utcnow() + timedelta(minutes=5)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            email_status = send_otp_email(email, otp)

            if email_status != True:
                flash(email_status, "danger")
                session.clear()
                return redirect(url_for("student_forgot_password"))

            flash("OTP sent to your registered email.", "success")
            cur.close()
            return redirect(url_for("student_forgot_password"))

        # ---------------- STEP 2: VERIFY OTP ----------------
        elif not session.get("fp_verified"):

            entered_otp = form.otp.data

            expiry = datetime.strptime(session["fp_expiry"], "%Y-%m-%d %H:%M:%S")

            if datetime.utcnow() > expiry:
                session.clear()
                flash("OTP expired! Try again.", "danger")
                return redirect(url_for("student_forgot_password"))

            if entered_otp == session.get("fp_otp"):
                session["fp_verified"] = True
                flash("OTP Verified Successfully!", "success")
            else:
                flash("Invalid OTP!", "danger")

            return redirect(url_for("student_forgot_password"))

        # ---------------- STEP 3: RESET PASSWORD ----------------
        elif session.get("fp_verified"):

            password = form.password.data
            confirm_password = form.confirm_password.data

            if not password or not confirm_password:
                flash("Please fill all password fields", "danger")
                return redirect(url_for("teacher_forgot_password"))

            if password != confirm_password:
                flash("Passwords do not match!", "danger")
                return redirect(url_for("teacher_forgot_password"))

            hashed_password = generate_password_hash(password)

            cur = mysql.connection.cursor()

            cur.execute(
                "UPDATE student_login SET password=%s WHERE regd_no=%s",
                (hashed_password, session["fp_regd"]),
            )

            mysql.connection.commit()
            cur.close()

            session.clear()
            flash("Password updated successfully! Please login.", "success")
            return redirect(url_for("student_login"))

    return render_template("student_forgot_password.html", form=form)


@app.route("/student_forgot_password/start")
def student_forgot_password_start():
    session.clear()
    return redirect(url_for("student_forgot_password"))


# =========================================================
#               STUDENT DATA (DYNAMIC)
# =========================================================
@app.route("/student_data")
def student_data():

    # Check student login
    if not session.get("student_logged_in"):
        flash("Please login first!", "danger")
        return redirect(url_for("student_login"))

    regd_no = session.get("student_regd")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM students WHERE regd_no=%s", (regd_no,))
    student = cur.fetchone()
    print(student)

    cur.close()

    if not student:
        flash("Student data not found!", "danger")
        return redirect(url_for("studet_login"))

    return render_template("student_data.html", student=student)


@app.route("/student_subjects", methods=["GET", "POST"])
def student_subjects():

    subjects = []
    student = None

    if request.method == "POST":

        regd_no = request.form.get("regd_no")

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # get student info
        cur.execute(
            "SELECT regd_no, name, branch, year FROM students WHERE regd_no=%s",
            (regd_no,),
        )
        student = cur.fetchone()

        if student:

            branch = student["branch"]
            year = student["year"]

            # get subjects of that class
            cur.execute(
                """
            SELECT subject_id, subject_name, subject_code
            FROM subjects
            WHERE branch=%s AND year=%s
            """,
                (branch, year),
            )

            subjects = cur.fetchall()

        else:
            flash("Registration number not found!", "danger")

        cur.close()

    return render_template("student_subjects.html", subjects=subjects, student=student)


@app.route("/student_subjects_for_exam", methods=["GET", "POST"])
def student_subjects_for_exam():

    subjects = []
    student = None

    if request.method == "POST":

        regd_no = request.form.get("regd_no")

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # get student info
        cur.execute(
            "SELECT regd_no, name, branch, year FROM students WHERE regd_no=%s",
            (regd_no,),
        )
        student = cur.fetchone()

        if student:

            branch = student["branch"]
            year = student["year"]

            # get subjects of that class
            cur.execute(
                """
            SELECT subject_id, subject_name, subject_code
            FROM subjects
            WHERE branch=%s AND year=%s
            """,
                (branch, year),
            )

            subjects = cur.fetchall()

        else:
            flash("Registration number not found!", "danger")

        cur.close()

    return render_template(
        "student_subjects_for_exam.html", subjects=subjects, student=student
    )


@app.route("/student_attendance/<int:subject_id>")
def student_attendance(subject_id):

    regd_no = request.args.get("regd_no")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get subject name
    cur.execute("SELECT subject_name FROM subjects WHERE subject_id=%s", (subject_id,))
    subject = cur.fetchone()

    # Get attendance records
    cur.execute(
        """
    SELECT attendance_date, status
    FROM attendance
    WHERE subject_id=%s AND regd_no=%s
    ORDER BY attendance_date
    """,
        (subject_id, regd_no),
    )

    records = cur.fetchall()

    # Total classes conducted
    # Total classes conducted
    cur.execute(
        """
    SELECT COUNT(DISTINCT attendance_date) AS total_classes
    FROM attendance
    WHERE subject_id=%s
    """,
        (subject_id,),
    )

    total_classes = cur.fetchone()["total_classes"]

    # Student present count
    cur.execute(
        """
    SELECT COUNT(*) AS present_count
    FROM attendance
    WHERE subject_id=%s AND regd_no=%s AND status='Present'
    """,
        (subject_id, regd_no),
    )

    present = cur.fetchone()["present_count"]

    cur.close()

    percentage = 0

    if total_classes > 0:
        percentage = round((present / total_classes) * 100, 2)

    return render_template(
        "student_attendance.html",
        subject=subject,
        records=records,
        total_classes=total_classes,
        present=present,
        percentage=percentage,
        regd_no=regd_no,
    )


@app.route("/student_marks_view/<int:subject_id>/<regd_no>")
def student_marks_view(subject_id, regd_no):

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get student
    cur.execute("SELECT * FROM students WHERE regd_no=%s", (regd_no,))
    student = cur.fetchone()

    # Get subject
    cur.execute("SELECT * FROM subjects WHERE subject_id=%s", (subject_id,))
    subject = cur.fetchone()

    # Get marks
    cur.execute(
        """
    SELECT 
        e.exam_name,
        m.marks_obtained,
        30 AS total_marks
    FROM internal_marks m
    JOIN exams e ON m.exam_id = e.id
    WHERE m.regd_no = %s AND m.subject_id = %s
    """,
        (regd_no, subject_id),
    )
    records = cur.fetchall()

    # Calculate totals
    total_obtained = sum(r["marks_obtained"] for r in records)
    total_marks = sum(r["total_marks"] for r in records)

    percentage = 0
    if total_marks > 0:
        percentage = round((total_obtained / total_marks) * 100, 2)

    cur.close()

    return render_template(
        "student_marks_view.html",
        subject=subject,
        records=records,
        total_obtained=total_obtained,
        total_marks=total_marks,
        percentage=percentage,
    )


# =========================================================
#               STUDENT ID CARD (DYNAMIC)
# =========================================================


@app.route("/student_id_card/<int:student_id>")
def student_id_card(student_id):

    regd_no = session.get("student_regd")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM students WHERE regd_no=%s", (regd_no,))
    student = cur.fetchone()

    cur.close()

    if not student:
        flash("student data not found!", "danger")
        return redirect(url_for("student_login"))

    return render_template("student_id_card.html", student=student)


# =========================================================
#                     TEACHER LOGIN
# =========================================================
@app.route("/teacherlogin", methods=["GET", "POST"])
def teacher_login():

    form = TeacherLoginForm()

    if form.validate_on_submit():

        regd_no = form.regd.data
        password = form.password.data

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM teacher_login WHERE regd_no=%s", (regd_no,))
        user = cur.fetchone()

        cur.execute("SELECT * FROM teachers WHERE regd_no=%s", (regd_no,))
        teacher = cur.fetchone()
        cur.close()

        # ✅ Check if user exists
        if user and check_password_hash(user["password"], password):
            session["teacher_logged_in"] = True
            session["teacher_regd"] = regd_no
            session["teacher_name"] = teacher["full_name"]
            return redirect(url_for("teacher_data"))
        else:
            flash("Invalid Registration No or Password", "danger")

    return render_template("teacher_login.html", form=form)


# =========================================================
#                 TEACHER REGISTRATION
# =========================================================


@app.route("/teacher_signup", methods=["GET", "POST"])
def teacher_signup():

    form = TeacherSignupForm()

    if request.method == "POST":

        # ---------------- STEP 1 ----------------
        if not session.get("signup_otp"):

            regd = form.regd.data
            email = form.email.data

            if not regd or not email:
                flash("Please enter Registration No and Email", "danger")
                return render_template("teacher_signup.html", form=form)

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cur.execute(
                "SELECT * FROM teachers WHERE regd_no=%s AND email=%s", (regd, email)
            )
            teacher = cur.fetchone()

            if not teacher:
                flash("Registration number or email not found!", "danger")
                cur.close()
                return render_template("teacher_signup.html", form=form)

            cur.execute("SELECT * FROM teacher_login WHERE regd_no=%s", (regd,))
            if cur.fetchone():
                flash("Account already exists. Please login.", "warning")
                cur.close()
                return redirect(url_for("teacher_login"))

            otp = str(random.randint(100000, 999999))

            session["signup_otp"] = otp
            session["signup_regd"] = regd
            session["signup_email"] = email
            session["otp_expiry"] = (datetime.utcnow() + timedelta(minutes=5)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            send_otp_email(email, otp)

            cur.close()

            flash("OTP sent successfully! Valid for 5 minutes.", "success")
            return redirect(url_for("teacher_signup"))

        # ---------------- STEP 2 ----------------
        elif not session.get("otp_verified"):

            entered_otp = form.otp.data

            if not entered_otp:
                flash("Please enter OTP", "danger")
                return redirect(url_for("teacher_signup"))

            expiry_time = datetime.strptime(
                session.get("otp_expiry"), "%Y-%m-%d %H:%M:%S"
            )

            if datetime.utcnow() > expiry_time:
                session.clear()
                flash("OTP expired! Please try again.", "danger")
                return redirect(url_for("teacher_signup"))

            if entered_otp == session.get("signup_otp"):
                session["otp_verified"] = True
                flash("OTP Verified Successfully!", "success")
            else:
                flash("Invalid OTP!", "danger")

            return redirect(url_for("teacher_signup"))

        # ---------------- STEP 3 ----------------
        elif session.get("otp_verified"):

            password = form.password.data
            confirm_password = form.confirm_password.data

            if not password or not confirm_password:
                flash("Please enter password fields", "danger")
                return redirect(url_for("teacher_signup"))

            if password != confirm_password:
                flash("Passwords do not match!", "danger")
                return redirect(url_for("teacher_signup"))

            cur = mysql.connection.cursor()

            hashed_password = generate_password_hash(password)

            cur.execute(
                "INSERT INTO teacher_login (regd_no, email, password) VALUES (%s, %s, %s)",
                (
                    session.get("signup_regd"),
                    session.get("signup_email"),
                    hashed_password,
                ),
            )

            mysql.connection.commit()
            cur.close()

            session.clear()
            flash("Account Created Successfully!", "success")
            return redirect(url_for("teacher_login"))

    return render_template("teacher_signup.html", form=form)


@app.route("/clear")
def clear():
    session.clear()
    return "Session Cleared"


@app.route("/teacher_signup/start")
def teacher_signup_start():
    session.clear()
    return redirect(url_for("teacher_signup"))


# =========================================================
#               TEACHER FORGOT PASSWORD
# =========================================================


@app.route("/teacher_forgot_password", methods=["GET", "POST"])
def teacher_forgot_password():

    form = TeacherForgotForm()

    if request.method == "POST":

        # ---------------- STEP 1: ENTER REGD ----------------
        if not session.get("fp_otp"):

            regd = form.regd.data

            if not regd:
                flash("Please enter Registration Number", "danger")
                return redirect(url_for("teacher_forgot_password"))

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cur.execute("SELECT email FROM teachers WHERE regd_no=%s", (regd,))
            teacher = cur.fetchone()

            if not teacher:
                flash("Registration number not found!", "danger")
                cur.close()
                return redirect(url_for("teacher_forgot_password"))

            email = teacher["email"]

            otp = str(random.randint(100000, 999999))

            session["fp_regd"] = regd
            session["fp_email"] = email
            session["fp_otp"] = otp
            session["fp_expiry"] = (datetime.utcnow() + timedelta(minutes=5)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            email_status = send_otp_email(email, otp)

            if email_status != True:
                flash(email_status, "danger")
                session.clear()
                return redirect(url_for("teacher_forgot_password"))

            flash("OTP sent to your registered email.", "success")
            cur.close()
            return redirect(url_for("teacher_forgot_password"))

        # ---------------- STEP 2: VERIFY OTP ----------------
        elif not session.get("fp_verified"):

            entered_otp = form.otp.data

            expiry = datetime.strptime(session["fp_expiry"], "%Y-%m-%d %H:%M:%S")

            if datetime.utcnow() > expiry:
                session.clear()
                flash("OTP expired! Try again.", "danger")
                return redirect(url_for("teacher_forgot_password"))

            if entered_otp == session.get("fp_otp"):
                session["fp_verified"] = True
                flash("OTP Verified Successfully!", "success")
            else:
                flash("Invalid OTP!", "danger")

            return redirect(url_for("teacher_forgot_password"))

        # ---------------- STEP 3: RESET PASSWORD ----------------
        elif session.get("fp_verified"):

            password = form.password.data
            confirm_password = form.confirm_password.data

            if not password or not confirm_password:
                flash("Please fill all password fields", "danger")
                return redirect(url_for("teacher_forgot_password"))

            if password != confirm_password:
                flash("Passwords do not match!", "danger")
                return redirect(url_for("teacher_forgot_password"))

            hashed_password = generate_password_hash(password)

            cur = mysql.connection.cursor()

            cur.execute(
                "UPDATE teacher_login SET password=%s WHERE regd_no=%s",
                (hashed_password, session["fp_regd"]),
            )

            mysql.connection.commit()
            cur.close()

            session.clear()
            flash("Password updated successfully! Please login.", "success")
            return redirect(url_for("teacher_login"))

    return render_template("teacher_forgot_password.html", form=form)


@app.route("/teacher_forgot_password/start")
def teacher_forgot_password_start():
    session.clear()
    return redirect(url_for("teacher_forgot_password"))


# =========================================================
#               TEACHER DATA (DYNAMIC)
# =========================================================


@app.route("/teacher_data")
def teacher_data():

    # Check teacher login
    if not session.get("teacher_logged_in"):
        flash("Please login first!", "danger")
        return redirect(url_for("teacher_login"))

    regd_no = session.get("teacher_regd")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM teachers WHERE regd_no=%s", (regd_no,))
    teacher = cur.fetchone()

    cur.close()

    if not teacher:
        flash("Teacher data not found!", "danger")
        return redirect(url_for("teacher_login"))

    return render_template("teacher_data.html", teacher=teacher)


@app.route("/select_class_by_teacher", methods=["GET", "POST"])
def select_class_by_teacher():
    if not session.get("teacher_logged_in"):
        flash("Please login first!", "danger")
        return redirect(url_for("teacher_login"))

    form = SelectClassForm(request.form)
    subjects = []

    if request.method == "POST":
        year = request.form.get("year")
        branch = request.form.get("branch")

        if year and branch:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(
                """
                SELECT subject_id, subject_name, subject_code, branch, year
                FROM subjects
                WHERE year=%s AND branch=%s
            """,
                (year, branch),
            )
            subjects = cur.fetchall()  # ✅ This will be a list of dictionaries
            cur.close()

            if not subjects:
                flash("No subjects found for this class.", "danger")

    return render_template("select_class_by_teacher.html", form=form, subjects=subjects)


@app.route("/verify_subject_password", methods=["POST"])
def verify_subject_password():
    subject_id = request.form.get("subject_id")
    password = request.form.get("password")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM subjects WHERE subject_id=%s", (subject_id,))
    subject = cur.fetchone()
    cur.close()

    if subject and subject["password"] == password:
        return redirect(url_for("attendance_option", subject_id=subject_id))
    else:
        flash("Incorrect subject password!", "danger")
        return redirect(url_for("select_class_by_teacher"))


@app.route("/select_exam_by_teacher", methods=["GET", "POST"])
def select_exam_by_teacher():

    if not session.get("teacher_logged_in"):
        flash("Please login first!", "danger")
        return redirect(url_for("teacher_login"))

    form = SelectClassForm(request.form)
    exams = []

    if request.method == "POST":

        year = request.form.get("year")
        branch = request.form.get("branch")

        # Branch name → branch_id mapping
        branch_map = {"CSE": 1, "ECE": 2, "EE": 3, "ME": 4, "CE": 5}

        branch_id = branch_map.get(branch)

        if year and branch_id:

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cur.execute(
                """
                SELECT e.id, e.exam_name, e.year_id, b.branch_name
                FROM exams e
                JOIN branches b ON e.branch_id = b.id
                WHERE e.year_id=%s AND e.branch_id=%s
            """,
                (year, branch_id),
            )

            exams = cur.fetchall()
            print(exams)
            cur.close()

            if not exams:
                flash("No exams found for this class.", "danger")

    return render_template("select_exam_by_teacher.html", form=form, exams=exams)


@app.route("/verify_exam_password", methods=["POST"])
def verify_exam_password():

    exam_id = request.form.get("exam_id")
    password = request.form.get("password")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM exams WHERE id=%s", (exam_id,))
    exam = cur.fetchone()

    cur.close()

    if exam and exam["exam_password"] == password:

        # store exam data in session
        session["exam_id"] = exam_id
        session["year_id"] = exam["year_id"]
        session["branch_id"] = exam["branch_id"]

        return redirect(url_for("internal_subjects"))

    else:
        flash("Incorrect exam password!", "danger")
        return redirect(url_for("select_exam_by_teacher"))


@app.route("/internal_subjects")
def internal_subjects():

    year_id = session.get("year_id")
    branch_id = session.get("branch_id")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # get branch name
    cur.execute("SELECT branch_name FROM branches WHERE id=%s", (branch_id,))
    branch = cur.fetchone()["branch_name"]

    # get year name
    cur.execute("SELECT year_name FROM years WHERE id=%s", (year_id,))
    year = cur.fetchone()["year_name"]

    # fetch subjects
    cur.execute(
        """
        SELECT subject_id, subject_name
        FROM subjects
        WHERE branch=%s AND year=%s
        """,
        (branch, year),
    )

    subjects = cur.fetchall()
    cur.close()

    return render_template(
        "internal_subjects.html", subjects=subjects, year=year, branch=branch
    )


# =========================================================
#               TEACHER ATTENDANCE
# =========================================================
@app.route("/attendance_option/<int:subject_id>")
def attendance_option(subject_id):

    session["subject_id"] = subject_id  # ⭐ STORE SUBJECT ID
    print("Stored subject id:", subject_id)

    return render_template("attendance_option.html", subject_id=subject_id)


@app.route("/view_attendance", methods=["GET", "POST"])
def view_attendance():

    if "subject_id" not in session:
        flash("Subject not selected", "danger")
        return redirect(url_for("select_class_by_teacher"))

    subject_id = session["subject_id"]

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get subject details
    cur.execute(
        "SELECT subject_name, branch, year FROM subjects WHERE subject_id=%s",
        (subject_id,),
    )
    subject = cur.fetchone()

    branch = subject["branch"]
    year = subject["year"]

    students = None

    if request.method == "POST":

        from_date = request.form.get("from_date")
        to_date = request.form.get("to_date")

        if datetime.strptime(to_date, "%Y-%m-%d").date() > date.today():
            flash("Future date is not allowed", "danger")
            return redirect(url_for("view_attendance"))

        cur.execute(
            """
        SELECT 
            s.student_id,
            s.regd_no,
            s.name,

            tc.total_classes,

            SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS total_present,

            ROUND(
                (SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) /
                NULLIF(tc.total_classes,0)) * 100,2
            ) AS percentage

        FROM students s

        LEFT JOIN attendance a
        ON s.regd_no = a.regd_no
        AND a.subject_id = %s
        AND a.attendance_date BETWEEN %s AND %s

        JOIN (
            SELECT COUNT(DISTINCT attendance_date) AS total_classes
            FROM attendance
            WHERE subject_id = %s
            AND attendance_date BETWEEN %s AND %s
        ) tc

        WHERE s.branch = %s
        AND s.year = %s

        GROUP BY s.student_id, s.regd_no, s.name, tc.total_classes

        ORDER BY s.regd_no
        """,
            (
                subject_id,
                from_date,
                to_date,
                subject_id,
                from_date,
                to_date,
                branch,
                year,
            ),
        )

        students = cur.fetchall()

    cur.close()

    return render_template(
        "view_attendance.html", students=students, subject=subject, today=date.today()
    )


@app.route("/take_attendance/<int:subject_id>", methods=["GET", "POST"])
def take_attendance(subject_id):

    if not session.get("teacher_logged_in"):
        flash("Please login first!", "danger")
        return redirect(url_for("teacher_login"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM subjects WHERE subject_id=%s", (subject_id,))
    subject = cur.fetchone()

    branch = subject["branch"]
    year = subject["year"]
    subject_name = subject["subject_name"]

    cur.execute(
        "SELECT student_id, regd_no, name FROM students WHERE branch=%s AND year=%s ORDER BY regd_no ASC",
        (branch, year),
    )
    students = cur.fetchall()

    # ✅ POST SECTION
    if request.method == "POST":

        teacher_name = session.get("teacher_name")

        # define attendance_date first
        attendance_date = request.form.get("attendance_date")

        if not attendance_date:
            flash("Please select date!", "danger")
            return redirect(request.url)

        # check duplicate attendance
        cur.execute(
            """
        SELECT 1 FROM attendance
        WHERE subject_id=%s AND attendance_date=%s
        """,
            (subject_id, attendance_date),
        )

        existing = cur.fetchone()

        if existing:
            flash(f"Attendance already taken for {attendance_date}", "warning")
            return redirect(request.url)

        for student in students:
            regd_no = student["regd_no"]
            status = request.form.get(f"status_{regd_no}")

            if not status:
                flash(f"Please mark attendance for {regd_no}", "danger")
                return redirect(request.url)

            cur.execute(
                """
            INSERT INTO attendance
            (regd_no, subject_id, attendance_date, status, teacher_name)
            VALUES (%s,%s,%s,%s,%s)
            """,
                (regd_no, subject_id, attendance_date, status, teacher_name),
            )

        mysql.connection.commit()

        flash("Attendance recorded successfully!", "success")
        return redirect(request.url)

    cur.close()

    return render_template(
        "take_attendance.html",
        students=students,
        subject_name=subject_name,
        year=year,
        total_students=len(students),
        today=date.today(),
        branch=branch,
    )


@app.route("/update_attendance", methods=["GET", "POST"])
def update_attendance():

    attendance = None
    subject_id = session.get("subject_id")
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM subjects WHERE subject_id=%s", (subject_id,))
    subject = cur.fetchone()

    if subject:
        session["subject_name"] = subject["subject_name"]

    if request.method == "POST":

        regd_no = request.form.get("regd_no")
        attendance_date = request.form.get("attendance_date")

        # ✅ BLOCK FUTURE DATE
        today = date.today()
        selected_date = datetime.strptime(attendance_date, "%Y-%m-%d").date()

        if selected_date > today:
            flash("Future date is not allowed!", "danger")
            return redirect(url_for("update_attendance"))

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute(
            """
        SELECT a.attendance_id,
            a.regd_no,
            a.attendance_date,
            a.status,
            s.student_id
        FROM attendance a
        JOIN students s ON a.regd_no = s.regd_no
        WHERE a.regd_no=%s 
        AND a.attendance_date=%s
        AND a.subject_id=%s
        """,
            (regd_no, attendance_date, subject_id),
        )

        attendance = cur.fetchone()

        cur.close()

        if not attendance:
            flash("Attendance record not found", "danger")

    return render_template(
        "update_attendance.html",
        attendance=attendance,
        current_date=date.today().strftime("%Y-%m-%d"),  # for frontend max
    )


@app.route("/update_status", methods=["POST"])
def update_status():

    attendance_id = request.form["attendance_id"]
    status = request.form["status"]

    cur = mysql.connection.cursor()

    cur.execute(
        """
    UPDATE attendance
    SET status=%s
    WHERE attendance_id=%s
    """,
        (status, attendance_id),
    )

    mysql.connection.commit()
    cur.close()

    flash("Attendance updated successfully", "success")

    return redirect(url_for("update_attendance"))


# =========================================================
#               TEACHER MARKS
# =========================================================


@app.route("/teacher_marks")
def teacher_marks():
    return "Marks Page"


@app.route("/view_marks/<int:subject_id>")
def view_marks(subject_id):

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    exam_id = session.get("exam_id")

    # Get subject information
    cur.execute(
        "SELECT subject_name, branch, year FROM subjects WHERE subject_id=%s",
        (subject_id,),
    )
    subject = cur.fetchone()

    branch = subject["branch"]
    year = subject["year"]

    # Get students and their marks
    cur.execute(
        """
    SELECT 
        students.student_id,
        students.regd_no,
        students.name,
        internal_marks.marks_obtained

    FROM students

    LEFT JOIN internal_marks
        ON students.regd_no = internal_marks.regd_no
        AND internal_marks.subject_id = %s
        AND internal_marks.exam_id = %s

    WHERE students.branch = %s
    AND students.year = %s
    """,
        (subject_id, exam_id, branch, year),
    )

    students = cur.fetchall()

    cur.close()

    return render_template(
        "view_marks.html",
        students=students,
        total_students=len(students),
        subject_name=subject["subject_name"],
        branch=branch,
        year=year,
    )


@app.route("/enter_internal_marks/<int:subject_id>", methods=["GET", "POST"])
def enter_internal_marks(subject_id):

    if not session.get("teacher_logged_in"):
        flash("Please login first!", "danger")
        return redirect(url_for("teacher_login"))

    exam_id = session.get("exam_id")

    if not exam_id:
        flash("Exam session expired!", "danger")
        return redirect(url_for("teacher_dashboard"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # get subject
    cur.execute("SELECT * FROM subjects WHERE subject_id=%s", (subject_id,))
    subject = cur.fetchone()

    if not subject:
        flash("Invalid subject!", "danger")
        cur.close()
        return redirect(url_for("teacher_dashboard"))

    branch = subject["branch"]
    year = subject["year"]
    subject_name = subject["subject_name"]

    # 🔒 CHECK IF MARKS ALREADY SUBMITTED
    cur.execute(
        """
    SELECT COUNT(*) AS total
    FROM internal_marks
    WHERE subject_id=%s AND exam_id=%s
    """,
        (subject_id, exam_id),
    )

    result = cur.fetchone()

    if result["total"] > 0:
        flash("Marks already submitted for this internal exam.", "warning")
        cur.close()
        return redirect(url_for("internal_subjects"))

    # get students
    cur.execute(
        """
    SELECT student_id, regd_no, name
    FROM students
    WHERE branch=%s AND year=%s
    ORDER BY regd_no ASC
    """,
        (branch, year),
    )

    students = cur.fetchall()

    if request.method == "POST":

        teacher_name = session.get("teacher_name")

        for student in students:

            regd_no = student["regd_no"]
            marks = request.form.get(f"marks_{regd_no}")

            if not marks:
                flash(f"Enter marks for {regd_no}", "danger")
                cur.close()
                return redirect(request.url)

            if not marks.isdigit():
                flash(f"Invalid marks for {regd_no}", "danger")
                cur.close()
                return redirect(request.url)

            marks = int(marks)

            if marks < 0 or marks > 30:
                flash(f"Marks must be between 0 and 30 for {regd_no}", "danger")
                cur.close()
                return redirect(request.url)

            cur.execute(
                """
            INSERT INTO internal_marks
            (regd_no, subject_id, exam_id, marks_obtained, teacher_name)
            VALUES (%s,%s,%s,%s,%s)
            """,
                (regd_no, subject_id, exam_id, marks, teacher_name),
            )

        mysql.connection.commit()
        cur.close()

        flash("Marks submitted successfully!", "success")
        return redirect(url_for("internal_subjects"))

    cur.close()

    return render_template(
        "enter_internal_marks.html",
        students=students,
        subject_name=subject_name,
        year=year,
        total_students=len(students),
        branch=branch,
    )


# =========================================================
#               TEACHER ADD NOTES
# =========================================================
@app.route("/add_subject_notes", methods=["GET", "POST"])
def add_subject_notes():

    # 🔒 Check if teacher is logged in
    if "teacher_regd" not in session:
        flash("Please login first!", "danger")
        return redirect(url_for("teacher_login"))

    form = SubjectNotesForm()

    if form.validate_on_submit():
        print("Form Validated ✅")

        try:
            cur = mysql.connection.cursor()

            insert_query = """
                INSERT INTO subject_notes
                (branch, year, subject_name, chapter_name,
                 summary, uploaded_by_name, uploaded_by_id,
                 notes_link)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            cur.execute(
                insert_query,
                (
                    form.branch.data,
                    form.year.data,
                    form.subject_name.data,
                    form.chapter_name.data,
                    form.summary.data,
                    session["teacher_name"],  # ✅ Auto from session
                    session["teacher_regd"],  # ✅ Auto from session
                    form.notes_link.data,
                ),
            )

            mysql.connection.commit()
            cur.close()

            flash("Subject Notes Added Successfully!", "success")
            return redirect(url_for("add_subject_notes"))

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    else:
        print("Form not validate")
    return render_template("add_subject_notes.html", form=form)


# =========================================================
#               TEACHER / STUDENT VIEW NOTES
# =========================================================
@app.route("/view_subject_notes", methods=["GET"])
def view_subject_notes():

    search_query = request.args.get("search")

    cur = mysql.connection.cursor()

    if search_query:
        query = """
            SELECT * FROM subject_notes
            WHERE subject_name LIKE %s
            ORDER BY id DESC
        """
        cur.execute(query, (f"%{search_query}%",))
    else:
        query = """
            SELECT * FROM subject_notes
            ORDER BY id DESC
        """
        cur.execute(query)

    notes = cur.fetchall()

    cur.close()

    return render_template("view_subject_notes.html", notes=notes)


# =========================================================
#               TEACHER ID CARD (DYNAMIC)
# =========================================================


@app.route("/teacher_id_card/<int:teacher_id>")
def teacher_id_card(teacher_id):

    regd_no = session.get("teacher_regd")

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM teachers WHERE regd_no=%s", (regd_no,))
    teacher = cur.fetchone()

    cur.close()

    if not teacher:
        flash("Teacher data not found!", "danger")
        return redirect(url_for("teacher_login"))

    return render_template("teacher_id_card.html", teacher=teacher)


# =========================================================
#                    INSTITUTE LOGIN
# =========================================================
@app.route("/institutelogin", methods=["GET", "POST"])
def institute_login():
    form = InstituteLoginForm()

    # Validate institute credentials
    if form.validate_on_submit():
        regd_no = form.regd.data
        password = form.password.data

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM institute_login WHERE regd_no=%s AND password=%s",
            (regd_no, password),
        )
        institute = cur.fetchone()
        cur.close()

        if institute:
            return redirect(url_for("institute_data"))
        else:
            flash("Invalid Registration No or Password", "danger")

    return render_template("institute_login.html", form=form)


@app.route("/institutedata")
def institute_data():
    return render_template("institute_data.html")


# =========================================================
#              INSTITUTE ADD STUDENT MODULE
# =========================================================
@app.route("/institute_add_student", methods=["GET", "POST"])
def institute_add_student():
    form = InstituteAddStudent()

    # Insert student data into database
    if form.validate_on_submit():
        cur = mysql.connection.cursor()

        try:
            # Read image file only once
            photo_file = form.photo.data
            photo_data = photo_file.read()
            photo_type = photo_file.mimetype

            cur.execute(
                """INSERT INTO students
                (name, regd_no, aadhaar, email, phone, gender, dob, branch, year, photo, photo_type,blood_group,address)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    form.student_name.data,
                    form.regd_no.data,
                    form.aadhaar.data,
                    form.email.data,
                    form.phone.data,
                    form.gender.data,
                    form.dob.data,
                    form.branch.data,
                    int(form.year.data),
                    photo_data,
                    photo_type,
                    form.blood_group.data,
                    form.address.data,
                ),
            )

            mysql.connection.commit()
            flash("Student added successfully!", "success")
            return redirect(url_for("institute_add_student"))

        # Handle duplicate / constraint errors
        except IntegrityError as e:
            mysql.connection.rollback()
            error = str(e)

            if "regd_no" in error:
                flash("Registration number already exists", "danger")
            elif "aadhaar" in error:
                flash("Aadhaar number already exists", "danger")
            elif "email" in error:
                flash("Email already exists", "danger")
            else:
                flash("Database constraint violation", "danger")

        finally:
            cur.close()

    return render_template("institute_add_student.html", form=form)


# =========================================================
#              INSTITUTE VIEW STUDENT MODULE
# =========================================================
@app.route("/institute_view_student", methods=["GET", "POST"])
def institute_view_student():
    form = InstituteViewStudent()
    students = []
    searched = False

    if form.validate_on_submit():
        searched = True
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Start query
        query = "SELECT * FROM students WHERE 1=1"
        params = []

        if form.regd_no.data:
            query += " AND regd_no = %s"
            params.append(form.regd_no.data)

        if form.name.data:
            query += " AND name LIKE %s"
            params.append("%" + form.name.data + "%")

        if form.year.data:
            query += " AND year = %s"
            params.append(form.year.data)

        if form.branch.data:
            query += " AND branch = %s"
            params.append(form.branch.data)

        if not params:
            flash("Please enter at least one search criteria", "warning")
            cur.close()
            return render_template(
                "institute_view_student.html",
                form=form,
                students=students,
                searched=False,
            )

        # ✅ Add ORDER BY at the END
        query += " ORDER BY regd_no ASC"

        cur.execute(query, tuple(params))
        students = cur.fetchall()
        cur.close()

        # if not students:
        #     flash("No student record found", "warning")

    return render_template(
        "institute_view_student.html", form=form, students=students, searched=searched
    )


# =========================================================
#              STUDENT PHOTO DISPLAY ROUTE
# =========================================================
@app.route("/student_photo/<int:student_id>")
def student_photo(student_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch student image from database
    cur.execute(
        "SELECT photo, photo_type FROM students WHERE student_id = %s", (student_id,)
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        return "", 404

    return Response(row["photo"], mimetype=row["photo_type"])


# =========================================================
#              INSTITUTE UPDATE STUDENT MODULE
# =========================================================
@app.route("/institute_update_student", methods=["GET", "POST"])
def institute_update_student():
    form = InstituteUpdateStudent()
    students = []  # Stores fetched student records
    searched = False  # Indicates whether search was performed

    if form.validate_on_submit():
        searched = True
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Build query dynamically based on input
        query = "SELECT * FROM students WHERE 1=1"
        params = []

        if form.regd_no.data:
            query += " AND regd_no = %s"
            params.append(form.regd_no.data)

        if form.name.data:
            query += " AND name LIKE %s"
            params.append("%" + form.name.data + "%")

        # If no input, you can either fetch all students or show a message
        if not params:
            flash("Please enter at least one search criteria", "warning")
            cur.close()
            return render_template(
                "institute_update_student.html",
                form=form,
                students=students,
                searched=False,
            )

        # Execute the query
        cur.execute(query, tuple(params))
        students = cur.fetchall()
        cur.close()

        if not students:
            flash("No student record found", "warning")

    return render_template(
        "institute_update_student.html", form=form, students=students, searched=searched
    )


@app.route("/final_update_student/<regd_no>", methods=["GET", "POST"])
def final_update_student(regd_no):

    form = FinalUpdateStudent()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get student data
    cur.execute("SELECT * FROM students WHERE regd_no=%s", (regd_no,))
    student = cur.fetchone()

    # -------------------------
    # When Page Loads (GET)
    # -------------------------
    if request.method == "GET":
        form.name.data = student["name"]
        form.aadhaar.data = student["aadhaar"]
        form.email.data = student["email"]
        form.phone.data = student["phone"]
        form.gender.data = student["gender"]
        form.dob.data = student["dob"]
        form.branch.data = student["branch"]
        form.year.data = student["year"]

    # -------------------------
    # When Form Submitted (POST)
    # -------------------------
    if form.validate_on_submit():

        photo_data = student["photo"]
        photo_type = student["photo_type"]

        # If new photo uploaded
        if form.photo.data:
            photo = form.photo.data
            photo_data = photo.read()
            photo_type = photo.content_type

        cur.execute(
            """
            UPDATE students
            SET name=%s,
                aadhaar=%s,
                email=%s,
                phone=%s,
                gender=%s,
                dob=%s,
                branch=%s,
                year=%s,
                photo=%s,
                photo_type=%s
            WHERE regd_no=%s
        """,
            (
                form.name.data,
                form.aadhaar.data,
                form.email.data,
                form.phone.data,
                form.gender.data,
                form.dob.data,
                form.branch.data,
                form.year.data,
                photo_data,
                photo_type,
                regd_no,
            ),
        )

        mysql.connection.commit()
        flash("Student updated successfully!", "success")
        return redirect(url_for("institute_update_student"))

    cur.close()

    return render_template("final_update_student.html", form=form, regd_no=regd_no)


# =========================================================
#              INSTITUTE DELETE STUDENT MODULE
# =========================================================
@app.route("/institute_delete_student", methods=["GET", "POST"])
def institute_delete_student():
    form = InstituteDeleteStudent()
    students = []  # Stores fetched student records
    searched = False  # Indicates whether search was performed

    if form.validate_on_submit():
        searched = True
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Build query dynamically based on input
        query = "SELECT * FROM students WHERE 1=1"
        params = []

        if form.regd_no.data:
            query += " AND regd_no = %s"
            params.append(form.regd_no.data)

        if form.name.data:
            query += " AND name LIKE %s"
            params.append("%" + form.name.data + "%")

        # If no input, you can either fetch all students or show a message
        if not params:
            flash("Please enter at least one search criteria", "warning")
            cur.close()
            return render_template(
                "institute_delete_student.html",
                form=form,
                students=students,
                searched=False,
            )

        # Execute the query
        cur.execute(query, tuple(params))
        students = cur.fetchall()
        cur.close()

        if not students:
            flash("No student record found", "warning")

    return render_template(
        "institute_delete_student.html", form=form, students=students, searched=searched
    )


@app.route("/final_delete_student/<regd_no>", methods=["POST"])
def final_delete_student(regd_no):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE regd_no=%s", (regd_no,))
    cur.execute("DELETE FROM student_login WHERE regd_no=%s",(regd_no,))
    mysql.connection.commit()
    cur.close()

    flash("Student deleted successfully!", "success")
    return redirect(url_for("institute_delete_student"))


# =========================================================
#              INSTITUTE ADD TEACHER MODULE
# =========================================================
@app.route("/institute_add_teacher", methods=["GET", "POST"])
def institute_add_teacher():
    form = InstituteAddTeacher()

    # Insert teacher data into database
    if form.validate_on_submit():
        cur = mysql.connection.cursor()

        try:
            # 🔹 Step 1: Check if email already exists
            cur.execute(
                "SELECT teacher_id FROM teachers WHERE email = %s", (form.email.data,)
            )
            existing_email = cur.fetchone()

            if existing_email:
                flash("Email already exists", "danger")
                return render_template("institute_add_teacher.html", form=form)

            # 🔹 Step 2: Read image
            photo_file = form.photo.data
            photo_data = photo_file.read()
            photo_type = photo_file.mimetype

            # 🔹 Step 3: Insert data
            cur.execute(
                """
                INSERT INTO teachers
                (
                    regd_no, full_name, aadhaar, gender,
                    date_of_birth, address, blood_group,
                    phone, email, designation, qualification,
                    experience_years, date_of_joining,
                    photo, salary, photo_type,department
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                """,
                (
                    form.regd_no.data,
                    form.full_name.data,
                    form.aadhaar.data,
                    form.gender.data,
                    form.date_of_birth.data,
                    form.address.data,
                    form.blood_group.data,
                    form.phone.data,
                    form.email.data,
                    form.designation.data,
                    form.qualification.data,
                    form.experience_years.data,
                    form.date_of_joining.data,
                    photo_data,
                    form.salary.data,
                    photo_type,
                    form.department.data,
                ),
            )

            mysql.connection.commit()
            flash("Teacher added successfully!", "success")
            return redirect(url_for("institute_add_teacher"))

        # Handle duplicate / constraint errors
        except IntegrityError as e:
            mysql.connection.rollback()
            error = str(e)

            if "regd_no" in error:
                flash("Registration number already exists", "danger")
            elif "aadhaar" in error:
                flash("Aadhaar number already exists", "danger")
            elif "email" in error:
                flash("Email already exists", "danger")
            else:
                flash("Database constraint violation", "danger")

        finally:
            cur.close()

    return render_template("institute_add_teacher.html", form=form)


# =========================================================
#              INSTITUTE VIEW TEACHER MODULE
# =========================================================


@app.route("/institute_view_teacher", methods=["GET", "POST"])
def institute_view_teacher():
    form = InstituteViewTeacher()
    teachers = []
    searched = False

    if request.method == "POST":

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # 🔵 SEARCH ALL BUTTON
        if form.search_all.data:
            searched = True
            cur.execute("SELECT * FROM teachers ORDER BY regd_no ASC")
            teachers = cur.fetchall()
            cur.close()

            return render_template(
                "institute_view_teacher.html",
                form=form,
                teachers=teachers,
                searched=searched,
            )

        # 🔍 NORMAL SEARCH BUTTON
        if form.submit.data:
            searched = True

            query = "SELECT * FROM teachers WHERE 1=1"
            params = []

            if form.regd_no.data:
                query += " AND regd_no = %s"
                params.append(form.regd_no.data)

            if form.name.data:
                query += " AND full_name LIKE %s"
                params.append("%" + form.name.data + "%")

            if not params:
                flash("Please enter at least one search criteria", "warning")
                cur.close()
                return render_template(
                    "institute_view_teacher.html",
                    form=form,
                    teachers=[],
                    searched=False,
                )

            query += " ORDER BY regd_no ASC"

            cur.execute(query, tuple(params))
            teachers = cur.fetchall()
            cur.close()

    return render_template(
        "institute_view_teacher.html", form=form, teachers=teachers, searched=searched
    )


# =========================================================
#              TEACHER PHOTO DISPLAY ROUTE
# =========================================================
@app.route("/teacher_photo/<int:teacher_id>")
def teacher_photo(teacher_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch student image from database
    cur.execute(
        "SELECT photo, photo_type FROM teachers WHERE teacher_id = %s", (teacher_id,)
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        return "", 404

    return Response(row["photo"], mimetype=row["photo_type"])


# =========================================================
#              INSTITUTE UPDATE TEACHER MODULE
# =========================================================
@app.route("/institute_update_teacher", methods=["GET", "POST"])
def institute_update_teacher():
    form = InstituteUpdateTeacher()
    teachers = []  # Stores fetched student records
    searched = False  # Indicates whether search was performed

    if form.validate_on_submit():
        searched = True
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Build query dynamically based on input
        query = "SELECT * FROM teachers WHERE 1=1"
        params = []

        if form.regd_no.data:
            query += " AND regd_no = %s"
            params.append(form.regd_no.data)

        if form.name.data:
            query += " AND full_name LIKE %s"
            params.append("%" + form.name.data + "%")

        # If no input, you can either fetch all students or show a message
        if not params:
            flash("Please enter at least one search criteria", "warning")
            cur.close()
            return render_template(
                "institute_update_teacher.html",
                form=form,
                teachers=teachers,
                searched=False,
            )

        # Execute the query
        cur.execute(query, tuple(params))
        teachers = cur.fetchall()
        cur.close()

        if not teachers:
            flash("No Teacher record found", "warning")

    return render_template(
        "institute_update_teacher.html", form=form, teachers=teachers, searched=searched
    )


@app.route("/final_update_teacher/<regd_no>", methods=["GET", "POST"])
def final_update_teacher(regd_no):

    form = FinalUpdateTeacher()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get student data
    cur.execute("SELECT * FROM teachers WHERE regd_no=%s", (regd_no,))
    teacher = cur.fetchone()

    # -------------------------
    # When Page Loads (GET)
    # -------------------------
    if request.method == "GET":
        form.full_name.data = teacher["full_name"]
        form.aadhaar.data = teacher["aadhaar"]
        form.gender.data = teacher["gender"]
        form.date_of_birth.data = teacher["date_of_birth"]
        form.address.data = teacher["address"]
        form.blood_group.data = teacher["blood_group"]
        form.phone.data = teacher["phone"]
        form.email.data = teacher["email"]
        form.designation.data = teacher["designation"]
        form.qualification.data = teacher["qualification"]
        form.department.data = teacher["department"]
        form.experience_years.data = teacher["experience_years"]
        form.date_of_joining.data = teacher["date_of_joining"]
        form.salary.data = teacher["salary"]

    # -------------------------
    # When Form Submitted (POST)
    # -------------------------
    if form.validate_on_submit():

        photo_data = teacher["photo"]
        photo_type = teacher["photo_type"]

        # Check properly if new file uploaded
        if form.photo.data and form.photo.data.filename != "":
            photo = form.photo.data
            photo_data = photo.read()
            photo_type = photo.content_type

        cur.execute(
            """
            UPDATE teachers
            SET full_name=%s,
                aadhaar=%s,
                gender=%s,
                date_of_birth=%s,
                address=%s,
                blood_group=%s,
                phone=%s,
                email=%s,
                designation=%s,
                qualification=%s,
                department=%s,
                experience_years=%s,
                date_of_joining=%s,
                salary=%s,
                photo=%s,
                photo_type=%s
            WHERE regd_no=%s
        """,
            (
                form.full_name.data,
                form.aadhaar.data,
                form.gender.data,
                form.date_of_birth.data,
                form.address.data,
                form.blood_group.data,
                form.phone.data,
                form.email.data,
                form.designation.data,
                form.qualification.data,
                form.department.data,
                form.experience_years.data,
                form.date_of_joining.data,
                form.salary.data,
                photo_data,
                photo_type,
                regd_no,
            ),
        )

        mysql.connection.commit()

        flash("Teacher updated successfully!", "success")
        return redirect(url_for("institute_update_teacher"))

    cur.close()

    return render_template("final_update_teacher.html", form=form, regd_no=regd_no)


# =========================================================
#              INSTITUTE DELETE TEACHER MODULE
# =========================================================
@app.route("/institute_delete_teacher", methods=["GET", "POST"])
def institute_delete_teacher():
    form = InstituteDeleteTeacher()
    teachers = []  # Stores fetched student records
    searched = False  # Indicates whether search was performed

    if form.validate_on_submit():
        searched = True
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Build query dynamically based on input
        query = "SELECT * FROM teachers WHERE 1=1"
        params = []

        if form.regd_no.data:
            query += " AND regd_no = %s"
            params.append(form.regd_no.data)

        if form.name.data:
            query += " AND full_name LIKE %s"
            params.append("%" + form.name.data + "%")

        # If no input, you can either fetch all students or show a message
        if not params:
            flash("Please enter at least one search criteria", "warning")
            cur.close()
            return render_template(
                "institute_delete_teacher.html",
                form=form,
                teachers=teachers,
                searched=False,
            )

        # Execute the query
        cur.execute(query, tuple(params))
        teachers = cur.fetchall()
        cur.close()

        if not teachers:
            flash("No Teacher record found", "warning")

    return render_template(
        "institute_delete_teacher.html", form=form, teachers=teachers, searched=searched
    )


@app.route("/final_delete_teacher/<regd_no>", methods=["POST"])
def final_delete_teacher(regd_no):
    cur = mysql.connection.cursor()
    print(regd_no)
    cur.execute("DELETE FROM teachers WHERE regd_no=%s", (regd_no,))
    cur.execute("DELETE FROM teacher_login WHERE regd_no=%s",(regd_no,))
    mysql.connection.commit()
    cur.close()

    flash("Teacher deleted successfully!", "success")
    return redirect(url_for("institute_delete_teacher"))


# =========================================================
#              INSTITUTE NOTIFICATION SECTION
# =========================================================


@app.route("/add-notice", methods=["GET", "POST"])
def add_notice():
    form = InstituteAddNotice()

    if form.validate_on_submit():

        try:
            conn = mysql.connection
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO notices 
                (notice_number, title, subject, purpose, description, drive_link, declared_by, department, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    form.notice_number.data,
                    form.title.data,
                    form.subject.data,
                    form.purpose.data,
                    form.description.data,
                    form.drive_link.data,
                    form.declared_by.data,
                    form.department.data,
                    form.is_active.data,
                ),
            )

            conn.commit()
            cursor.close()

            flash(" Notice added successfully!", "success")
            return redirect(url_for("add_notice"))

        except MySQLdb.IntegrityError:
            flash(
                " Notice number already exists! Please use a different number.",
                "danger",
            )

        except Exception as e:
            flash(f" Something went wrong: {str(e)}", "danger")

    return render_template("add_notice.html", form=form)


@app.route("/view-notice", methods=["GET"])
def view_notice():
    search = request.args.get("search", "").strip()  # 🔥 important fix

    cursor = mysql.connection.cursor()

    if search:  # only when actual text exists
        cursor.execute(
            "SELECT * FROM notices WHERE notice_number LIKE %s ORDER BY created_at DESC",
            ("%" + search + "%",),
        )
    else:  # when empty → show all notices
        cursor.execute("SELECT * FROM notices ORDER BY created_at DESC")

    notices = cursor.fetchall()
    cursor.close()

    return render_template("view_notice.html", notices=notices)


@app.route("/update_notice", methods=["GET", "POST"])
def update_notice():

    form = UpdateNoticeSearchForm()
    notices = []
    searched = False
    no_result = False  # 🔥 NEW FLAG

    if form.validate_on_submit():

        # ❌ If input empty → DO NOTHING
        if not form.notice_number.data.strip():
            return render_template(
                "update_notice.html",
                form=form,
                notices=[],
                searched=False,
                no_result=False,
            )

        searched = True

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute(
            "SELECT * FROM notices WHERE notice_number LIKE %s",
            ("%" + form.notice_number.data + "%",),
        )

        notices = cur.fetchall()
        cur.close()

        if not notices:
            no_result = True  # 🔥 ONLY when searched but no data

    return render_template(
        "update_notice.html",
        form=form,
        notices=notices,
        searched=searched,
        no_result=no_result,  # 🔥 REQUIRED
    )


@app.route("/final_update_notice/<path:notice_number>", methods=["GET", "POST"])
def final_update_notice(notice_number):

    form = FinalUpdateNoticeForm()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM notices WHERE notice_number=%s", (notice_number,))
    notice = cur.fetchone()

    if not notice:
        flash("Notice not found!", "danger")
        return redirect(url_for("update_notice"))

    # 🔥 THIS IS THE MAIN FIX
    if request.method == "GET":
        form.process(
            data={
                "title": notice["title"],
                "subject": notice["subject"],
                "purpose": notice["purpose"],  # MUST match choices
                "declared_by": notice["declared_by"],
                "department": notice["department"],
                "description": notice["description"],
                "drive_link": notice["drive_link"],
            }
        )

    if form.validate_on_submit():

        cur.execute(
            """
            UPDATE notices
            SET title=%s,
                subject=%s,
                purpose=%s,
                declared_by=%s,
                department=%s,
                description=%s,
                drive_link=%s
            WHERE notice_number=%s
        """,
            (
                form.title.data,
                form.subject.data,
                form.purpose.data,
                form.declared_by.data,
                form.department.data,
                form.description.data,
                form.drive_link.data,
                notice_number,
            ),
        )

        mysql.connection.commit()
        cur.close()

        flash("Notice updated successfully!", "success")
        return redirect(url_for("update_notice"))

    cur.close()

    return render_template("final_update_notice.html", form=form)


@app.route("/delete-notice", methods=["GET", "POST"])
def delete_notice():

    form = DeleteNoticeSearchForm()
    confirm_form = ConfirmDeleteForm()

    notice = None
    searched = False

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # =====================
    # 🔍 SEARCH NOTICE
    # =====================
    if request.method == "POST" and form.submit.data:
        searched = True

        notice_number = form.notice_number.data.strip()

        if notice_number:
            
            cur.execute(
                "SELECT * FROM notices WHERE notice_number LIKE %s",
                ("%" + notice_number + "%",),
            )
            notice = cur.fetchone()

            if not notice:
                print()
        else:
            flash("⚠ Please enter notice number", "warning")

    # =====================
    # ❌ DELETE NOTICE
    # =====================
    elif request.method == "POST" and confirm_form.confirm.data:

        notice_number = request.form.get("notice_number")

        if notice_number:
            cur.execute("DELETE FROM notices WHERE notice_number=%s", (notice_number,))
            mysql.connection.commit()

            flash("✅ Notice deleted successfully!", "success")
        else:
            flash("⚠ Something went wrong!", "warning")

        cur.close()
        return redirect(url_for("delete_notice"))
    cur.close()
    return render_template(
        "delete_notice.html",
        form=form,
        confirm_form=confirm_form,
        notice=notice,
        searched=searched,
    )


# =========================================================
#                     RUN APPLICATION
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)
