from pyfzf.pyfzf import FzfPrompt

from model import Model
from params import Params
from screen import Screen


class Config:
    def __init__(self):
        self.model = Model()
        self.params = Params()
        self.screen = Screen()

        self.fzf = FzfPrompt()
        self.info = ''

    def manage(self):
        active = 'off'
        if self.params.get('active'):
            active = 'on'
        self.info = 'Show current tasks: [' + active + ']\n'

        done = 'off'
        if self.params.get('done'):
            done = 'on'
        self.info += 'Show done tasks: [' + done + ']\n'

        self.manage_menu()

    def manage_menu(self):
        about = '''
Short instruction
-----------------
? - help (this dialog)
! - toggle active tasks
v - toggle done tasks
t - manage time slots
# - backup/restore
< - back
q - exit
        '''
        self.screen.change_path('~config', '?!vt#<q', about, 'Managing configs', self.info)
        menu = self.screen.print()

        if menu == 'q':
            self.screen.bye()

        elif menu == '?':
            self.screen.activate_about()
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
            self.screen.add_fail('This is not implemented...')
            self.manage_menu()

    def toggle_active(self):
        active = self.params.get('active')
        self.params.update('active', not active)
        self.screen.add_message('parameter "active" has been toggled')

    def toggle_done(self):
        done = self.params.get('done')
        self.params.update('done', not done)
        self.screen.add_message('parameter "done" has been toggled')

    def manage_timeslot(self):
        self.manage_timeslot_menu()

    def manage_timeslot_menu(self):
        about = '''
Short instruction
-----------------
? - help (this dialog)
+ - add time slot
- - remove time slot
< - back
q - exit
        '''
        self.screen.change_path('~config/time_slot', '?+-<q', about, 'Managing time slots')
        menu = self.screen.print()

        if menu == 'q':
            self.screen.bye()

        elif menu == '?':
            self.screen.activate_about()
            self.manage_timeslot_menu()

        elif menu == '+':
            self.add_time_slot()

        elif menu == '-':
            self.remove_time_slot()

        elif menu == '<':
            return

        else:
            self.screen.add_fail('This is not implemented...')
            self.manage_timeslot_menu()

    def add_time_slot(self):
        self.screen.print_init('Adding time slot')
        name = input('Name (short): ')
        description = input('Description: ')
        tid = self.model.create_time_slot(name, description)
        self.screen.add_message('time slot has been created')
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
            self.screen.add_fail('Tag was not selected...')

    def remove_tag(self, tid=None):
        tagsData = self.model.get_all_tags()
        if not tagsData:
            self.screen.add_fail('Where is no tags...')
            self.manage_tag_menu()

        tags = []
        for t in tagsData:
            tags.append(t['name'])

        selected = self.fzf.prompt(tags)
        if selected:
            self.model.remove_tag_by_name(selected[0])
            self.screen.add_message('tag has been deleted')
            self.manage_tag()
        else:
            self.screen.add_fail('Tag was not selected...')
