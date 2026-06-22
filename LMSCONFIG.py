import mysql.connector as sql
import random
import string
import hashlib
import re
import smtplib
import ssl
import threading
import datetime
import time
import os
from email.mime.text import MIMEText
from fpdf import FPDF


try:
    conn = sql.connect(
        host="127.0.0.1",
        port="3306",
        user="root",
        password=""
    )
    conn.autocommit = True
    mycursor = conn.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS SHAMSKAY_LMS")
    conn.close()
    conn = sql.connect(
        host="127.0.0.1",
        port="3306",
        user="root",
        database="SHAMSKAY_LMS",
        password=""
    )
    conn.autocommit = True
    mycursor = conn.cursor(dictionary=True)
    # print(f'Database connected successfully.')
except Exception as e:
    print(f"Database unable to connect: {e}")


def email_validate(email):
    pattern = r"^[\w.-]+@[\w.-]+\.com$"
    return bool(re.match(pattern, email))

def password_hash(plain_password):
    return hashlib.sha256(plain_password.encode()).hexdigest()

def password_check(plain_password, stored_hash):
    # Hash what the user typed and compare to the stored hash
    return password_hash(plain_password) == stored_hash

def code_OTP():
    return ''.join(random.choices(string.digits, k=4))

def code_OTP_with_expiry(minutes=2):
    code = code_OTP()
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    return code, expiry

def is_otp_expired(expires_at):
    return datetime.datetime.now() > expires_at


def init_email(to_email, subject, body):
    email    = "shamskay@gmail.com"   # email where app is located
    password = "juxeaagbvsyvwais"      # input app created in email password

    message             = MIMEText(body)
    message["Subject"]  = subject
    message["From"]     = "shamskay@gmail.com"
    message["To"]       = to_email  # input receivers email
    context = ssl.create_default_context()   # secure connection settings
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email, password)
            server.sendmail(email, to_email, message.as_string())
        # print(f"Mail succesfully sent to {to_email}")
        return True
    except Exception as e:
        # print(f"Mail could not be sent: {e}")
        return False
    
def email_verification(email, expiry_minutes=2):
    code, expiry = code_OTP_with_expiry(expiry_minutes)
    subject = "VERIFICATION CODE"
    body    = f"Kindly use {code} to verify your email.\nThis code expires in {expiry_minutes} minutes.\n\nEnsure not to share this."
    sent = init_email(email, subject, body)
    if sent:
        return {"code": code, "expires_at": expiry}
    return None

def strong_password(length=8):
    lower_case  = random.choice(string.ascii_lowercase)
    upper_case  = random.choice(string.ascii_uppercase)
    numeric = random.choice(string.digits)
    special_char = random.choice(string.punctuation)

    characters = string.ascii_letters + string.digits + string.punctuation
    others = [random.choice(characters) for _ in range(length - 4)]

    password_order = list(lower_case + upper_case + numeric + special_char) + others
    random.shuffle(password_order)
    return ''.join(password_order)

def password_is_strong(password):
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in string.punctuation for c in password)
    return has_upper and has_lower and has_digit and has_special


def password_requirements():
    return "Password must be at least 8 characters and include uppercase, lowercase, number, and special character."

def calculate_grade(percentage):
    if percentage >= 70:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    else:
        return "F"

def speak(message):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        # If pyttsx3 is not installed, just skip speaking silently
        pass

class Exam_Time:
    
    def __init__(self, seconds):
        self.total_seconds  = seconds
        self._expired       = False
        self._stopped       = False
        self._start_time    = None
        self._thread        = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        self._start_time = time.time()
        while not self._stopped:
            elapsed = time.time() - self._start_time
            if elapsed >= self.total_seconds:
                self._expired = True
                break
            time.sleep(1)

    def begin(self):
        self._thread.start()

    def end(self):
        self._stopped = True

    def t_expired(self):
        return self._expired

    def t_remaining(self):
        if self._expired:
            return 0
        if self._start_time is None:
            return self.total_seconds
        elapsed = time.time() - self._start_time
        return max(0, self.total_seconds - elapsed)
    


