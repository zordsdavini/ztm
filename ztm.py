#!/usr/bin/env python

import argparse

from pyfzf.pyfzf import FzfPrompt

from model import Model
from task import Task
from tag import Tag
from config import Config
from params import Params
from screen import Screen


class Main:
    def __init__(self):
        self.model = Model()
        self.task = Task()
        self.tag = Tag()
        self.config = Config()
        self.params = Params()
        self.screen = Screen()

        self.fzf = FzfPrompt()

        self.parser = argparse.ArgumentParser('ztm')
        self.parser.add_argument('-c', '--current', dest='active', action='store_true')
        self.parser.set_defaults(active=False)

    def run(self):
        n = self.parser.parse_args()
        if n.active:
            self.params.update('active', True)
        self.menu()

    def menu(self):
        about = '''
Short instruction
-----------------
? - help (this dialog)
+ - add
/ - search
t - tag manager
c - configuration
q - exit
            '''
        self.screen.change_path('~', '?+/tcq', about)
        menu = self.screen.print()

        if menu == '?':
            self.screen.activate_about()
            self.menu()

        elif menu == '+':
            self.task.add()
            self.menu()

        elif menu == '/':
            self.task.search()
            self.menu()

        elif menu == 't':
            self.tag.manage_tag()
            self.menu()

        elif menu == 'c':
            self.config.manage()
            self.menu()

        elif menu == 'q':
            self.screen.bye()

        else:
            self.screen.add_fail('This is not implemented...')
            self.menu()


if __name__ == '__main__':
    a = Main()
    a.run()
