import sys

from pyfzf.pyfzf import FzfPrompt

from model import Model
from bcolors import bcolors


class Tag:
    def __init__(self):
        self.model = Model()
        self.fzf = FzfPrompt()

    def manage_tag(self, tid=None):
        if tid:
            tag = self.model.get_tag(tid)
            print(bcolors.HEADER + 'Managing tag: ' + tag['name'] + bcolors.ENDC)
        else:
            print(bcolors.HEADER + 'Managing tags' + bcolors.ENDC)

        tagsData = self.model.get_all_tags()
        if not tagsData:
            self.add_tag()
            tagsData = self.model.get_all_tags()

        tags = bcolors.WARNING
        for t in tagsData:
            tags += t['name'] + ' '

        print(tags + bcolors.ENDC)

        self.manage_tag_menu(tid)

    def manage_tag_menu(self, tid=None):
        menu = input(bcolors.OKBLUE + '~tag: ' + bcolors.OKGREEN + 'What you want to do? (?/+-&<q) ' + bcolors.ENDC)

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
            print(bcolors.FAIL + 'This is not implemented...' + bcolors.ENDC)
            self.manage_tag_menu(tid)

    def manage_tag_about(self, tid=None):
        print(bcolors.WARNING + '''
Short instruction
-----------------
? - help (this dialog)
/ - search tag
+ - add tag
- - remove tag
& - search linked tasks
< - back
q - exit
                ''' + bcolors.ENDC)
        self.manage_tag(tid)

    def add_tag(self):
        print(bcolors.HEADER + 'Adding tag' + bcolors.ENDC)
        name = input('Name: ')
        tid = self.model.create_tag(name)
        print(bcolors.OKBLUE + '[tag has been created]' + bcolors.ENDC)
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
            print(bcolors.FAIL + 'Tag was not selected...' + bcolors.ENDC)

    def remove_tag(self, tid=None):
        tagsData = self.model.get_all_tags()
        if not tagsData:
            print(bcolors.FAIL + 'Where is no tags...' + bcolors.ENDC)
            self.manage_tag_menu()

        tags = []
        for t in tagsData:
            tags.append(t['name'])

        selected = self.fzf.prompt(tags)
        if selected:
            self.model.remove_tag_by_name(selected[0])
            print(bcolors.OKBLUE + '[tag has been deleted]' + bcolors.ENDC)
            self.manage_tag()
        else:
            print(bcolors.FAIL + 'Tag was not selected...' + bcolors.ENDC)

    def bye(self):
        print(bcolors.FAIL + 'bye o/' + bcolors.ENDC)
        sys.exit(0)
