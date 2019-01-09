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
            self.manage_time_slot_menu()
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

    def manage_time_slot_menu(self):
        tsData = self.model.get_all_time_slots()
        if tsData:
            self.info = ' | '.join(['%s:%s' % (t['name'], t['description']) for t in tsData]) + '\n'
        else:
            self.info = None

        about = '''
Short instruction
-----------------
? - help (this dialog)
+ - add time slot
- - remove time slot
< - back
q - exit
        '''
        self.screen.change_path('~config/time_slot', '?+-<q', about, 'Managing time slots', self.info)
        menu = self.screen.print()

        if menu == 'q':
            self.screen.bye()

        elif menu == '?':
            self.screen.activate_about()
            self.manage_time_slot_menu()

        elif menu == '+':
            self.add_time_slot()

        elif menu == '-':
            self.remove_time_slot()

        elif menu == '<':
            return

        else:
            self.screen.add_fail('This is not implemented...')
            self.manage_time_slot_menu()

    def add_time_slot(self):
        self.screen.print_init('Adding time slot')
        name = input('Name (short): ')
        description = input('Description: ')
        self.model.create_time_slot(name, description)
        self.screen.add_message('time slot has been created')
        self.manage_time_slot_menu()

    def remove_time_slot(self):
        ts_id = self.select_time_slot()
        if ts_id is not None:
            self.model.remove_time_slot(ts_id)
            self.screen.add_message('time_slot has been deleted')
        else:
            self.screen.add_fail('Time slot was not selected...')

        self.manage_time_slot_menu()

    def select_time_slot(self):
        tsData = self.model.get_all_time_slots()
        if not tsData:
            self.screen.add_fail('Where is no time slots...')
            return

        ts_ids = {}
        ts = []
        for t in tsData:
            ts.append('%s:%s' % (t['name'], t['description']))
            ts_ids['%s:%s' % (t['name'], t['description'])] = t['id']

        selected = self.fzf.prompt(ts)
        if selected:
            return ts_ids[selected[0]]
