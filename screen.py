import os
import sys

from bcolors import bcolors


class Screen:
    logo = '''
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
    '''

    def __init__(self):
        self.path = '~'
        self.menu = ''
        self.about = ''
        self.header = None
        self.info = None
        self.message = None
        self.fail = None
        self.about_active = False

    def change_path(self, path, menu, about, header=None, info=None):
        self.path = path
        self.menu = menu
        self.about = about
        self.header = header
        self.info = info

    def add_message(self, message):
        self.message = message

    def add_fail(self, message):
        self.fail = message

    def print_logo(self):
        os.system('clear')
        print(bcolors.OKBLUE + self.logo + bcolors.ENDC)

    def formated_path(self):
        return bcolors.OKBLUE + self.path + ': ' + bcolors.ENDC

    def formated_menu(self):
        return bcolors.OKGREEN + 'What you want to do? (' + self.menu + ') ' + bcolors.ENDC

    def print_header(self):
        if self.header is None:
            return
        print(bcolors.HEADER + self.header + bcolors.ENDC)
        print(bcolors.HEADER + '='*len(self.header) + bcolors.ENDC + '\n')

    def print_info(self):
        if self.info is None:
            return
        print(bcolors.WARNING + self.info + bcolors.ENDC)

    def print_message(self):
        if self.message is None:
            return
        print(bcolors.OKGREEN + '[' + self.message + ']' + bcolors.ENDC + '\n')
        self.message = None

    def print_fail(self):
        if self.fail is None:
            return
        print(bcolors.FAIL + '[' + self.fail + ']' + bcolors.ENDC + '\n')
        self.fail = None

    def get_menu(self):
        return input(self.formated_path() + self.formated_menu())

    def activate_about(self):
        self.about_active = True

    def print_about(self):
        if not self.about_active:
            return
        print(bcolors.WARNING + self.about + bcolors.ENDC)
        self.about_active = False

    def print(self):
        self.print_logo()
        self.print_message()
        self.print_fail()
        self.print_about()
        self.print_header()
        self.print_info()
        return self.get_menu()

    def print_init(self, header):
        self.header = header
        self.print_logo()
        self.print_header()

    def bye(self):
        print(bcolors.FAIL + 'bye o/' + bcolors.ENDC)
        sys.exit(0)
