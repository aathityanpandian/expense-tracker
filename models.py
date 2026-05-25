from database import get_connection


# --- Category Operations ---

def get_all_categories():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_category(name):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
    except Exception as e:
        conn.close()
        raise e
    conn.close()


def delete_category(category_id):
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE category_id = ?", (category_id,))
    conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()


# --- Expense Operations ---

def add_expense(amount, currency, amount_in_inr, description, category_id, date):
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (amount, currency, amount_in_inr, description, category_id, date) VALUES (?, ?, ?, ?, ?, ?)",
        (amount, currency, amount_in_inr, description, category_id, date),
    )
    conn.commit()
    conn.close()


def edit_expense(expense_id, amount, currency, amount_in_inr, description, category_id, date):
    conn = get_connection()
    conn.execute(
        """UPDATE expenses
           SET amount = ?, currency = ?, amount_in_inr = ?, description = ?, category_id = ?, date = ?
           WHERE id = ?""",
        (amount, currency, amount_in_inr, description, category_id, date, expense_id),
    )
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def get_all_expenses():
    conn = get_connection()
    rows = conn.execute("""
        SELECT e.id, e.amount, e.currency, e.amount_in_inr, e.description, e.date, c.name as category
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def filter_expenses(category_id=None, start_date=None, end_date=None, min_amount=None, max_amount=None):
    conn = get_connection()
    query = """
        SELECT e.id, e.amount, e.currency, e.amount_in_inr, e.description, e.date, c.name as category
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE 1=1
    """
    params = []

    if category_id:
        query += " AND e.category_id = ?"
        params.append(category_id)
    if start_date:
        query += " AND e.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND e.date <= ?"
        params.append(end_date)
    if min_amount is not None:
        query += " AND e.amount_in_inr >= ?"
        params.append(min_amount)
    if max_amount is not None:
        query += " AND e.amount_in_inr <= ?"
        params.append(max_amount)

    query += " ORDER BY e.date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_monthly_summary(year, month):
    conn = get_connection()
    date_prefix = f"{year:04d}-{month:02d}"
    rows = conn.execute("""
        SELECT c.name as category, SUM(e.amount_in_inr) as total, COUNT(e.id) as count
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.date LIKE ?
        GROUP BY c.name
        ORDER BY total DESC
    """, (date_prefix + "%",)).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_expense_by_id(expense_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT e.id, e.amount, e.currency, e.amount_in_inr, e.description, e.date, e.category_id, c.name as category
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.id = ?
    """, (expense_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
