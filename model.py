import sqlite3

from abcex import Abcex
from params import Params


class Model:
    def __init__(self):
        self.conn = sqlite3.connect('ztm.db')
        self.conn.row_factory = sqlite3.Row
        self.abcex = Abcex()

        self.params = Params()

    def get_tasks_by_tag(self, tag_name):
        query = '''
            SELECT t.* FROM task t
            LEFT JOIN tag_task tgt ON t.id = tgt.task_id
            LEFT JOIN tag tg ON tg.id = tgt.tag_id
            WHERE tg.name = ?
        '''

        return self.conn.execute(query, tag_name)

    def get_all_tasks(self, done=False, active=False):
        done_query = ''
        if done or self.params.get('done'):
            done_query = 'AND t.done = 1'

        active_query = ''
        if active or self.params.get('active'):
            active_query = 'AND t.active = 1'

        query = '''
            SELECT t.*, GROUP_CONCAT(g.name, ' ') AS tag_names FROM task t
            LEFT JOIN tag_task tt ON tt.task_id = t.id
            LEFT JOIN tag g ON g.id = tt.tag_id
            WHERE 1 %s %s
            GROUP BY t.id
        ''' % (done_query, active_query)

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
        query = 'SELECT t.* FROM task t WHERE t.aid = ?'
        cursor = self.conn.cursor()
        results = cursor.execute(query, (aid,))
        task = dict(results.fetchone())

        tquery = '''
            SELECT t.* from tag t
            LEFT JOIN tag_task tt ON t.id = tt.tag_id
            WHERE tt.task_id = ?
        '''
        tags = cursor.execute(tquery, (task['id'],))
        task['tags'] = [t for t in tags]
        task['tag_names'] = [t['name'] for t in tags]

        return task

    def get_tags_not_in_task(self, task_id):
        query = '''
            SELECT t.* from tag t
            WHERE t.id NOT IN (
                SELECT t2.id from tag t2
                LEFT JOIN tag_task tt ON t2.id = tt.tag_id
                WHERE tt.task_id = ?
            )
        '''
        cursor = self.conn.cursor()
        return cursor.execute(query, (task_id,))

    def save_content(self, aid, content):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE task SET content=? WHERE aid=?', (content, aid))
        self.conn.commit()

    def toggle_long_term(self, aid):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE task SET long_term=NOT long_term WHERE aid=?', (aid))
        self.conn.commit()

    def toggle_active(self, aid):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE task SET active=NOT active WHERE aid=?', (aid))
        self.conn.commit()

    def toggle_done(self, aid):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE task SET done=NOT done, finished_at=DATETIME(\'now\'), active=0 WHERE aid=?', (aid,))
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

    def link_tags_to_task(self, task_id, tag_names):
        query = 'INSERT INTO tag_task (task_id, tag_id) VALUES (?, ?)'
        cursor = self.conn.cursor()
        for name in tag_names:
            tag = self.get_tag_by_name(name)
            cursor.execute(query, (task_id, tag['id']))

        self.conn.commit()

    def unlink_tags_from_task(self, task_id, tag_names):
        query = 'DELETE FROM tag_task WHERE task_id = ? AND  tag_id = ?'
        cursor = self.conn.cursor()
        for name in tag_names:
            tag = self.get_tag_by_name(name)
            cursor.execute(query, (task_id, tag['id']))

        self.conn.commit()

    def create_time_slot(self, name, description):
        query = 'INSERT INTO time_slot (name, description) VALUES (?, ?)'
        cursor = self.conn.cursor()
        cursor.execute(query, (name, description))
        self.conn.commit()

        return cursor.lastrowid

    def get_all_time_slots(self):
        query = 'SELECT t.* FROM time_slot t'

        return self.conn.execute(query)

    def remove_time_slot(self, tid):
        query = 'DELETE FROM time_slot WHERE id = ?'
        cursor = self.conn.cursor()
        cursor.execute(query, (tid,))
        self.conn.commit()

    def add_tag_to_time_slot(self, t_id, ts_id):
        query = 'DELETE FROM tag_time_slot WHERE tag_id = ?'
        cursor = self.conn.cursor()
        cursor.execute(query, (t_id,))
        self.conn.commit()

        query = 'INSERT INTO tag_time_slot (tag_id, time_slot_id) VALUES (?, ?)'
        cursor = self.conn.cursor()
        cursor.execute(query, (t_id, ts_id))
        self.conn.commit()
