import sys

from pyfzf.pyfzf import FzfPrompt

from model import Model
from task import Task
from tag import Tag
from bcolors import bcolors


class Main:
    def __init__(self):
        self.model = Model()
        self.task = Task()
        self.tag = Tag()
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

Task manager from Zordsdavini (2018) ''' + bcolors.ENDC)

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
            self.tag.manage_tag()
            self.menu()

        elif menu == 'q':
            self.bye()

        else:
            print(bcolors.FAIL + 'This is not implemented...' + bcolors.ENDC)
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


if __name__ == '__main__':
    a = Main()
    a.run()
