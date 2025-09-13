import sqlite3

# Функция создания БД
def create_table():
    try:#пытаемся выполнить
        conn = sqlite3.connect('db/notes.db')#подключение к бд
        cur = conn.cursor()#нужен для выполнения SQL запросов
        cur.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                datetime TEXT NOT NULL,
                note TEXT NOT NULL
            )
        ''')# SQL запрос
        # создание таблицы из айди, пользовательского айди, времени и заметки
        conn.commit()
    except sqlite3.Error as e:# действия при ошибке
        print(f"Ошибка при создании таблицы: {e}")
    finally:# действия которые всегда будут выполнены
        conn.close()

# Функция добавления данных в БД
def add_note(user_id, datetime, note):
    try:
        conn = sqlite3.connect('db/notes.db')
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO notes (user_id, datetime, note)
            VALUES (?, ?, ?)
        ''', (user_id, datetime, note))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении заметки: {e}")
    finally:
        conn.close()

# Функция получения данных из БД
def get_notes(user_id):
    try:
        conn = sqlite3.connect('db/notes.db')
        cur = conn.cursor()
        cur.execute('''
            SELECT id, datetime, note FROM notes WHERE user_id = ?
        ''', (user_id,))
        notes = cur.fetchall()
        return notes
    except sqlite3.Error as e:
        print(f"Ошибка при получении заметок: {e}")
        return []
    finally:
        conn.close()

# Функция удаления данных из БД
def delete_note(note_id):
    try:
        conn = sqlite3.connect('db/notes.db')
        cur = conn.cursor()
        cur.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при удалении заметки: {e}")
    finally:
        conn.close()

# Функция сброса номеров после удаления в БД
def rebuild_ids():
    with sqlite3.connect('db/notes.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM notes ORDER BY id")
        rows = cursor.fetchall()
        current_id = 1
        for row in rows:
            cursor.execute("UPDATE notes SET id = ? WHERE id = ?", (current_id, row[0]))
            current_id += 1
        #cursor.execute("UPDATE SQLITE_SEQUENCE SET seq = ? WHERE name = 'notes'", (current_id - 1,))
        conn.commit()