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
        query = '''
            SELECT t.* FROM task t
        '''

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