class LMSCONFIG:

    # __school_name has __ to make it private (only this class can access it)
    __school_name = None

    def __init__(self, school_name):
        self.__school_name = school_name
        self._init_tables()

    def get_schoolname(self):
        return self.__school_name

    def _init_tables(self):
        self._create_all_tables()

    def _create_all_tables(self):
        queries = [
            """CREATE TABLE IF NOT EXISTS users (
                serial_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                email VARCHAR(200) NOT NULL UNIQUE,
                Full_name VARCHAR(200) NOT NULL,
                password VARCHAR(255) NOT NULL,
                id VARCHAR(100) NOT NULL UNIQUE,
                role ENUM('student', 'staff') NOT NULL,
                gender VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                subject VARCHAR(100) NOT NULL,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                answer ENUM('A','B','C','D') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(100) NOT NULL,
                subject VARCHAR(100) NOT NULL,
                score INT NOT NULL,
                total INT NOT NULL,
                percentage DECIMAL(5,2) NOT NULL,
                grade VARCHAR(2),
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS class_schedule (
                id INT AUTO_INCREMENT PRIMARY KEY,
                subject VARCHAR(100) NOT NULL,
                staff_id VARCHAR(100),
                staff_name VARCHAR(200),
                class_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                location VARCHAR(200),
                meet_link TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                link_id INT,
                is_read TINYINT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS student_exams (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(100) NOT NULL,
                subject VARCHAR(100) NOT NULL,
                taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_student_subject (student_id, subject)
            )""",
        ]
        for q in queries:
            try:
                mycursor.execute(q)
            except Exception as e:
                print(f"Could not create table: {e}")

        try:
            mycursor.execute("SELECT COUNT(*) as cnt FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='SHAMSKAY_LMS' AND TABLE_NAME='users' AND COLUMN_NAME='gender'")
            if mycursor.fetchone()["cnt"] == 0:
                mycursor.execute("ALTER TABLE users ADD COLUMN gender VARCHAR(20)")
        except Exception as e:
            print(f"Could not add gender column: {e}")

    def generate_unique_id(self, role):
        year = datetime.datetime.now().year
        prefix = "MAT" if role == "student" else "STF"
        try:
            mycursor.execute(
                "SELECT id FROM users WHERE role=%s AND id LIKE %s ORDER BY id ASC",
                (role, f"{prefix}/{year}/%")
            )
            existing_ids = [row["id"] for row in mycursor.fetchall()]
            if existing_ids:
                last_id = existing_ids[-1]
                last_num = int(last_id.split("/")[-1])
                next_num = last_num + 1
            else:
                next_num = 1
            return f"{prefix}/{year}/{next_num:03d}"
        except Exception:
            return f"{prefix}/{year}/001"

    def reset_schema(self):
        try:
            queries = [
                "DROP TABLE IF EXISTS student_exams",
                "DROP TABLE IF EXISTS notifications",
                "DROP TABLE IF EXISTS results",
                "DROP TABLE IF EXISTS class_schedule",
                "DROP TABLE IF EXISTS questions",
                "DROP TABLE IF EXISTS users",
                """CREATE TABLE users (
                    serial_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(100) NOT NULL,
                    email VARCHAR(200) NOT NULL UNIQUE,
                    Full_name VARCHAR(200) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    id VARCHAR(100) NOT NULL UNIQUE,
                    role ENUM('student', 'staff') NOT NULL,
                    gender VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE questions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject VARCHAR(100) NOT NULL,
                    question TEXT NOT NULL,
                    option_a TEXT NOT NULL,
                    option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL,
                    option_d TEXT NOT NULL,
                    answer ENUM('A','B','C','D') NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(100) NOT NULL,
                    subject VARCHAR(100) NOT NULL,
                    score INT NOT NULL,
                    total INT NOT NULL,
                    percentage DECIMAL(5,2) NOT NULL,
                    grade VARCHAR(2),
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE class_schedule (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject VARCHAR(100) NOT NULL,
                    staff_id VARCHAR(100),
                    staff_name VARCHAR(200),
                    class_date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    location VARCHAR(200),
                    meet_link TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(100) NOT NULL,
                    message TEXT NOT NULL,
                    link_id INT,
                    is_read TINYINT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                """CREATE TABLE student_exams (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(100) NOT NULL,
                    subject VARCHAR(100) NOT NULL,
                    taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_student_subject (student_id, subject)
                )""",
            ]
            for q in queries:
                mycursor.execute(q)
            return {"status": True, "message": "Schema reset successfully. All tables dropped and recreated."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def create_account(self, user_id, email, full_name, password, generated_id, confirm_password, role, gender=None):
        if password != confirm_password:
            return {"status": False, "message": "Password does not match."}
        if not password_is_strong(password):
            return {"status": False, "message": password_requirements()}
        role = role.strip().lower()
        if role not in ("student", "staff"):
            return {"status": False, "message": "Your role must either be 'student' or 'staff'"}
        if not email_validate(email):
            return {"status": False, "message": "Email format not valid.\nPlease input in the form: name@gmail.com"}
        hashed = password_hash(password)
        try:
            query  = "INSERT INTO users(user_id, email, Full_name, password, id, role, gender) VALUES(%s,%s,%s,%s,%s,%s,%s)"
            values = (user_id, email, full_name, hashed, generated_id, role, gender if gender is not None else "")
            mycursor.execute(query, values)
            return {
                "status"          : True,
                "role"            : role,
                "generated_id"    : generated_id,
                "message_student" : f"Account created! Your matric number is: {generated_id}",
                "message_staff"   : f"Account created! Your staff ID is: {generated_id}",
                "message"         : f"Account created! Your {'matric number' if role == 'student' else 'staff ID'} is: {generated_id}",
            }
        except sql.errors.IntegrityError:
            return {"status": False, "message": "This email is already registered"}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def Login_user(self, identifier, password):
        try:
            if "@" in identifier:
                query = "SELECT * FROM users WHERE email=%s"
            else:
                query = "SELECT * FROM users WHERE user_id=%s"
            mycursor.execute(query, (identifier,))
            user = mycursor.fetchone()

            if not user:
                return {"status": False, "message": "User not found. Please check your username/email."}

            if password_check(password, user["password"]):
                return {
                    "status"  : True,
                    "message" : f"Welcome back, {user['Full_name']}.",
                    "data"    : user,
                }
            else:
                return {"status": False, "message": "Incorrect password"}

        except Exception as e:
            return {"status": False, "message": str(e)}

    def forgot_password(self, identifier):
        try:
            if "@" in identifier:
                query = "SELECT * FROM users WHERE email=%s"
            else:
                query = "SELECT * FROM users WHERE user_id=%s"
            mycursor.execute(query, (identifier,))
            user = mycursor.fetchone()

            if not user:
                return {"status": False, "message": "User not found. Please check your username/email."}

            otp, expiry = code_OTP_with_expiry()
            subject = "PASSWORD RESET VERIFICATION"
            body = f"Your OTP to reset your password is: {otp}\nThis code expires in 2 minutes.\n\nEnsure not to share this."
            sent = init_email(user["email"], subject, body)
            if not sent:
                return {"status": False, "message": "Could not send verification email. Try again later."}
            return {"status": True, "message": "OTP sent to your email.", "otp": otp, "expires_at": expiry, "user_id": user["id"]}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def reset_password_with_otp(self, user_id, otp, expires_at, entered_otp, new_password):
        try:
            if not password_is_strong(new_password):
                return {"status": False, "message": password_requirements()}
            if is_otp_expired(expires_at):
                return {"status": False, "message": "OTP has expired. Password reset cancelled."}
            if entered_otp != otp:
                return {"status": False, "message": "Invalid OTP. Password reset cancelled."}
            hashed = password_hash(new_password)
            mycursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed, user_id))
            return {"status": True, "message": "Password reset successfully."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def add_class_schedule(self, subject, staff_id, staff_name, class_date, start_time, end_time, location="", meet_link="", description=""):
        try:
            query = """
                INSERT INTO class_schedule(subject, staff_id, staff_name, class_date, start_time, end_time, location, meet_link, description)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (subject, staff_id, staff_name, class_date, start_time, end_time, location, meet_link, description)
            mycursor.execute(query, values)
            return {"status": True, "message": "Class scheduled successfully."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def get_all_schedules(self):
        try:
            mycursor.execute("SELECT * FROM class_schedule ORDER BY class_date ASC, start_time ASC")
            schedules = mycursor.fetchall()
            for s in schedules:
                if isinstance(s.get("start_time"), datetime.timedelta):
                    s["start_time"] = str(s["start_time"])
                if isinstance(s.get("end_time"), datetime.timedelta):
                    s["end_time"] = str(s["end_time"])
                if isinstance(s.get("class_date"), datetime.date):
                    s["class_date"] = str(s["class_date"])
            if schedules:
                return {"status": True, "data": schedules}
            return {"status": False, "message": "No scheduled classes found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def _normalize_schedule(self, schedule):
        if not schedule:
            return schedule
        for key in ["start_time", "end_time"]:
            if isinstance(schedule.get(key), datetime.timedelta):
                schedule[key] = str(schedule[key])
        if isinstance(schedule.get("class_date"), datetime.date):
            schedule["class_date"] = str(schedule["class_date"])
        return schedule

    def update_class_schedule(self, schedule_id, subject, staff_id, staff_name, class_date, start_time, end_time, location, meet_link, description):
        try:
            query = """
                UPDATE class_schedule
                SET subject=%s, staff_id=%s, staff_name=%s, class_date=%s,
                    start_time=%s, end_time=%s, location=%s, meet_link=%s, description=%s
                WHERE id=%s
            """
            values = (subject, staff_id, staff_name, class_date, start_time, end_time, location, meet_link, description, schedule_id)
            mycursor.execute(query, values)
            if mycursor.rowcount:
                return {"status": True, "message": "Schedule updated successfully."}
            return {"status": False, "message": "Schedule not found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def delete_class_schedule(self, schedule_id):
        try:
            mycursor.execute("DELETE FROM class_schedule WHERE id=%s", (schedule_id,))
            if mycursor.rowcount:
                return {"status": True, "message": "Schedule deleted successfully."}
            return {"status": False, "message": "Schedule not found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def get_next_class_for_student(self, subject=None):
        try:
            now = datetime.datetime.now()
            if subject:
                query = """
                    SELECT * FROM class_schedule
                    WHERE subject=%s AND (class_date > %s OR (class_date = %s AND start_time >= %s))
                    ORDER BY class_date ASC, start_time ASC LIMIT 1
                """
                values = (subject, now.date(), now.date(), now.strftime("%H:%M:%S"))
            else:
                query = """
                    SELECT * FROM class_schedule
                    WHERE class_date > %s OR (class_date = %s AND start_time >= %s)
                    ORDER BY class_date ASC, start_time ASC LIMIT 1
                """
                values = (now.date(), now.date(), now.strftime("%H:%M:%S"))
            mycursor.execute(query, values)
            cls = mycursor.fetchone()
            if cls:
                return {"status": True, "data": self._normalize_schedule(cls)}
            return {"status": False, "message": "No upcoming class found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def get_schedules_by_subject(self, subject):
        try:
            mycursor.execute("SELECT * FROM class_schedule WHERE subject=%s ORDER BY class_date ASC, start_time ASC", (subject,))
            schedules = mycursor.fetchall()
            for s in schedules:
                self._normalize_schedule(s)
            if schedules:
                return {"status": True, "data": schedules}
            return {"status": False, "message": "No scheduled classes for this subject."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def get_upcoming_reminder(self, minutes_before=15):
        try:
            now = datetime.datetime.now()
            reminder_time = now + datetime.timedelta(minutes=minutes_before)
            query = """
                SELECT * FROM class_schedule
                WHERE
                    (class_date > %s OR (class_date = %s AND start_time >= %s))
                    AND
                    (class_date < %s OR (class_date = %s AND start_time < %s))
                ORDER BY class_date ASC, start_time ASC
                LIMIT 1
            """
            values = (
                now.date(), now.date(), now.strftime("%H:%M:%S"),
                reminder_time.date(), reminder_time.date(), reminder_time.strftime("%H:%M:%S")
            )
            mycursor.execute(query, values)
            cls = mycursor.fetchone()
            if cls:
                return {
                    "status": True,
                    "data": self._normalize_schedule(cls),
                    "minutes_before": minutes_before
                }
            return {"status": False, "message": "No upcoming class reminder."}
        except Exception as e:
            return {"status": False, "message": str(e)}


    # **********************
    #  QUESTIONS (BY STAFF)
    # **********************

    def create_question(self, subject, question, option_a, option_b, option_c, option_d, answer):
        try:
            query = """
                INSERT INTO questions(subject, question, option_a, option_b, option_c, option_d, answer)
                VALUES(%s, %s, %s, %s, %s, %s, %s)
            """
            mycursor.execute(query, (subject, question, option_a, option_b, option_c, option_d, answer))
            return {"status": True, "message": "Question has been added successfully."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def access_all_questions(self):
        try:
            mycursor.execute("SELECT * FROM questions")
            questions = mycursor.fetchall()
            if questions:
                return {"status": True, "data": questions}
            return {"status": False, "message": "No questions found in the database."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def access_question_by_id(self, question_id):
        try:
            mycursor.execute("SELECT * FROM questions WHERE id=%s", (question_id,))
            q_id = mycursor.fetchone()
            if q_id:
                return {"status": True, "data": q_id}
            return {"status": False, "message": "Question not found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def update_question(self, question_id, subject, question, option_a, option_b, option_c, option_d, answer):
        try:
            query = """
                UPDATE questions
                SET subject=%s, question=%s, option_a=%s, option_b=%s,
                    option_c=%s, option_d=%s, answer=%s
                WHERE id=%s
            """
            mycursor.execute(query, (subject, question, option_a, option_b, option_c, option_d, answer, question_id))
            if mycursor.rowcount:
                return {"status": True, "message": "Question has been updated successfully."}
            return {"status": False, "message": "Question not found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def delete_question(self, question_id):
        try:
            mycursor.execute("DELETE FROM questions WHERE id=%s", (question_id,))
            if mycursor.rowcount:
                return {"status": True, "message": "Question deleted successfully"}
            return {"status": False, "message": "Question not found"}
        except Exception as e:
            return {"status": False, "message": str(e)}

    # *********************
    #  EXAMS FOR STUDENTS
    # *********************

    def generate_exam(self, student_id, subject=None, num_questions=5, time_minutes=5):
        try:
            exam_subject = subject if subject else "General"
            mycursor.execute("SELECT * FROM student_exams WHERE student_id=%s AND subject=%s", (student_id, exam_subject))
            if mycursor.fetchone():
                return {"status": False, "message": f"You have already taken the {exam_subject} exam."}

            if subject:
                mycursor.execute("SELECT * FROM questions WHERE subject=%s", (subject,))
            else:
                mycursor.execute("SELECT * FROM questions")
            all_questions = mycursor.fetchall()

            if not all_questions:
                return {"status": False, "message": "No questions available for this exam"}

            selected = random.sample(all_questions, min(num_questions, len(all_questions)))
            return {
                "status"      : True,
                "questions"   : selected,
                "time_seconds": time_minutes * 60,
            }
        except Exception as e:
            return {"status": False, "message": str(e)}

    # ***********
    #  RESULTS
    # ***********

    def save_result(self, student_id, subject, score, total, percentage):
        try:
            grade = calculate_grade(percentage)
            query = "INSERT INTO results(student_id, subject, score, total, percentage, grade) VALUES(%s,%s,%s,%s,%s,%s)"
            mycursor.execute(query, (student_id, subject, score, total, percentage, grade))
            mycursor.execute("INSERT INTO student_exams(student_id, subject) VALUES(%s,%s)", (student_id, subject))
            return {"status": True, "message": "Result saved successfully"}
        except sql.errors.IntegrityError:
            return {"status": False, "message": "This exam has already been recorded."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def access_results(self, student_id):
        try:
            mycursor.execute("SELECT * FROM results WHERE student_id=%s", (student_id,))
            results = mycursor.fetchall()
            if results:
                return {"status": True, "data": results}
            return {"status": False, "message": "No results found for this student"}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def get_student_results(self, student_id):
        try:
            mycursor.execute("SELECT * FROM results WHERE student_id=%s ORDER BY date DESC", (student_id,))
            results = mycursor.fetchall()
            if results:
                return {"status": True, "data": results}
            return {"status": False, "message": "No results found for this student"}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def view_all_results(self):
        try:
            mycursor.execute("""
                SELECT r.id, r.student_id, u.Full_name, r.subject, r.score, r.total, r.percentage, r.grade, r.date
                FROM results r
                JOIN users u ON r.student_id = u.id
                ORDER BY r.date DESC
            """)
            results = mycursor.fetchall()
            if results:
                return {"status": True, "data": results}
            return {"status": False, "message": "No results found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def get_best_student(self):
        try:
            query = """
                SELECT r.student_id, u.Full_name, u.id,
                       AVG(r.percentage) as avg_percentage,
                       MAX(r.percentage) as max_percentage,
                       COUNT(*) as exam_count,
                       SUM(r.score) as total_score,
                       SUM(r.total) as total_possible
                FROM results r
                JOIN users u ON r.student_id = u.id
                GROUP BY r.student_id, u.Full_name, u.id
                ORDER BY avg_percentage DESC
                LIMIT 1
            """
            mycursor.execute(query)
            best = mycursor.fetchone()
            if best:
                overall_percentage = round((best["total_score"] / best["total_possible"]) * 100, 2) if best["total_possible"] > 0 else 0
                best["overall_percentage"] = overall_percentage
                best["grade"] = calculate_grade(overall_percentage)
                return {
                    "status": True,
                    "data": best,
                    "message": f"Best student: {best['Full_name']} with average {best['avg_percentage']}% and overall {overall_percentage}% ({best['grade']})"
                }
            return {"status": False, "message": "No results found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def generate_result_pdf(self, student_id, student_name, save_path="results"):
        result = self.get_student_results(student_id)
        if not result["status"]:
            return {"status": False, "message": result["message"]}

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        safe_name = "".join(c for c in student_name if c.isalnum() or c in " _-").replace(" ", "_")
        filepath = os.path.join(save_path, f"{safe_name}_Results.pdf")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 12, "Shamskay Academy - Exam Results", ln=True, align="C")
        pdf.ln(4)
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 8, f"Student: {student_name}  |  ID: {student_id}", ln=True, align="C")
        pdf.ln(6)

        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(55, 10, "Subject", 1, 0, "C", True)
        pdf.cell(20, 10, "Score", 1, 0, "C", True)
        pdf.cell(20, 10, "Total", 1, 0, "C", True)
        pdf.cell(25, 10, "Percentage", 1, 0, "C", True)
        pdf.cell(15, 10, "Grade", 1, 0, "C", True)
        pdf.cell(0, 10, "Date", 1, 1, "C", True)

        pdf.set_font("Helvetica", "", 11)
        for r in result["data"]:
            pdf.cell(55, 9, str(r.get("subject", "")), 1, 0, "L")
            pdf.cell(20, 9, str(r.get("score", "")), 1, 0, "C")
            pdf.cell(20, 9, str(r.get("total", "")), 1, 0, "C")
            pdf.cell(25, 9, f"{r.get('percentage', 0)}%", 1, 0, "C")
            pdf.cell(15, 9, str(r.get("grade", "")), 1, 0, "C")
            date_str = str(r.get("date", ""))[:10] if r.get("date") else ""
            pdf.cell(0, 9, date_str, 1, 1, "C")

        pdf.ln(8)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="R")
        pdf.output(filepath)

        return {"status": True, "filepath": filepath, "message": f"PDF saved to {filepath}"}


    # *************************************
    #  ADMIN FEATURES
    # *************************************

    def add_staff(self, user_id, email, full_name, password, confirm_password):
        if password != confirm_password:
            return {"status": False, "message": "Passwords do not match."}
        hashed = password_hash(password)
        generated_id = self.generate_unique_id("staff")
        try:
            query = "INSERT INTO users(user_id, email, Full_name, password, id, role) VALUES(%s,%s,%s,%s,%s,%s)"
            values = (user_id, email, full_name, hashed, generated_id, "staff")
            mycursor.execute(query, values)
            return {
                "status": True,
                "message": f"Staff added successfully! Staff ID: {generated_id}",
                "staff_id": generated_id
            }
        except sql.errors.IntegrityError:
            return {"status": False, "message": "This email is already registered."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def remove_staff(self, staff_id):
        try:
            mycursor.execute("SELECT * FROM users WHERE id=%s AND role='staff'", (staff_id,))
            staff = mycursor.fetchone()
            if not staff:
                return {"status": False, "message": "Staff not found."}
            mycursor.execute("DELETE FROM users WHERE id=%s", (staff_id,))
            if mycursor.rowcount:
                return {"status": True, "message": f"Staff {staff['Full_name']} ({staff_id}) removed successfully."}
            return {"status": False, "message": "Failed to remove staff."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def remove_student(self, student_id):
        try:
            mycursor.execute("SELECT * FROM users WHERE id=%s AND role='student'", (student_id,))
            student = mycursor.fetchone()
            if not student:
                return {"status": False, "message": "Student not found."}
            mycursor.execute("DELETE FROM results WHERE student_id=%s", (student_id,))
            mycursor.execute("DELETE FROM notifications WHERE student_id=%s", (student_id,))
            mycursor.execute("DELETE FROM users WHERE id=%s", (student_id,))
            if mycursor.rowcount:
                return {"status": True, "message": f"Student {student['Full_name']} ({student_id}) removed successfully."}
            return {"status": False, "message": "Failed to remove student."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def view_all_students(self):
        try:
            mycursor.execute("SELECT id, user_id, email, Full_name FROM users WHERE role='student' ORDER BY Full_name ASC")
            students = mycursor.fetchall()
            if students:
                return {"status": True, "data": students}
            return {"status": False, "message": "No students found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def view_all_staff(self):
        try:
            mycursor.execute("SELECT id, user_id, email, Full_name FROM users WHERE role='staff' ORDER BY Full_name ASC")
            staff = mycursor.fetchall()
            if staff:
                return {"status": True, "data": staff}
            return {"status": False, "message": "No staff found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def get_student_rankings(self):
        try:
            query = """
                SELECT r.student_id, u.Full_name, u.id,
                       AVG(r.percentage) as avg_percentage,
                       MAX(r.percentage) as max_percentage,
                       COUNT(*) as exam_count,
                       SUM(r.score) as total_score,
                       SUM(r.total) as total_possible,
                       SUM(r.score) / SUM(r.total) * 100 as overall_percentage
                FROM results r
                JOIN users u ON r.student_id = u.id
                GROUP BY r.student_id, u.Full_name, u.id
                ORDER BY overall_percentage DESC
            """
            mycursor.execute(query)
            rankings = mycursor.fetchall()
            if rankings:
                return {"status": True, "data": rankings}
            return {"status": False, "message": "No results found."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def change_password(self, user_id, new_password):
        try:
            if not password_is_strong(new_password):
                return {"status": False, "message": password_requirements()}
            mycursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            user = mycursor.fetchone()
            if not user:
                return {"status": False, "message": "User not found."}
            otp = code_OTP()
            subject = "PASSWORD CHANGE VERIFICATION"
            body = f"Your OTP to change your password is: {otp}\n\nEnsure not to share this."
            sent = init_email(user["email"], subject, body)
            if not sent:
                return {"status": False, "message": "Could not send verification email. Try again later."}
            entered_otp = input("Enter the OTP sent to your email: ").strip()
            if entered_otp != otp:
                return {"status": False, "message": "Invalid OTP. Password change cancelled."}
            hashed = password_hash(new_password)
            mycursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed, user_id))
            return {"status": True, "message": "Password changed successfully."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def create_notification(self, student_id, message, link_id=None):
        try:
            data = (student_id, message, link_id)
            if link_id is None:
                query = "INSERT INTO notifications(student_id, message) VALUES(%s, %s)"
                values = (student_id, message)
            else:
                query = "INSERT INTO notifications(student_id, message, link_id) VALUES(%s, %s, %s)"
                values = (student_id, message, link_id)
            mycursor.execute(query, values)
            return {"status": True, "message": "Notification sent."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def get_unread_notifications(self, student_id):
        try:
            mycursor.execute("SELECT * FROM notifications WHERE student_id=%s AND is_read=0 ORDER BY id DESC", (student_id,))
            data = mycursor.fetchall()
            if data:
                return {"status": True, "data": data}
            return {"status": False, "message": "No new notifications."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def mark_notification_read(self, student_id):
        try:
            mycursor.execute("UPDATE notifications SET is_read=1 WHERE student_id=%s AND is_read=0", (student_id,))
            return {"status": True, "message": "Notifications marked as read."}
        except Exception as e:
            return {"status": False, "message": str(e)}

    def verify_admin(self, admin_pin):
        if admin_pin.strip().upper() == "SHAMSKAY":
            return {"status": True, "message": "Admin verified."}
        return {"status": False, "message": "Invalid admin PIN."}





