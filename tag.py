from pyfzf.pyfzf import FzfPrompt

from model import Model
from screen import Screen


class Tag:
    def __init__(self):
        self.model = Model()
        self.fzf = FzfPrompt()
        self.screen = Screen()
        self.header = ''
        self.info = None

    def manage_tag(self, tid=None):
        if tid:
            tag = self.model.get_tag(tid)
            self.header = 'Managing tag: ' + tag['name']
        else:
            self.header = 'Managing tags'

        tagsData = self.model.get_all_tags()
        if not tagsData:
            self.add_tag()
            tagsData = self.model.get_all_tags()

        self.info = ' '.join([t['name'] for t in tagsData]) + '\n'

        self.manage_tag_menu(tid)

    def manage_tag_menu(self, tid=None):
        about = '''
Short instruction
-----------------
? - help (this dialog)
/ - search tag
+ - add tag
- - remove tag
& - search linked tasks
< - back
q - exit
        '''
        self.screen.change_path('~tag', '?/+-&<q', about, self.header, self.info)
        menu = self.screen.print()

        if menu == 'q':
            self.screen.bye()

        elif menu == '/':
            self.search_tag(tid)
            self.manage_tag_menu(tid)

        elif menu == '?':
            self.screen.activate_about()
            self.manage_tag(tid)

        elif menu == '+':
            self.add_tag()

        elif menu == '-':
            self.remove_tag(tid)

        elif menu == '<':
            return

        else:
            self.screen.add_fail('This is not implemented...')
            self.manage_tag_menu(tid)

    def add_tag(self):
        self.screen.print_init('Adding tag')
        name = input('Name: ')
        tid = self.model.create_tag(name)
        self.screen.add_message('tag has been created')
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
