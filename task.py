import re
import sqlite3
import subprocess
import tempfile

from pyfzf.pyfzf import FzfPrompt

from model import Model
from bcolors import bcolors
from screen import Screen


class Task:
    def __init__(self):
        self.model = Model()
        self.fzf = FzfPrompt()
        self.screen = Screen()

        self.header = ''
        self.info = ''

    def search(self):
        tasks = []
        tasksData = self.model.get_all_tasks()
        if not tasksData:
            self.add()
            tasksData = self.model.get_all_tasks()

        for t in tasksData:
            tasks.append('%s: %s   [ %s ]' % (t['aid'], t['description'], t['tag_names']))

        selected = self.fzf.prompt(tasks)
        if selected:
            m = re.search(r'^(.+):', selected[0])
            aid = m.group(1)
            if aid:
                self.edit_task(aid)
        else:
            self.screen.add_fail('Task was not selected...')

    def add(self):
        self.screen.print_init('Adding task')
        description = input('Description: ')
        aid = self.model.create_task_draft(description)
        self.screen.add_message('task has been created')
        self.manage_task(aid)

    def manage_task(self, aid):
        task = self.model.get_task(aid)
        self.header = 'Managing task: [' + task['aid'] + '] ' + task['description']

        long_term = ' '
        if task['long_term'] and task['long_term'] != 'FALSE':
            long_term = 'x'

        tags = ''
        if task['tags']:
            tags = ' '.join([t['name'] for t in task['tags']])

        self.info = '''%s
Description: %s
Tags:        [%s]
Long Term:   [%s]
Created:     %s ''' % (task['aid'], task['description'], tags, long_term, task['created_at'])

        if task['done'] and task['done'] != 'FALSE':
            self.info += bcolors.ENDC + bcolors.OKGREEN + '\nFinished:    ' + task['finished_at']

        if task['active'] and task['active'] != 'FALSE':
            self.info += bcolors.ENDC + bcolors.WARNING + '\nACTIVE'

        self.manage_task_menu(aid)

    def manage_task_menu(self, aid):
        about = '''
Short instruction
-----------------
? - help (this dialog)
e - edit content
* - toggle long term
+ - add tag
- - remove tag
! - toggle active
v - toggle done
x - delete task
& - add child task
> - go to child
< - back
q - exit
        '''
        self.screen.change_path('~task', '?e*+-!v&><q', about, self.header, self.info)
        menu = self.screen.print()

        if menu == 'q':
            self.screen.bye()

        elif menu == '?':
            self.screen.activate_about()
            self.manage_task_menu(aid)

        elif menu == 'e':
            self.edit_task(aid)

        elif menu == '*':
            self.toggle_long_term(aid)

        elif menu == '+':
            self.add_tags(aid)

        elif menu == '-':
            self.remove_tags(aid)

        elif menu == '!':
            self.toggle_active(aid)

        elif menu == 'v':
            self.toggle_done(aid)

        elif menu == '<':
            return

        else:
            self.screen.add_fail('This is not implemented...')
            self.manage_task_menu(aid)

    def edit_task(self, aid):
        task = self.model.get_task(aid)

        long_term = ' '
        if task['long_term'] and task['long_term'] != 'FALSE':
            long_term = 'x'

        tags = ''
        if task['tags']:
            tags = ' '.join([t['name'] for t in task['tags']])

        content = '''%s
Tags:        [%s]
Long Term:   [%s]
Created:     %s ''' % (task['aid'], tags, long_term, task['created_at'])

        if task['done'] and task['done'] != 'FALSE':
            content += '\nFinished:    ' + task['finished_at']

        if task['active'] and task['active'] != 'FALSE':
            content += '\n**ACTIVE**'

        content += '\n\n# ' + task['description']
        if task['content']:
            content += task['content']

        with tempfile.NamedTemporaryFile(suffix='.md', mode='r+') as temp:
            f = open(temp.name, 'r+')
            f.write(content)
            f.close()

            subprocess.call(['nvim', temp.name])

            f = open(temp.name, 'r')
            new_content = f.read()
            f.close()

            temp.close()

        found = False
        content = ''
        for row in new_content.splitlines():
            if found:
                content += '\n' + row
                continue

            if row == '# ' + task['description']:
                found = True

        self.model.save_content(aid, content)
        self.screen.add_message('content has been saved')
        self.manage_task(aid)

    def toggle_long_term(self, aid):
        self.model.toggle_long_term(aid)
        self.screen.add_message('task has been updated')
        self.manage_task(aid)

    def toggle_active(self, aid):
        self.model.toggle_active(aid)
        self.screen.add_message('task has been activated')
        self.manage_task(aid)

    def toggle_done(self, aid):
        self.model.toggle_done(aid)
        self.screen.add_message('task has been updated')
        self.manage_task(aid)

    def add_tags(self, aid):
        task = self.model.get_task(aid)
        unlinked_tags = self.model.get_tags_not_in_task(task['id'])
        if type(unlinked_tags) is sqlite3.Cursor and unlinked_tags.rowcount == 0:
            self.screen.add_fail('Where is no more unlinked tags left...')
            self.manage_task(aid)

        tags = [t['name'] for t in unlinked_tags]

        selected = self.fzf.prompt(tags, '--multi --cycle')
        if selected:
            self.model.link_tags_to_task(task['id'], selected)
            self.screen.add_message('tags have been linked')
            self.manage_task(aid)
        else:
            self.screen.add_fail('Tag was not selected...')

    def remove_tags(self, aid):
        task = self.model.get_task(aid)
        if not task['tags']:
            self.screen.add_fail('Where is no tags linked...')
            self.manage_task(aid)

        tags = [t['name'] for t in task['tags']]

        selected = self.fzf.prompt(tags, '--multi --cycle')
        if selected:
            self.model.unlink_tags_from_task(task['id'], selected)
            self.screen.add_message('tags have been unlinked')
            self.manage_task(aid)
        else:
            self.screen.add_fail('Tag was not selected...')
