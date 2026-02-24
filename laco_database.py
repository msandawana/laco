"""
LACO Membership Database Module
Labour and Civic Organization - Membership Management System
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.expanduser("~/Documents/LACO"), "laco_members.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            surname TEXT NOT NULL,
            firstnames TEXT NOT NULL,
            initials TEXT,
            id_number TEXT,
            date_of_birth TEXT,
            gender TEXT,
            postal_address TEXT,
            tel_number TEXT,
            cell_number TEXT,
            postal_code TEXT,
            email TEXT,
            province TEXT,
            ward TEXT,
            municipality TEXT,
            membership_category TEXT DEFAULT 'Ordinary',
            monthly_amount REAL DEFAULT 50.0,
            bank_account_holder TEXT,
            bank_name TEXT,
            account_number TEXT,
            branch_name TEXT,
            branch_code TEXT,
            debit_order_date TEXT,
            membership_number TEXT,
            status TEXT DEFAULT 'Pending',
            date_joined TEXT,
            form_pdf_path TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_member(data: dict):
    conn = get_conn()
    c = conn.cursor()
    # Auto-generate membership number
    c.execute("SELECT COUNT(*) FROM members")
    count = c.fetchone()[0] + 1
    membership_no = f"LACO-{datetime.now().year}-{count:04d}"
    try:
        c.execute("""
            INSERT INTO members (
                title, surname, firstnames, initials, id_number, date_of_birth,
                gender, postal_address, tel_number, cell_number, postal_code, email,
                province, ward, municipality, membership_category, monthly_amount,
                bank_account_holder, bank_name, account_number, branch_name,
                branch_code, debit_order_date, membership_number, status,
                date_joined, form_pdf_path, notes
            ) VALUES (
                :title, :surname, :firstnames, :initials, :id_number, :date_of_birth,
                :gender, :postal_address, :tel_number, :cell_number, :postal_code, :email,
                :province, :ward, :municipality, :membership_category, :monthly_amount,
                :bank_account_holder, :bank_name, :account_number, :branch_name,
                :branch_code, :debit_order_date, :membership_number, :status,
                :date_joined, :form_pdf_path, :notes
            )
        """, {**data, "membership_number": membership_no})
        conn.commit()
        new_id = c.lastrowid
        conn.close()
        return True, "Member added successfully", new_id, membership_no
    except Exception as e:
        conn.close()
        return False, str(e), None, None


def update_member(member_id: int, data: dict):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("""
            UPDATE members SET
                title=:title, surname=:surname, firstnames=:firstnames,
                initials=:initials, id_number=:id_number, date_of_birth=:date_of_birth,
                gender=:gender, postal_address=:postal_address, tel_number=:tel_number,
                cell_number=:cell_number, postal_code=:postal_code, email=:email,
                province=:province, ward=:ward, municipality=:municipality,
                membership_category=:membership_category, monthly_amount=:monthly_amount,
                bank_account_holder=:bank_account_holder, bank_name=:bank_name,
                account_number=:account_number, branch_name=:branch_name,
                branch_code=:branch_code, debit_order_date=:debit_order_date,
                status=:status, notes=:notes
            WHERE id=:id
        """, {**data, "id": member_id})
        conn.commit()
        conn.close()
        return True, "Member updated successfully"
    except Exception as e:
        conn.close()
        return False, str(e)


def delete_member(member_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM members WHERE id=?", (member_id,))
    conn.commit()
    conn.close()
    return True, "Member deleted"


def get_all_members():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, membership_number, title, surname, firstnames, id_number,
               cell_number, email, province, membership_category, status, date_joined
        FROM members ORDER BY surname ASC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_members(term: str):
    conn = get_conn()
    c = conn.cursor()
    like = f"%{term}%"
    c.execute("""
        SELECT id, membership_number, title, surname, firstnames, id_number,
               cell_number, email, province, membership_category, status, date_joined
        FROM members
        WHERE surname LIKE ? OR firstnames LIKE ? OR id_number LIKE ?
           OR membership_number LIKE ? OR email LIKE ? OR cell_number LIKE ?
           OR province LIKE ? OR municipality LIKE ?
        ORDER BY surname ASC
    """, (like, like, like, like, like, like, like, like))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_member_by_id(member_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM members WHERE id=?", (member_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM members")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM members WHERE status='Active'")
    active = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM members WHERE status='Pending'")
    pending = c.fetchone()[0]
    c.execute("SELECT SUM(monthly_amount) FROM members WHERE status='Active'")
    revenue = c.fetchone()[0] or 0
    conn.close()
    return {"total": total, "active": active, "pending": pending, "monthly_revenue": revenue}
