import re
import sys
import subprocess
import tempfile

from pyfzf.pyfzf import FzfPrompt

from model import Model
from bcolors import bcolors


class Main:
    def __init__(self):
        self.model = Model()
        self.fzf = FzfPrompt()

    def run(self):
        print(bcolors.HEADER + '''
                         GEEEEEEEL        ..       :
       ,##############Wf.,;;L#K;;.       ,W,     .Et
        ........jW##Wt      t#E         t##,    ,W#t
              tW##Kt        t#E        L###,   j###t
            tW##E;          t#E      .E#j##,  G#fE#t
          tW##E;            t#E     ;WW; ##,:K#i E#t
       .fW##D,              t#E    j#E.  ##f#W,  E#t
     .f###D,                t#E  .D#L    ###K:   E#t
   .f####Gfffffffffff;      t#E :K#t     ##D.    E#t
  .fLLLLLLLLLLLLLLLLLi       fE ...      #G      ..
                              :          j

Task manager from Zordsdavini (2018)
                ''' + bcolors.ENDC)

        self.menu()

    def menu(self):
        menu = input(bcolors.OKGREEN + 'What you want to do? (?+/tcq) ' + bcolors.ENDC)

        if menu == 'q':
            self.bye()

        elif menu == '?':
            self.about()

        elif menu == '/':
            self.search()

        elif menu == '+':
            self.add()

    def about(self):
        print(bcolors.WARNING + '''
Short instruction
-----------------
? - help (this dialog)
+ - add
/ - search
t - tag manager
c - configuration
q - exit
                ''' + bcolors.ENDC)
        self.menu()

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

    def add(self):
        print('\n' + bcolors.HEADER + 'Adding task\n' + bcolors.ENDC)
        description = input('Description: ')
        aid = self.model.create_task_draft(description)
        self.manage_task(aid)

    def manage_task(self, aid):
        task = self.model.get_task(aid)
        print('\n' + bcolors.HEADER + 'Managing: [' + task['aid'] + '] ' + task['description'] + bcolors.ENDC)

        print('''
            #%s
            Description: %s
            Tags:        [%s]
            Long Term:   [%s]
            Created:     %s
        ''' % (task['aid'], task['description'], '', ' ', task['created_at']))

        self.manage_task_menu(aid)

    def manage_task_menu(self, aid):
        menu = input(bcolors.OKGREEN + 'What you want to do? (?e*+-v&q) ' + bcolors.ENDC)

        if menu == 'q':
            self.bye()

        elif menu == '?':
            self.manage_task_about(aid)

        elif menu == 'e':
            self.edit_task(aid)

    def manage_task_about(self, aid):
        print(bcolors.WARNING + '''
Short instruction
-----------------
? - help (this dialog)
e - edit content
* - toggle long term
+ - add tag
- - remove tag
v - mark done
& - add child task
q - exit
        ''' + bcolors.ENDC)
        self.manage_task_menu(aid)

    def edit_task(self, aid):
        task = self.model.get_task(aid)

        content = '''%s
Tags:        [%s]
Long Term:   [%s]
Created:     %s
        ''' % (task['aid'], '', ' ', task['created_at'])

        content += '\n# ' + task['description']
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
        print(bcolors.OKBLUE + '[content has been saved]/n' + bcolors.ENDC)
        self.manage_task(aid)

    def bye(self):
        print(bcolors.FAIL + 'bye o/' + bcolors.ENDC)
        sys.exit(0)


if __name__ == '__main__':
    a = Main()
    a.run()
