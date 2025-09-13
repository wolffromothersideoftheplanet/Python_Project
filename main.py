# main.py
import sys
import csv
from db import StudentDB
from typing import Optional
import datetime

DB = StudentDB()

def print_student_row(row):
    print(f"[{row['id']}] {row['first_name']} {row['last_name']} | email: {row['email']} | course: {row['course']} | gpa: {row['gpa']}")

def prompt_date(s: str) -> Optional[str]:
    s = s.strip()
    if not s:
        return None
    try:
        # accept YYYY-MM-DD
        dt = datetime.datetime.strptime(s, "%Y-%m-%d")
        return dt.date().isoformat()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD. Value will be left empty.")
        return None

def add_student_flow():
    print("Add new student")
    fn = input("First name: ").strip()
    ln = input("Last name: ").strip()
    email = input("Email (optional): ").strip() or None
    gender = input("Gender (optional): ").strip() or None
    birth = prompt_date(input("Birthdate YYYY-MM-DD (optional): "))
    phone = input("Phone (optional): ").strip() or None
    course = input("Course (optional): ").strip() or None
    gpa_str = input("GPA (optional, e.g. 3.25): ").strip()
    gpa = float(gpa_str) if gpa_str else None

    sid = DB.add_student(fn, ln, email, gender, birth, phone, course, gpa)
    print(f"Student added with id: {sid}")

def list_students_flow():
    print("All students:")
    rows = DB.list_students()
    if not rows:
        print("-- no students --")
        return
    for r in rows:
        print_student_row(r)

def view_student_flow():
    sid = input("Enter student id: ").strip()
    if not sid.isdigit():
        print("Invalid id")
        return
    row = DB.get_student(int(sid))
    if not row:
        print("Student not found.")
        return
    for k in row.keys():
        print(f"{k}: {row[k]}")

def update_student_flow():
    sid = input("Enter student id to update: ").strip()
    if not sid.isdigit():
        print("Invalid id")
        return
    sid = int(sid)
    row = DB.get_student(sid)
    if not row:
        print("Student not found.")
        return
    print("Leave blank to keep existing value.")
    first_name = input(f"First name [{row['first_name']}]: ").strip() or row['first_name']
    last_name = input(f"Last name [{row['last_name']}]: ").strip() or row['last_name']
    email = input(f"Email [{row['email']}]: ").strip() or row['email']
    gender = input(f"Gender [{row['gender']}]: ").strip() or row['gender']
    birth = input(f"Birthdate [{row['birthdate']}]: ").strip()
    birth = birth or row['birthdate']
    phone = input(f"Phone [{row['phone']}]: ").strip() or row['phone']
    course = input(f"Course [{row['course']}]: ").strip() or row['course']
    gpa_input = input(f"GPA [{row['gpa']}]: ").strip()
    gpa = float(gpa_input) if gpa_input else row['gpa']

    DB.update_student(sid,
                      first_name=first_name,
                      last_name=last_name,
                      email=email,
                      gender=gender,
                      birthdate=birth,
                      phone=phone,
                      course=course,
                      gpa=gpa)
    print("Updated.")

def delete_student_flow():
    sid = input("Enter student id to delete: ").strip()
    if not sid.isdigit():
        print("Invalid id")
        return
    sid = int(sid)
    ok = DB.delete_student(sid)
    if ok:
        print("Deleted.")
    else:
        print("Not found or couldn't delete.")

def search_flow():
    term = input("Search term (name/email/course): ").strip()
    rows = DB.search_students(term)
    if not rows:
        print("No matches.")
        return
    for r in rows:
        print_student_row(r)

def import_csv_flow():
    path = input("CSV file path to import: ").strip()
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Expect header: first_name,last_name,email,gender,birthdate,phone,course,gpa
            header = next(reader, None)
            rows = []
            for r in reader:
                # basic normalization
                if not r:
                    continue
                # Pad to 8 fields
                while len(r) < 8:
                    r.append(None)
                # convert gpa
                try:
                    gpa = float(r[7]) if r[7] else None
                except:
                    gpa = None
                rows.append((r[0], r[1], r[2] or None, r[3] or None, r[4] or None, r[5] or None, r[6] or None, gpa))
            DB.import_from_list(rows)
        print("Import completed.")
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("Error importing:", e)

def export_csv_flow():
    path = input("CSV file path to export to: ").strip()
    rows = DB.export_all()
    with open(path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id','first_name','last_name','email','gender','birthdate','phone','course','gpa','created_at','updated_at'])
        for r in rows:
            writer.writerow([r['id'], r['first_name'], r['last_name'], r['email'], r['gender'], r['birthdate'],
                             r['phone'], r['course'], r['gpa'], r['created_at'], r['updated_at']])
    print(f"Exported {len(rows)} rows to {path}")

def menu():
    MENU = """
Student Management - choose an option:
1. Add student
2. List all students
3. View student by id
4. Update student
5. Delete student
6. Search students
7. Import students from CSV
8. Export students to CSV
9. Exit
"""
    while True:
        print(MENU)
        opt = input("Select (1-9): ").strip()
        if opt == "1":
            add_student_flow()
        elif opt == "2":
            list_students_flow()
        elif opt == "3":
            view_student_flow()
        elif opt == "4":
            update_student_flow()
        elif opt == "5":
            delete_student_flow()
        elif opt == "6":
            search_flow()
        elif opt == "7":
            import_csv_flow()
        elif opt == "8":
            export_csv_flow()
        elif opt == "9":
            print("Bye.")
            DB.close()
            sys.exit(0)
        else:
            print("Invalid option. Choose 1-9.")

if __name__ == "__main__":
    menu()
