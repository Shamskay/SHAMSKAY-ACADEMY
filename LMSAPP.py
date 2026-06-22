from LMSCONFIG import (
    LMSCONFIG,
    speak,
    email_verification,
    strong_password,
    password_is_strong,
    email_validate,
    password_requirements,
    is_otp_expired,
    calculate_grade,
    Exam_Time,
)
import random
import sys
import datetime
import os


class LMSAPP(LMSCONFIG):
    def __init__(self, school_name):
        super().__init__(school_name)
        self._create_all_tables()
        speak(f"Welcome to {school_name}.")

        print(f"\n{'='*50}")
        print(f"   WELCOME TO {self.get_schoolname()} LMS")
        print(f"{'='*50}")
        self.Home()

    # ************
    #  HOME PAGE
    # ************

    def Home(self):
        while True:
            print("""
            ===== MAIN MENU =====
            1. Register
            2. Login
            3. Forgot Password
            4. Admin Login
            5. Exit
                     """)
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.Register()
            elif choice == "2":
                self.Login()
            elif choice == "3":
                self._forgot_password()
            elif choice == "4":
                self.admin_login()
            elif choice == "5":
                speak(f"Thanks for coming.")
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
                continue

    # **********************
    #  REGISTRATION SECTION
    # **********************

    def Register(self):
        print("\n===== REGISTER =====")
        full_name = input("Full Name: ").strip()
        email = input("Email: ").strip()

        if not email_validate(email):
            print("Invalid email format. Use name@gmail.com")
            return

        print("Select Role:\n1. Student\n2. Staff")
        role_choice = input("Enter choice: ").strip()
        if role_choice == "1":
            role = "student"
        elif role_choice == "2":
            role = "staff"
        else:
            print("Invalid role selection.")
            return

        user_id = input("Create a User ID (username): ").strip()

        print("Sending verification code to your email...")
        sys.stdout.flush()
        otp_data = email_verification(email)
        if not otp_data:
            print("Could not send verification email. Try again later.")
            return

        print(f"\nVerification code sent to {email}")
        if is_otp_expired(otp_data["expires_at"]):
            print("The verification code has expired. Please try registering again.")
            return
        entered_code = input("Enter the verification code: ").strip()
        if entered_code != otp_data["code"]:
            print("Verification failed. Invalid code.")
            return
        print("Email verified successfully!")
        
        auto_password = strong_password()
        print(f"\nAuto-generated strong password: {auto_password}")
        use_auto_password = input("Use this password? (YES/NO): ").strip().lower()
        if use_auto_password == "yes":
            password = auto_password
            confirm_password = password
        else:
            while True:
                password = input("Set your password: ").strip()
                if not password_is_strong(password):
                    print(password_requirements())
                    continue
                confirm_password = input("Confirm password: ").strip()
                if password != confirm_password:
                    print("Passwords do not match.")
                    continue
                break

        generated_id = self._generate_id(role)

        result = self.create_account(user_id, email, full_name, password, generated_id, confirm_password, role)
        if result["status"]:
            if role == "student":
                print(result["message_student"])
            else:
                print(result["message_staff"])
            print("Registration complete! You can now login.")
        else:
            print(f"Registration failed: {result['message']}")

    # ********************************
    #  ID GENERATION (STUDENT, STAFF)
    # ********************************

    def _generate_id(self, role):
        return self.generate_unique_id(role)

    # ********************************
    #  LOGIN (STUDENT, STAFF, ADMIN)
    # ********************************

    def Login(self):
        print("\n===== LOGIN =====")
        identifier = input("Email or Username: ").strip()
        password = input("Password: ").strip()

        result = self.Login_user(identifier, password)
        if result["status"]:
            print(result["message"])
            user = result["data"]
            speak(f"Welcome back, {user['Full_name']}.")

            if user["role"] == "student":
                self.student_dashboard(user)
            else:
                self.staff_dashboard(user)
        else:
            print(result["message"])
            return

    def _forgot_password(self):
        print("\n===== FORGOT PASSWORD =====")
        identifier = input("Enter your Email or Username: ").strip()
        result = self.forgot_password(identifier)
        if not result["status"]:
            print(result["message"])
            return

        if is_otp_expired(result["expires_at"]):
            print("The OTP has expired. Please try again.")
            return

        otp = result["otp"]
        user_id = result["user_id"]
        print(result["message"])

        entered_otp = input("Enter the OTP sent to your email: ").strip()
        if entered_otp != otp:
            print("Invalid OTP. Password reset cancelled.")
            return
        print("OTP verified successfully!")

        while True:
            new_password = input("Enter new password: ").strip()
            if not password_is_strong(new_password):
                print(password_requirements())
                continue
            confirm_password = input("Confirm new password: ").strip()
            if new_password != confirm_password:
                print("Passwords do not match.")
                continue
            break

        reset_result = self.reset_password_with_otp(user_id, otp, result["expires_at"], entered_otp, new_password)
        print(reset_result["message"])

    def admin_login(self):
        print("\n===== ADMIN LOGIN =====")
        pin = input("Enter Admin PIN: ").strip()
        result = self.verify_admin(pin)
        if result["status"]:
            print(result["message"])
            self.admin_dashboard()
        else:
            print(result["message"])
            return


    # ********************
    #  STUDENT DASHBOARD
    # ********************

    def student_dashboard(self, user):
        self._show_class_reminder()
        while True:
            print(f"""
            ===== STUDENT DASHBOARD =====
            Hello, {user['Full_name']} (ID: {user['id']})
            1. View Next Class
            2. View My Full Schedule
            3. Take Exam
            4. View My Results
            5. Download My Results (PDF)
            6. Change Password
            7. Logout
                    """)
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self._view_next_class(user)
            elif choice == "2":
                self._view_my_schedule(user)
            elif choice == "3":
                self._take_exam(user)
            elif choice == "4":
                self._view_results(user)
            elif choice == "5":
                self._download_results_pdf(user)
            elif choice == "6":
                self._change_password(user)
            elif choice == "7":
                print("Logging out...")
                speak("Logged out successfully.")
                return
            else:
                print("Invalid choice.")
                continue

    def _view_next_class(self, user):
        print("\n===== NEXT CLASS =====")
        result = self.get_next_class_for_student()
        if result["status"]:
            cls = result["data"]
            print(f"Subject : {cls['subject']}")
            print(f"Staff   : {cls['staff_name']}")
            print(f"Date    : {cls['class_date']}")
            print(f"Time    : {cls['start_time']} - {cls['end_time']}")
            if cls.get("location"):
                print(f"Venue   : {cls['location']}")
            if cls.get("meet_link"):
                print(f"Meet    : {cls['meet_link']}")
            if cls.get("description"):
                print(f"Note    : {cls['description']}")
        else:
            print(result["message"])


    def _view_my_schedule(self, user):
        print("\n===== MY FULL SCHEDULE =====")
        result = self.get_all_schedules()
        if result["status"]:
            for cls in result["data"]:
                print(f"\nSubject : {cls['subject']}")
                print(f"Staff   : {cls['staff_name']}")
                print(f"Date    : {cls['class_date']}")
                print(f"Time    : {cls['start_time']} - {cls['end_time']}")
                if cls.get("location"):
                    print(f"Venue   : {cls['location']}")
                if cls.get("meet_link"):
                    print(f"Meet    : {cls['meet_link']}")
                if cls.get("description"):
                    print(f"Note    : {cls['description']}")
        else:
            print(result["message"])


    def _show_class_reminder(self):
        result = self.get_upcoming_reminder(minutes_before=15)
        if result["status"]:
            cls = result["data"]
            mins_left = result.get("minutes_before", 15)
            print(f"\n{'!'*50}")
            print(f"  REMINDER: {cls['subject']} starts in {mins_left} minutes!")
            print(f"  Time: {cls['class_date']} at {cls['start_time']} - {cls['end_time']}")
            if cls.get("meet_link"):
                print(f"  Google Meet: {cls['meet_link']}")
            if cls.get("location"):
                print(f"  Venue: {cls['location']}")
            if cls.get("staff_name"):
                print(f"  Staff: {cls['staff_name']}")
            print(f"{'!'*50}\n")


    def _take_exam(self, user):
        print("\n===== TAKE EXAM =====")
        subjects = ["Mathematics", "English"]
        print("Available Subjects:")
        for idx, subj in enumerate(subjects, 1):
            print(f"  {idx}. {subj}")
        print("  0. All Subjects (Random)")

        subj_choice = input("Select subject number: ").strip()
        if subj_choice == "0":
            subject = None
            subject_label = "General"
        else:
            try:
                subject = subjects[int(subj_choice) - 1]
                subject_label = subject
            except (IndexError, ValueError):
                print("Invalid subject selection.")
                return

        exam = self.generate_exam(student_id=user["id"], subject=subject, time_minutes=5)
        if not exam["status"]:
            print(exam["message"])
            return

        questions = exam["questions"]
        time_limit = exam["time_seconds"]

        print(f"\nExam started! Subject: {subject_label}")
        print(f"Questions: {len(questions)} | Time: 5 minutes")

        timer = Exam_Time(seconds=time_limit)
        timer.begin()

        results_list = []

        for idx, q in enumerate(questions, 1):
            if timer.t_expired():
                print("\nExam ended!")
                speak("Time's up!")
                break

            remaining = timer.t_remaining()
            mins_left = remaining // 60
            secs_left = remaining % 60

            print(f"\n{'='*50}")
            print(f"  Q{idx}/{len(questions)}  |  Time Left: {mins_left}m {secs_left}s")
            print(f"{'='*50}")
            print(f"\nQ{idx}: {q['question']}")
            print(f"  A. {q['option_a']}")
            print(f"  B. {q['option_b']}")
            print(f"  C. {q['option_c']}")
            print(f"  D. {q['option_d']}")

            answer = input("Your answer (A/B/C/D): ").strip().upper()
            while answer not in ("A", "B", "C", "D"):
                print("Invalid input. Please enter A, B, C, or D.")
                answer = input("Your answer (A/B/C/D): ").strip().upper()

            is_correct = answer == q["answer"].upper()
            results_list.append({
                "question": q["question"],
                "selected": answer,
                "correct": q["answer"].upper(),
                "status": "Correct" if is_correct else "Incorrect"
            })

        timer.end()
        sys.stdout.write("\r" + " " * 40 + "\r")
        sys.stdout.flush()

        total = len(questions)
        score = sum(1 for r in results_list if r["status"] == "Correct")
        percentage = round((score / total) * 100, 2) if total > 0 else 0.0

        print("\n===== EXAM RESULTS =====")
        for r in results_list:
            print(f"Q: {r['question']}")
            print(f"  Your answer: {r['selected']} | Correct: {r['correct']} | {r['status']}")
        print(f"\nTotal Questions: {total}")
        print(f"Correct Answers: {score}")
        print(f"Percentage: {percentage}%")

        save = self.save_result(user["id"], subject_label, score, total, percentage)
        if save["status"]:
            print("Result saved.")
        else:
            print(f"Could not save result: {save['message']}")


    def _view_results(self, user):
        print("\n===== MY RESULTS =====")
        result = self.access_results(user["id"])
        if result["status"]:
            data = result["data"]
            print(f"{'Subject':<20} {'Score':<10} {'Total':<10} {'%':<8} {'Grade':<7} {'Date':<12}")
            print("-" * 75)
            for r in data:
                date_str = str(r.get("date", "N/A"))[:10]
                grade = r.get("grade", "N/A")
                print(f"{r['subject']:<20} {r['score']:<10} {r['total']:<10} {r['percentage']}%{'':<4} {grade:<7} {date_str:<12}")
        else:
            print(result["message"])

    def _change_password(self, user):
        print("\n===== CHANGE PASSWORD =====")
        while True:
            new_password = input("Enter new password: ").strip()
            if not password_is_strong(new_password):
                print(password_requirements())
                continue
            confirm_password = input("Confirm new password: ").strip()
            if new_password != confirm_password:
                print("Passwords do not match.")
                continue
            break
        result = self.change_password(user["id"], new_password)
        print(result["message"])


    def _download_results_pdf(self, user):
        print("\n===== DOWNLOAD RESULTS PDF =====")
        result = self.generate_result_pdf(user["id"], user["Full_name"])
        if result["status"]:
            print(result["message"])
            speak("Your results PDF has been generated.")
        else:
            print(result["message"])


    # *******************
    #  STAFF DASHBOARD
    # *******************

    def staff_dashboard(self, user):
        while True:
            print(f"""
            ===== STAFF DASHBOARD =====
            Hello, {user['Full_name']} (ID: {user['id']})
            1. Add Question
            2. View All Questions
            3. Edit a Question
            4. Delete a Question
            5. Schedule Class
            6. View All Schedules
            7. Edit Schedule
            8. Delete Schedule
            9. View All Students
            10. View Student Results
            11. View Student Rankings
            12. Change Password
            13. Logout
                      """)
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self._add_question()
            elif choice == "2":
                self._view_all_questions()
            elif choice == "3":
                self._edit_question()
            elif choice == "4":
                self._delete_question()
            elif choice == "5":
                self._schedule_class(user)
            elif choice == "6":
                self._view_all_schedules()
            elif choice == "7":
                self._edit_schedule(user)
            elif choice == "8":
                self._delete_schedule(user)
            elif choice == "9":
                self._staff_view_students()
            elif choice == "10":
                self._staff_view_results_menu()
            elif choice == "11":
                self._staff_view_rankings()
            elif choice == "12":
                self._change_password(user)
            elif choice == "13":
                print("Logging out...")
                break
            else:
                print("Invalid choice.")


    def _add_question(self):
        print("\n===== ADD QUESTION =====")
        subject = input("Subject: ").strip()
        question = input("Question: ").strip()
        option_a = input("Option A: ").strip()
        option_b = input("Option B: ").strip()
        option_c = input("Option C: ").strip()
        option_d = input("Option D: ").strip()
        answer = input("Correct Answer (A/B/C/D): ").strip().upper()

        if answer not in ("A", "B", "C", "D"):
            print("Invalid answer. Must be A, B, C, or D.")
            return

        result = self.create_question(subject, question, option_a, option_b, option_c, option_d, answer)
        print(result["message"])


    def _view_all_questions(self):
        print("\n===== ALL QUESTIONS =====")
        result = self.access_all_questions()
        if result["status"]:
            for q in result["data"]:
                print(f"\nID: {q['id']} | Subject: {q['subject']}")
                print(f"  Q: {q['question']}")
                print(f"  A. {q['option_a']}")
                print(f"  B. {q['option_b']}")
                print(f"  C. {q['option_c']}")
                print(f"  D. {q['option_d']}")
                print(f"  Answer: {q['answer']}")
        else:
            print(result["message"])


    def _edit_question(self):
        print("\n===== EDIT QUESTION =====")
        all_q = self.access_all_questions()
        if all_q["status"]:
            print("\nAvailable Questions:")
            print(f"{'ID':<5} {'Subject':<15} {'Question':<50}")
            print("-" * 75)
            for q in all_q["data"]:
                q_text = q['question'][:47] + ".." if len(q['question']) > 49 else q['question']
                print(f"{q['id']:<5} {q['subject']:<15} {q_text:<50}")
        else:
            print(all_q["message"])
            return

        try:
            q_id = int(input("\nEnter Question ID to edit: ").strip())
        except ValueError:
            print("Invalid ID.")
            return

        result = self.access_question_by_id(q_id)
        if not result["status"]:
            print(result["message"])
            return

        q = result["data"]
        print(f"Editing Question ID: {q['id']}")
        print(f"Current Subject: {q['subject']}")
        subject = input("New Subject (leave blank to keep): ").strip() or q["subject"]
        print(f"Current Question: {q['question']}")
        question = input("New Question (leave blank to keep): ").strip() or q["question"]
        print(f"Current Option A: {q['option_a']}")
        option_a = input("New Option A (leave blank to keep): ").strip() or q["option_a"]
        print(f"Current Option B: {q['option_b']}")
        option_b = input("New Option B (leave blank to keep): ").strip() or q["option_b"]
        print(f"Current Option C: {q['option_c']}")
        option_c = input("New Option C (leave blank to keep): ").strip() or q["option_c"]
        print(f"Current Option D: {q['option_d']}")
        option_d = input("New Option D (leave blank to keep): ").strip() or q["option_d"]
        print(f"Current Answer: {q['answer']}")
        answer = input("New Answer A/B/C/D (leave blank to keep): ").strip().upper() or q["answer"]

        if answer not in ("A", "B", "C", "D"):
            print("Invalid answer. Must be A, B, C, or D.")
            return

        update = self.update_question(q_id, subject, question, option_a, option_b, option_c, option_d, answer)
        print(update["message"])


    def _delete_question(self):
        print("\n===== DELETE QUESTION =====")
        all_q = self.access_all_questions()
        if all_q["status"]:
            print("\nAvailable Questions:")
            print(f"{'ID':<5} {'Subject':<15} {'Question':<50}")
            print("-" * 75)
            for q in all_q["data"]:
                q_text = q['question'][:47] + ".." if len(q['question']) > 49 else q['question']
                print(f"{q['id']:<5} {q['subject']:<15} {q_text:<50}")
        else:
            print(all_q["message"])
            return

        try:
            q_id = int(input("\nEnter Question ID to delete: ").strip())
        except ValueError:
            print("Invalid ID.")
            return

        confirm = input(f"Are you sure you want to delete question {q_id}? (YES/NO): ").strip().upper()
        if confirm != "YES":
            print("Deletion cancelled.")
            return

        result = self.delete_question(q_id)
        print(result["message"])


    def _schedule_class(self, user):
        print("\n===== SCHEDULE CLASS =====")
        subject = input("Subject: ").strip()
        class_date = input("Date (YYYY-MM-DD): ").strip()
        start_time = input("Start Time (HH:MM): ").strip()
        end_time = input("End Time (HH:MM): ").strip()
        location = input("Location/Venue (optional): ").strip()
        meet_link = input("Google Meet Link (optional): ").strip()
        description = input("Description/Nagging note (optional): ").strip()

        result = self.add_class_schedule(
            subject=subject,
            staff_id=user["id"],
            staff_name=user.get("Full_name", ""),
            class_date=class_date,
            start_time=start_time,
            end_time=end_time,
            location=location,
            meet_link=meet_link,
            description=description,
        )
        print(result["message"])


    def _edit_schedule(self, user):
        try:
            print("\n===== EDIT SCHEDULE =====")
            result = self.get_all_schedules()
            if not result["status"]:
                print(result["message"])
                return

            print(f"{'#':<4} {'ID':<6} {'Subject':<15} {'Date':<12} {'Time':<12} {'Staff':<20}")
            print("-" * 80)
            for idx, cls in enumerate(result["data"], 1):
                print(f"{idx:<4} {cls['id']:<6} {cls['subject']:<15} {cls['class_date']:<12} {cls['start_time']:<12} {cls.get('staff_name',''):<20}")

            try:
                schedule_id = int(input("Enter the Schedule ID to edit: ").strip())
            except ValueError:
                print("Invalid ID.")
                return

            cls = next((s for s in result["data"] if s["id"] == schedule_id), None)
            if not cls:
                print("Schedule not found.")
                return

            print(f"\nEditing Schedule ID: {cls['id']}")
            print(f"Current Subject: {cls['subject']}")
            subject = input("New Subject (leave blank to keep): ").strip() or cls["subject"]
            print(f"Current Date: {cls['class_date']}")
            class_date = input("New Date (YYYY-MM-DD) (leave blank to keep): ").strip() or str(cls["class_date"])
            print(f"Current Start Time: {cls['start_time']}")
            start_time = input("New Start Time (HH:MM) (leave blank to keep): ").strip() or str(cls["start_time"])
            print(f"Current End Time: {cls['end_time']}")
            end_time = input("New End Time (HH:MM) (leave blank to keep): ").strip() or str(cls["end_time"])
            print(f"Current Location: {cls.get('location', '')}")
            location = input("New Location (leave blank to keep): ").strip() or cls.get("location", "")
            print(f"Current Meet Link: {cls.get('meet_link', '')}")
            meet_link = input("New Meet Link (leave blank to keep): ").strip() or cls.get("meet_link", "")
            print(f"Current Description: {cls.get('description', '')}")
            description = input("New Description (leave blank to keep): ").strip() or cls.get("description", "")

            update = self.update_class_schedule(
                schedule_id, subject, user["id"], user.get("Full_name", ""),
                class_date, start_time, end_time, location, meet_link, description
            )
            print(update["message"])
        except Exception as e:
            print(f"Error editing schedule: {e}")

    def _view_all_schedules(self):
        print("\n===== ALL SCHEDULED CLASSES =====")
        result = self.get_all_schedules()
        if result["status"]:
            for cls in result["data"]:
                print(f"\nID      : {cls['id']}")
                print(f"Subject : {cls['subject']}")
                print(f"Staff   : {cls['staff_name']}")
                print(f"Date    : {cls['class_date']}")
                print(f"Time    : {cls['start_time']} - {cls['end_time']}")
                if cls.get("location"):
                    print(f"Venue   : {cls['location']}")
                if cls.get("meet_link"):
                    print(f"Meet    : {cls['meet_link']}")
                if cls.get("description"):
                    print(f"Note    : {cls['description']}")
        else:
            print(result["message"])

    def _delete_schedule(self, user):
        try:
            print("\n===== DELETE SCHEDULE =====")
            result = self.get_all_schedules()
            if not result["status"]:
                print(result["message"])
                return

            print(f"{'#':<4} {'ID':<6} {'Subject':<15} {'Date':<12} {'Time':<12} {'Staff':<20}")
            print("-" * 80)
            for idx, cls in enumerate(result["data"], 1):
                print(f"{idx:<4} {cls['id']:<6} {cls['subject']:<15} {cls['class_date']:<12} {cls['start_time']:<12} {cls.get('staff_name',''):<20}")

            try:
                schedule_id = int(input("Enter the Schedule ID to delete: ").strip())
            except ValueError:
                print("Invalid ID.")
                return

            cls = next((s for s in result["data"] if s["id"] == schedule_id), None)
            if not cls:
                print(f"Schedule with ID {schedule_id} not found. Use the ID column, not the # column.")
                return

            print(f"\nSchedule to delete:")
            print(f"  Subject : {cls['subject']}")
            print(f"  Date    : {cls['class_date']}")
            print(f"  Time    : {cls['start_time']} - {cls['end_time']}")

            confirm = input("Are you sure you want to delete this schedule? (YES/NO): ").strip().upper()
            if confirm != "YES":
                print("Deletion cancelled.")
                return

            delete_result = self.delete_class_schedule(schedule_id)
            print(delete_result["message"])
        except Exception as e:
            print(f"Error deleting schedule: {e}")


    def _staff_view_students(self):
        print("\n===== ALL STUDENTS =====")
        result = self.view_all_students()
        if result["status"]:
            print(f"{'#':<4} {'Name':<25} {'ID':<20} {'Email':<30}")
            print("-" * 80)
            for idx, s in enumerate(result["data"], 1):
                print(f"{idx:<4} {s['Full_name']:<25} {s['id']:<20} {s['email']:<30}")
        else:
            print(result["message"])

    def _staff_view_results_menu(self):
        while True:
            print(f"""
            ===== VIEW STUDENT RESULTS =====
            1. View by Student ID
            2. View All Students Results
            3. Back to Staff Dashboard
                      """)
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self._staff_view_student_result()
            elif choice == "2":
                self._staff_view_all_results()
            elif choice == "3":
                break
            else:
                print("Invalid choice.")

    def _staff_view_student_result(self):
        print("\n===== VIEW STUDENT RESULT BY ID =====")
        result = self.view_all_students()
        if not result["status"]:
            print(result["message"])
            return

        print(f"{'#':<4} {'Name':<25} {'ID':<20}")
        print("-" * 60)
        for idx, s in enumerate(result["data"], 1):
            print(f"{idx:<4} {s['Full_name']:<25} {s['id']:<20}")

        student_id = input("\nEnter Student ID to view results: ").strip()
        results = self.get_student_results(student_id)
        if results["status"]:
            print(f"\n{'Subject':<20} {'Score':<10} {'Total':<10} {'%':<8} {'Grade':<7} {'Date':<12}")
            print("-" * 75)
            for r in results["data"]:
                date_str = str(r.get("date", ""))[:10]
                grade = r.get("grade", "N/A")
                print(f"{r['subject']:<20} {r['score']:<10} {r['total']:<10} {r['percentage']}%{'':<4} {grade:<7} {date_str:<12}")
        else:
            print(results["message"])

    def _staff_view_all_results(self):
        print("\n===== ALL STUDENTS RESULTS =====")
        result = self.view_all_results()
        if result["status"]:
            print(f"{'#':<4} {'Student':<25} {'ID':<20} {'Subject':<15} {'Score':<8} {'%':<7} {'Grade':<7} {'Date':<12}")
            print("-" * 100)
            for idx, r in enumerate(result["data"], 1):
                name = r.get("Full_name", "N/A")[:24]
                date_str = str(r.get("date", ""))[:10]
                grade = r.get("grade", "N/A")
                print(f"{idx:<4} {name:<25} {r['student_id']:<20} {r['subject']:<15} {r['score']:<8} {r['percentage']}%{'':<4} {grade:<7} {date_str:<12}")
        else:
            print(result["message"])

    def _staff_view_rankings(self):
        print("\n===== STUDENT RANKINGS BY PERFORMANCE =====")
        result = self.get_student_rankings()
        if result["status"]:
            data = result["data"]
            print(f"{'Rank':<6} {'Name':<25} {'ID':<20} {'Exams':<7} {'Avg %':<8} {'Overall %':<10} {'Grade':<7}")
            print("-" * 90)
            for idx, r in enumerate(data, 1):
                grade = calculate_grade(float(r["overall_percentage"])) if r["overall_percentage"] else "N/A"
                marker = " <-- BEST" if idx == 1 else ""
                print(f"{idx:<6} {r['Full_name']:<25} {r['id']:<20} {r['exam_count']:<7} {round(r['avg_percentage'], 2):<8} {round(r['overall_percentage'], 2)}%{'':<6} {grade:<7}{marker}")
        else:
            print(result["message"])


    # *******************
    #  ADMIN DASHBOARD
    # *******************

    def admin_dashboard(self):
        while True:
            print(f"""
            ===== ADMIN DASHBOARD =====
            1. Add Staff
            2. Remove Staff
            3. Add Student
            4. Remove Student
            5. View All Students
            6. View All Staff
            7. View All Results
            8. View Best Student
            9. Logout to Main Menu
                      """)
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self._admin_add_staff()
            elif choice == "2":
                self._admin_remove_staff()
            elif choice == "3":
                self._admin_add_student()
            elif choice == "4":
                self._admin_remove_student()
            elif choice == "5":
                self._admin_view_students()
            elif choice == "6":
                self._admin_view_staff()
            elif choice == "7":
                self._admin_view_results()
            elif choice == "8":
                self._admin_view_best_student()
            elif choice == "9":
                print("Logging out admin...")
                return
            else:
                print("Invalid choice.")


    def _admin_add_staff(self):
        print("\n===== ADD STAFF =====")
        full_name = input("Staff Full Name: ").strip()
        email = input("Staff Email: ").strip()

        if not email_validate(email):
            print("Invalid email format. Use name@gmail.com")
            return

        user_id = input("Staff Username: ").strip()

        print("Sending verification code to staff email...")
        sys.stdout.flush()
        otp_data = email_verification(email)
        if not otp_data:
            print("Could not send verification email. Try again later.")
            return

        print(f"\nVerification code sent to {email}")
        if is_otp_expired(otp_data["expires_at"]):
            print("The verification code has expired. Please try again.")
            return
        entered_code = input("Enter the verification code: ").strip()
        if entered_code != otp_data["code"]:
            print("Verification failed. Invalid code.")
            return
        print("Email verified successfully!")

        auto_password = strong_password()
        print(f"\nAuto-generated strong password: {auto_password}")
        use_auto_password = input("Use this password? (YES/NO): ").strip().lower()
        if use_auto_password == "yes":
            password = auto_password
            confirm_password = password
        else:
            while True:
                password = input("Set password: ").strip()
                if not password_is_strong(password):
                    print(password_requirements())
                    continue
                confirm_password = input("Confirm password: ").strip()
                if password != confirm_password:
                    print("Passwords do not match.")
                    continue
                break

        generated_id = self._generate_id("staff")
        result = self.create_account(user_id, email, full_name, password, generated_id, password, "staff")
        if result["status"]:
            print(result["message"])
            print("Registration complete. Staff can now login.")
        else:
            print(f"Registration failed: {result['message']}")


    def _admin_remove_staff(self):
        print("\n===== REMOVE STAFF =====")
        result = self.view_all_staff()
        if result["status"]:
            print(f"{'#':<4} {'Name':<25} {'ID':<20} {'Email':<30}")
            print("-" * 80)
            for idx, s in enumerate(result["data"], 1):
                print(f"{idx:<4} {s['Full_name']:<25} {s['id']:<20} {s['email']:<30}")
        else:
            print(result["message"])
            return

        staff_id = input("Enter Staff ID to remove: ").strip()
        confirm = input(f"Are you sure you want to remove staff {staff_id}? (YES/NO): ").strip().upper()
        if confirm != "YES":
            print("Deletion cancelled.")
            return
        result = self.remove_staff(staff_id)
        print(result["message"])

    def _admin_add_student(self):
        print("\n===== ADD STUDENT =====")
        full_name = input("Student Full Name: ").strip()
        email = input("Student Email: ").strip()

        if not email_validate(email):
            print("Invalid email format. Use name@gmail.com")
            return

        user_id = input("Student Username: ").strip()

        print("Sending verification code to student email...")
        sys.stdout.flush()
        otp_data = email_verification(email)
        if not otp_data:
            print("Could not send verification email. Try again later.")
            return

        print(f"\nVerification code sent to {email}")
        if is_otp_expired(otp_data["expires_at"]):
            print("The verification code has expired. Please try again.")
            return
        entered_code = input("Enter the verification code: ").strip()
        if entered_code != otp_data["code"]:
            print("Verification failed. Invalid code.")
            return
        print("Email verified successfully!")

        auto_password = strong_password()
        print(f"\nAuto-generated strong password: {auto_password}")
        use_auto_password = input("Use this password? (YES/NO): ").strip().lower()
        if use_auto_password == "yes":
            password = auto_password
            confirm_password = password
        else:
            while True:
                password = input("Set password: ").strip()
                if not password_is_strong(password):
                    print(password_requirements())
                    continue
                confirm_password = input("Confirm password: ").strip()
                if password != confirm_password:
                    print("Passwords do not match.")
                    continue
                break

        generated_id = self._generate_id("student")
        result = self.create_account(user_id, email, full_name, password, generated_id, password, "student")
        if result["status"]:
            print(result["message"])
            print("Registration complete. Student can now login.")
        else:
            print(f"Registration failed: {result['message']}")

    def _admin_remove_student(self):
        print("\n===== REMOVE STUDENT =====")
        result = self.view_all_students()
        if result["status"]:
            print(f"{'#':<4} {'Name':<25} {'ID':<20} {'Email':<30}")
            print("-" * 80)
            for idx, s in enumerate(result["data"], 1):
                print(f"{idx:<4} {s['Full_name']:<25} {s['id']:<20} {s['email']:<30}")
        else:
            print(result["message"])
            return

        student_id = input("Enter Student ID to remove: ").strip()
        confirm = input(f"Are you sure you want to remove student {student_id}? (YES/NO): ").strip().upper()
        if confirm != "YES":
            print("Deletion cancelled.")
            return
        result = self.remove_student(student_id)
        print(result["message"])


    def _admin_view_students(self):
        print("\n===== ALL STUDENTS =====")
        result = self.view_all_students()
        if result["status"]:
            print(f"{'#':<4} {'Name':<25} {'ID':<20} {'Email':<30}")
            print("-" * 80)
            for idx, s in enumerate(result["data"], 1):
                print(f"{idx:<4} {s['Full_name']:<25} {s['id']:<20} {s['email']:<30}")
        else:
            print(result["message"])


    def _admin_view_staff(self):
        print("\n===== ALL STAFF =====")
        result = self.view_all_staff()
        if result["status"]:
            print(f"{'#':<4} {'Name':<25} {'ID':<20} {'Email':<30}")
            print("-" * 80)
            for idx, s in enumerate(result["data"], 1):
                print(f"{idx:<4} {s['Full_name']:<25} {s['id']:<20} {s['email']:<30}")
        else:
            print(result["message"])


    def _admin_view_results(self):
        print("\n===== ALL STUDENT RESULTS =====")
        result = self.view_all_results()
        if result["status"]:
            print(f"{'#':<4} {'Student':<25} {'ID':<20} {'Subject':<15} {'Score':<8} {'%':<7} {'Grade':<7} {'Date':<12}")
            print("-" * 100)
            for idx, r in enumerate(result["data"], 1):
                name = r.get("Full_name", "N/A")[:24]
                date_str = str(r.get("date", ""))[:10]
                grade = r.get("grade", "N/A")
                print(f"{idx:<4} {name:<25} {r['student_id']:<20} {r['subject']:<15} {r['score']:<8} {r['percentage']}%{'':<4} {grade:<7} {date_str:<12}")
        else:
            print(result["message"])

    def _admin_view_best_student(self):
        print("\n===== BEST STUDENT BY PERFORMANCE =====")
        result = self.get_best_student()
        if result["status"]:
            data = result["data"]
            print(f"Rank: #1")
            print(f"Name    : {data['Full_name']}")
            print(f"ID      : {data['id']}")
            print(f"Exams   : {data['exam_count']}")
            print(f"Avg %   : {round(data['avg_percentage'], 2)}%")
            print(f"Best %  : {data['max_percentage']}%")
            print(f"Overall : {data['overall_percentage']}%")
            print(f"Grade   : {data['grade']}")
        else:
            print(result["message"])


lms = LMSAPP("SHAMSKAY ACADEMY")
