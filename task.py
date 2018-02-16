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

        for t in tasksData:
            tasks.append('%s: %s' % (t['aid'], t['description']))

        selected = self.fzf.prompt(tasks)
        if selected:
            m = re.search(r'^(.+):', selected[0])
            aid = m.group(1)
            if aid:
                self.edit_task(aid)
        else:
            print(bcolors.FAIL + 'Task was not selected...' + bcolors.ENDC)

    def add(self):
        print(bcolors.HEADER + 'Adding task' + bcolors.ENDC)
        description = input('Description: ')
        aid = self.model.create_task_draft(description)
        print(bcolors.OKBLUE + '[task has been created]' + bcolors.ENDC)
        self.manage_task(aid)

    def manage_task(self, aid):
        task = self.model.get_task(aid)
        print(bcolors.HEADER + 'Managing task: [' + task['aid'] + '] ' + task['description'] + bcolors.ENDC)

        long_term = ' '
        if task['long_term'] and task['long_term'] != 'FALSE':
            long_term = 'x'

        tags = ''
        if task['tags']:
            tags = ' '.join([t['name'] for t in task['tags']])

        print('''%s
Description: %s
Tags:        [%s]
Long Term:   [%s]
Created:     %s ''' % (task['aid'], task['description'], tags, long_term, task['created_at']))

        if task['done'] and task['done'] != 'FALSE':
            print(bcolors.OKGREEN + 'Finished:    ' + task['finished_at'] + bcolors.ENDC)

        self.manage_task_menu(aid)

    def manage_task_menu(self, aid):
        menu = input(bcolors.OKBLUE + '~task: ' + bcolors.OKGREEN + 'What you want to do? (?e*+-v&><q) ' + bcolors.ENDC)

        if menu == 'q':
            self.bye()

        elif menu == '?':
            self.manage_task_about(aid)

        elif menu == 'e':
            self.edit_task(aid)

        elif menu == '*':
            self.toggle_long_term(aid)

        elif menu == '+':
            self.add_tags(aid)

        elif menu == '-':
            self.remove_tags(aid)

        elif menu == 'v':
            self.toggle_done(aid)

        elif menu == '<':
            return

        else:
            print(bcolors.FAIL + 'This is not implemented...' + bcolors.ENDC)
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

        tags = ''
        if task['tags']:
            tags = ' '.join([t['name'] for t in task['tags']])

        content = '''%s
Tags:        [%s]
Long Term:   [%s]
Created:     %s ''' % (task['aid'], tags, long_term, task['created_at'])

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
        print(bcolors.OKBLUE + '[content has been saved]' + bcolors.ENDC)
        self.manage_task(aid)

    def toggle_long_term(self, aid):
        self.model.toggle_long_term(aid)
        print(bcolors.OKBLUE + '[task has been updated]' + bcolors.ENDC)
        self.manage_task(aid)

    def toggle_done(self, aid):
        self.model.toggle_done(aid)
        print(bcolors.OKBLUE + '[task has been updated]' + bcolors.ENDC)
        self.manage_task(aid)

    def add_tags(self, aid):
        task = self.model.get_task(aid)
        unlinked_tags = self.model.get_tags_not_in_task(task['id'])
        if len(unlinked_tags) == 0:
            print(bcolors.FAIL + 'Where is no more unlinked tags left...' + bcolors.ENDC)
            self.manage_task(aid)

        tags = [t['name'] for t in unlinked_tags]

        selected = self.fzf.prompt(tags, '--multi --cycle')
        if selected:
            self.model.link_tags_to_task(task['id'], selected)
            print(bcolors.OKBLUE + '[tags have been linked]' + bcolors.ENDC)
            self.manage_task(aid)
        else:
            print(bcolors.FAIL + 'Tag was not selected...' + bcolors.ENDC)

    def remove_tags(self, aid):
        task = self.model.get_task(aid)
        if not task['tags']:
            print(bcolors.FAIL + 'Where is no tags linked...' + bcolors.ENDC)
            self.manage_task(aid)

        tags = [t['name'] for t in task['tags']]

        selected = self.fzf.prompt(tags, '--multi --cycle')
        if selected:
            self.model.unlink_tags_from_task(task['id'], selected)
            print(bcolors.OKBLUE + '[tags have been unlinked]' + bcolors.ENDC)
            self.manage_task(aid)
        else:
            print(bcolors.FAIL + 'Tag was not selected...' + bcolors.ENDC)

    def bye(self):
        print(bcolors.FAIL + 'bye o/' + bcolors.ENDC)
        sys.exit(0)
