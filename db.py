# db.py
import sqlite3
from typing import List, Tuple, Optional
import datetime

DB_FILENAME = "students.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE,
    gender TEXT,
    birthdate TEXT,          -- stored as ISO YYYY-MM-DD
    phone TEXT,
    course TEXT,
    gpa REAL,
    created_at TEXT NOT NULL,
    updated_at TEXT
);
"""

class StudentDB:
    def __init__(self, db_filename: str = DB_FILENAME):
        self.conn = sqlite3.connect(db_filename)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute(CREATE_TABLE_SQL)
        self.conn.commit()

    def add_student(self, first_name: str, last_name: str, email: Optional[str],
                    gender: Optional[str], birthdate: Optional[str],
                    phone: Optional[str], course: Optional[str], gpa: Optional[float]) -> int:
        now = datetime.datetime.utcnow().isoformat()
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO students
            (first_name, last_name, email, gender, birthdate, phone, course, gpa, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (first_name, last_name, email, gender, birthdate, phone, course, gpa, now)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_student(self, student_id: int) -> Optional[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        return cur.fetchone()

    def update_student(self, student_id: int, **fields) -> bool:
        if not fields:
            return False
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        params = list(fields.values())
        params.append(datetime.datetime.utcnow().isoformat())  # updated_at
        params.append(student_id)
        sql = f"UPDATE students SET {set_clause}, updated_at = ? WHERE id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur.rowcount > 0

    def delete_student(self, student_id: int) -> bool:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def list_students(self, limit: Optional[int] = None) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        if limit:
            cur.execute("SELECT * FROM students ORDER BY id LIMIT ?", (limit,))
        else:
            cur.execute("SELECT * FROM students ORDER BY id")
        return cur.fetchall()

    def search_students(self, term: str) -> List[sqlite3.Row]:
        # search across first_name, last_name, email, course
        t = f"%{term}%"
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT * FROM students
            WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR course LIKE ?
            ORDER BY id
            """,
            (t, t, t, t)
        )
        return cur.fetchall()

    def import_from_list(self, rows: List[Tuple]):
        # rows are tuples matching (first_name,last_name,email,gender,birthdate,phone,course,gpa)
        for r in rows:
            try:
                self.add_student(*r)
            except sqlite3.IntegrityError:
                # skip duplicates (e.g., same email) — you could update instead if wanted
                continue
        return True

    def export_all(self) -> List[sqlite3.Row]:
        return self.list_students()

    def close(self):
        self.conn.close()
