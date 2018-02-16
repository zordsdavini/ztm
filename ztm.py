import sys

from pyfzf.pyfzf import FzfPrompt

from model import Model
from task import Task
from bcolors import bcolors


class Main:
    def __init__(self):
        self.model = Model()
        self.task = Task()
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
        menu = input(bcolors.OKBLUE + '~: ' + bcolors.OKGREEN + 'What you want to do? (?+/tcq) ' + bcolors.ENDC)

        if menu == '?':
            self.about()

        elif menu == '+':
            self.task.add()
            self.menu()

        elif menu == '/':
            self.task.search()
            self.menu()

        elif menu == 't':
            self.manage_tag()
            self.menu()

        elif menu == 'q':
            self.bye()

        else:
            print(bcolors.FAIL + 'This is not implemented...\n' + bcolors.ENDC)
            self.menu()

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

    def bye(self):
        print(bcolors.FAIL + 'bye o/' + bcolors.ENDC)
        sys.exit(0)

    def manage_tag(self, tid=None):
        if tid:
            tag = self.model.get_tag(tid)
            print(bcolors.HEADER + '\nManaging tag: ' + tag['name'] + '\n' + bcolors.ENDC)
        else:
            print(bcolors.HEADER + '\nManaging tags\n' + bcolors.ENDC)

        tagsData = self.model.get_all_tags()
        if not tagsData:
            self.add_tag()
            tagsData = self.model.get_all_tags()

        tags = bcolors.WARNING
        for t in tagsData:
            tags += t['name'] + ' '

        print(tags + '\n' + bcolors.ENDC)

        self.manage_tag_menu(tid)

    def manage_tag_menu(self, tid=None):
        menu = input(bcolors.OKBLUE + '~tag: ' + bcolors.OKGREEN + 'What you want to do? (?/+-<q) ' + bcolors.ENDC)

        if menu == 'q':
            self.bye()

        elif menu == '/':
            self.search_tag(tid)
            self.manage_tag_menu(tid)

        elif menu == '?':
            self.manage_tag_about(tid)

        elif menu == '+':
            self.add_tag()

        elif menu == '-':
            self.remove_tag(tid)

        elif menu == '<':
            return

        else:
            print(bcolors.FAIL + 'This is not implemented...\n' + bcolors.ENDC)
            self.manage_tag_menu(tid)

    def manage_tag_about(self, tid=None):
        print(bcolors.WARNING + '''
Short instruction
-----------------
? - help (this dialog)
/ - search tag
+ - add tag
- - remove tag
< - back
q - exit
                ''' + bcolors.ENDC)
        self.manage_tag(tid)

    def add_tag(self):
        print('\n' + bcolors.HEADER + 'Adding tag\n' + bcolors.ENDC)
        name = input('Name: ')
        tid = self.model.create_tag(name)
        print(bcolors.OKBLUE + '\n[tag has been created]' + bcolors.ENDC)
        self.manage_tag(tid)

    def search_tag(self, tid=None):
        tagsData = self.model.get_all_tags()
        if not tagsData:
            self.add_tag()
            tagsData = self.model.get_all_tags()

        tags = []
        for t in tagsData:
            tags.append(t['name'])

        selected = self.fzf.prompt(tags)
        if selected:
            tag = self.model.get_tag_by_name(selected[0])
            self.manage_tag(tag['id'])
        else:
            print(bcolors.FAIL + 'Tag was not selected...\n' + bcolors.ENDC)

    def remove_tag(self, tid=None):
        tagsData = self.model.get_all_tags()
        if not tagsData:
            print(bcolors.FAIL + 'Where is no tags...\n' + bcolors.ENDC)
            self.manage_tag_menu()

        tags = []
        for t in tagsData:
            tags.append(t['name'])

        selected = self.fzf.prompt(tags)
        if selected:
            self.model.remove_tag_by_name(selected[0])
            print(bcolors.OKBLUE + '\n[tag has been deleted]' + bcolors.ENDC)
            self.manage_tag()
        else:
            print(bcolors.FAIL + 'Tag was not selected...\n' + bcolors.ENDC)


if __name__ == '__main__':
    a = Main()
    a.run()
