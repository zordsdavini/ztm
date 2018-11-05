import sys

from pyfzf.pyfzf import FzfPrompt

from model import Model
from params import Params
from bcolors import bcolors


class Config:
    def __init__(self):
        self.model = Model()
        self.params = Params()
        self.fzf = FzfPrompt()

    def manage(self):
        print(bcolors.HEADER + 'Managing configs' + bcolors.ENDC)
        active = 'off'
        if self.params.get('active'):
            active = 'on'

        print(bcolors.WARNING + 'Show current tasks: [' + active + ']' + bcolors.ENDC)

        done = 'off'
        if self.params.get('done'):
            done = 'on'

        print(bcolors.WARNING + 'Show done tasks: [' + done + ']' + bcolors.ENDC)

        self.manage_menu()

    def manage_menu(self):
        menu = input(bcolors.OKBLUE + '~config: ' + bcolors.OKGREEN + 'What you want to do? (?!vt#<q) ' + bcolors.ENDC)

        if menu == 'q':
            self.bye()

        elif menu == '?':
            self.manage_about()
            self.manage_menu()

        elif menu == '!':
            self.toggle_active()
            self.manage()

        elif menu == 'v':
            self.toggle_done()
            self.manage()

        elif menu == 't':
            self.manage_timeslot()
            self.manage_menu()

        elif menu == '<':
            return

        else:
            print(bcolors.FAIL + 'This is not implemented...' + bcolors.ENDC)
            self.manage_menu()

    def manage_about(self):
        print(bcolors.WARNING + '''
Short instruction
-----------------
? - help (this dialog)
! - toggle active tasks
v - toggle done tasks
t - manage time slots
# - backup/restore
< - back
q - exit
                ''' + bcolors.ENDC)

    def toggle_active(self):
        active = self.params.get('active')
        self.params.update('active', not active)
        print(bcolors.OKBLUE + '[parameter "active" has been toggled]' + bcolors.ENDC)

    def toggle_done(self):
        done = self.params.get('done')
        self.params.update('done', not done)
        print(bcolors.OKBLUE + '[parameter "done" has been toggled]' + bcolors.ENDC)

    def manage_timeslot(self):
        self.manage_timeslot_menu()

    def manage_timeslot_menu(self):
        menu = input(bcolors.OKBLUE + '~config/time_slot: ' + bcolors.OKGREEN + 'What you want to do? (?!vt#<q) ' + bcolors.ENDC)

        if menu == 'q':
            self.bye()

        elif menu == '?':
            self.manage_timeslot_about()

        elif menu == '+':
            self.add_time_slot()

        elif menu == '-':
            self.remove_time_slot()

        elif menu == '<':
            return

        else:
            print(bcolors.FAIL + 'This is not implemented...' + bcolors.ENDC)
            self.manage_menu()

    def manage_timeslot_about(self):
        print(bcolors.WARNING + '''
Short instruction
-----------------
? - help (this dialog)
+ - add time slot
- - remove time slot
< - back
q - exit
                ''' + bcolors.ENDC)
        self.manage()

    def add_time_slot(self):
        print(bcolors.HEADER + 'Adding time slot' + bcolors.ENDC)
        name = input('Name (short): ')
        description = input('Description: ')
        tid = self.model.create_time_slot(name, description)
        print(bcolors.OKBLUE + '[time slot has been created]' + bcolors.ENDC)
        self.manage()

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
