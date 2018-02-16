import sqlite3

from abcex import Abcex


class Model:
    def __init__(self):
        self.conn = sqlite3.connect('ztm.db')
        self.conn.row_factory = sqlite3.Row
        self.abcex = Abcex()

    def get_tasks_by_tag(self, tag_name):
        query = '''
            SELECT t.* FROM task t
            LEFT JOIN tag_task tgt ON t.id = tgt.task_id
            LEFT JOIN tag tg ON tg.id = tgt.tag_id
            WHERE tg.name = ?
        '''

        return self.conn.execute(query, tag_name)

    def get_all_tasks(self):
        query = 'SELECT t.* FROM task t'

        return self.conn.execute(query)

    def create_task_draft(self, description):
        query = '''
            INSERT INTO task
            (description, created_at)
            VALUES
            (?, DATETIME('now'))
        '''
        cursor = self.conn.cursor()
        cursor.execute(query, (description,))
        task_id = cursor.lastrowid

        aid = self.abcex.encode(task_id)
        cursor.execute('UPDATE task SET aid=? WHERE id=?', (aid, task_id))

        self.conn.commit()

        return aid

    def get_task(self, aid):
        query = '''
            SELECT t.* FROM task t
            LEFT JOIN tag_task tgt ON t.id = tgt.task_id
            LEFT JOIN tag tg ON tg.id = tgt.tag_id
            WHERE t.aid = ?
        '''
        cursor = self.conn.cursor()
        results = cursor.execute(query, (aid,))

        return results.fetchone()

    def save_content(self, aid, content):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE task SET content=? WHERE aid=?', (content, aid))
        self.conn.commit()

    def toggle_long_term(self, aid):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE task SET long_term=NOT long_term WHERE aid=?', (aid))
        self.conn.commit()

    def toggle_done(self, aid):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE task SET done=NOT done, finished_at=DATETIME(\'now\') WHERE aid=?', (aid))
        self.conn.commit()

    def create_tag(self, name):
        query = 'INSERT INTO tag (name) VALUES (?)'
        cursor = self.conn.cursor()
        cursor.execute(query, (name,))
        self.conn.commit()

        return cursor.lastrowid

    def get_all_tags(self):
        query = 'SELECT t.* FROM tag t'

        return self.conn.execute(query)

    def get_tag(self, tid):
        query = 'SELECT t.* FROM tag t WHERE t.id = ?'
        cursor = self.conn.cursor()
        results = cursor.execute(query, (tid,))

        return results.fetchone()

    def get_tag_by_name(self, name):
        query = 'SELECT t.* FROM tag t WHERE t.name = ?'
        cursor = self.conn.cursor()
        results = cursor.execute(query, (name,))

        return results.fetchone()

    def remove_tag_by_name(self, name):
        query = 'DELETE FROM tag WHERE name = ?'
        cursor = self.conn.cursor()
        cursor.execute(query, (name,))
        self.conn.commit()
