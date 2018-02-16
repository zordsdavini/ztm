import re
import sys
import subprocess
import tempfile

from pyfzf.pyfzf import FzfPrompt

from model import Model
from bcolors import bcolors


class Task:
    def __init__(self):
        self.model = Model()
        self.fzf = FzfPrompt()

    def search(self):
        tasks = []
        tasksData = self.model.get_all_tasks()
        if not tasksData:
            self.add()
            tasksData = self.model.get_all_tasks()

        for t in self.model.get_all_tasks():
            tasks.append('%s: %s' % (t['aid'], t['description']))

        selected = self.fzf.prompt(tasks)
        if selected:
            m = re.search(r'^(.+):', selected[0])
            aid = m.group(1)
            if aid:
                self.edit_task(aid)
        else:
            print(bcolors.FAIL + 'Task was not selected...\n' + bcolors.ENDC)

    def add(self):
        print('\n' + bcolors.HEADER + 'Adding task\n' + bcolors.ENDC)
        description = input('Description: ')
        aid = self.model.create_task_draft(description)
        self.manage_task(aid)

    def manage_task(self, aid):
        task = self.model.get_task(aid)
        print('\n' + bcolors.HEADER + 'Managing: [' + task['aid'] + '] ' + task['description'] + bcolors.ENDC)

        long_term = ' '
        if task['long_term'] and task['long_term'] != 'FALSE':
            long_term = 'x'

        print('''
%s
Description: %s
Tags:        [%s]
Long Term:   [%s]
Created:     %s
        ''' % (task['aid'], task['description'], '', long_term, task['created_at']))

        if task['done'] and task['done'] != 'FALSE':
            print(bcolors.OKGREEN + 'Finished:    ' + task['finished_at'] + '\n' + bcolors.ENDC)

        self.manage_task_menu(aid)

    def manage_task_menu(self, aid):
        menu = input(bcolors.OKGREEN + 'What you want to do? (?e*+-v&><q) ' + bcolors.ENDC)

        if menu == 'q':
            self.bye()

        elif menu == '?':
            self.manage_task_about(aid)

        elif menu == 'e':
            self.edit_task(aid)

        elif menu == '*':
            self.toggle_long_term(aid)

        elif menu == 'v':
            self.toggle_done(aid)

        elif menu == '<':
            return

        else:
            print(bcolors.FAIL + 'This is not implemented...\n' + bcolors.ENDC)
            self.manage_task_menu(aid)

    def manage_task_about(self, aid):
        print(bcolors.WARNING + '''
Short instruction
-----------------
? - help (this dialog)
e - edit content
* - toggle long term
+ - add tag
- - remove tag
v - mark done/undone
& - add child task
> - go to child
< - back
q - exit
        ''' + bcolors.ENDC)
        self.manage_task_menu(aid)

    def edit_task(self, aid):
        task = self.model.get_task(aid)

        long_term = ' '
        if task['long_term'] and task['long_term'] != 'FALSE':
            long_term = 'x'

        content = '''%s
Tags:        [%s]
Long Term:   [%s]
Created:     %s ''' % (task['aid'], '', long_term, task['created_at'])

        if task['done'] and task['done'] != 'FALSE':
            content += '\nFinished:    ' + task['finished_at']

        content += '\n\n# ' + task['description']
        if task['content']:
            content += task['content']

        with tempfile.NamedTemporaryFile(suffix='.md', mode='r+') as temp:
            f = open(temp.name, 'r+')
            f.write(content)
            f.close()

            subprocess.call(['vim', temp.name])

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
        print(bcolors.OKBLUE + '\n[content has been saved]' + bcolors.ENDC)
        self.manage_task(aid)

    def toggle_long_term(self, aid):
        self.model.toggle_long_term(aid)
        self.manage_task(aid)

    def toggle_done(self, aid):
        self.model.toggle_done(aid)
        self.manage_task(aid)

    def bye(self):
        print(bcolors.FAIL + 'bye o/' + bcolors.ENDC)
        sys.exit(0)
