import sys
import subprocess

from model import Model
from bcolors import bcolors


class Main:
    def __init__(self):
        self.model = Model()

    def run(self):
        print('''
     _oo (o)__(o)  \/
  >-(_  \(__  __) (OO)
     / _/  (  ) ,'.--.)
    / /     )( / /|_|_\\
   / (     (  )| \_.--.
  (   `-.   )/ '.   \) \\
   `--.._) (     `-.(_.'

Task manager from Zordsdavini (2018)
                ''')

        self.menu()

    def menu(self):
        menu = input('What you want to do? (?+/tcq) ')

        if menu == 'q':
            print('bye o/')
            sys.exit(0)

        elif menu == '?':
            self.about()

        elif menu == '/':
            self.search()

        elif menu == '+':
            self.add()

    def about(self):
        print('''
Short instruction
-----------------
? - help (this dialog)
+ - add
/ - search
t - tag manager
c - configuration
q - exit
                ''')
        self.menu()

    def search(self):
        tasks = []
        tasksData = self.model.get_all_tasks()
        if not tasksData:
            self.add()
            tasksData = self.model.get_all_tasks()

        for t in self.model.get_all_tasks():
            tasks.append('%s: %s' % (t[1], t[2]))

        selected = self.fzfCall(tasks)

    def add(self):
        print('\n' + bcolors.HEADER + 'Adding task\n' + bcolors.ENDC)
        description = input('Description: ')
        aid = self.model.create_task_draft(description)
        self.manage_task(aid)


    def add_tag(self, task_id):
        question = input('Do you want to add tag? ([y]/n) ')
        if question == 'y' or question == '':
            self.add_tag(task_id)
        pass

    def manage_task(self, aid):
        task = self.model.get_task(aid)
        print('\n' + bcolors.HEADER + 'Managing: [' + task['aid'] + '] ' + task['description'] + '\n' + bcolors.ENDC)

        print()
        self.manage_task_menu(aid)

    def manage_task_menu(self, aid):
        menu = input('What you want to do? (?e*+-v&q) ')

        if menu == 'q':
            print('bye o/')
            sys.exit(0)

        elif menu == '?':
            self.manage_task_about(aid)

    def manage_task_about(self, aid):
        print('''
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
                ''')
        self.manage_task_menu(aid)

    def fzfCall(self, elements):
        try:
            p = subprocess.Popen(['echo', '\n'.join(elements)], stdout=subprocess.PIPE)
            p2 = subprocess.check_output(('fzf'), stdin=p.stdout)
            return p2
        except:
            return None


if __name__ == '__main__':
    a = Main()
    a.run()
