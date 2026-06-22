<<<<<<< HEAD
# SHAMSKAY LMS

SHAMSKAY LMS is a Learning Management System built with Python and MySQL. It supports CBT (Computer-Based Testing), class scheduling, results management, and role-based access for students, staff, and administrators.

## Features

- **Role-Based Access**: Student, Staff, and Admin dashboards
- **Email OTP Verification**: Secure registration and password reset with time-limited OTP (2 minutes)
- **Strong Password Policy**: Minimum 8 characters with uppercase, lowercase, number, and special character
- **Exam System**:
  - Students cannot retake the same subject exam
  - Live countdown timer during exams
  - Automatic grading (A, B, C, D, F)
- **Results Management**:
  - View results with grades
  - Download results as PDF
  - Student rankings by performance
- **Class Scheduling**: Staff can schedule classes with date, time, venue, and Google Meet links
- **Admin Controls**: Add/remove students and staff

## Requirements

- Python 3.x
- MySQL Server
- Python packages:
  - `mysql-connector-python`
  - `fpdf`

## Database Setup

1. Start MySQL server
2. Create database `SHAMSKAY_LMS` (or let the app auto-create it)
3. Update database credentials in `LMSCONFIG.py` if needed

## Configuration

Edit `LMSCONFIG.py` to configure:
- Database host, port, user, password
- Email SMTP settings (sender email and password)
- Admin PIN

## Usage

Run `LMSAPP.py`:

```bash
python LMSAPP.py
```

### Main Menu
1. Register (with OTP email verification)
2. Login (with email or username)
3. Forgot Password
4. Admin Login
5. Exit

### Staff Dashboard
- Create/manage questions
- Schedule classes
- View all students and their results
- View student rankings

### Student Dashboard
- Take available exams
- View personal results
- Download results PDF
- View class reminders

### Admin Dashboard
- Add/remove staff and students
- View all students, staff, and results
- View best performing student

## Project Structure

```
SHAMSKAY LMS/
├── LMSAPP.py          # Application entry point and UI
├── LMSCONFIG.py       # Database config, models, and business logic
├── schema.sql         # SQL schema (reference)
└── README.md
```

## Default Admin PIN

`SHAMSKAY`
