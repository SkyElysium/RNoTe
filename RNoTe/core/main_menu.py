import tkinter as tk
import tkinter.ttk as ttk

import webbrowser

from .config import get_settings, get_path
from .dialogs import show_about_dialog, show_find_dialog


class MainMenu(tk.Menu):
    def __init__(self, master: 'Editor'):

        super().__init__(master)

        self.font_size = tk.IntVar(self, 13)

        self['postcommand'] = self._change_status_of_options

        # Options that need checking the status in "_change_status_of_options"
        self.file_option_checklist = get_settings('close', 'save', 'save_as', 'tab')
        self.edit_option_checklist = get_settings('undo', 'redo', 'copy', 'cut', 'paste', 'select_all', 'find')
        self.view_option_checklist = get_settings('zoom_in', 'zoom_out', 'original_size')

        # File
        self.file_option = tk.Menu(
            self,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7'
        )

        self.file_option.add_command(
            label = get_settings('new'),
            accelerator = 'Ctrl+N',
            command = self.master.custom_notebook.add_tab
        )
        self.file_option.add_separator()
        self.file_option.add_command(
            label = get_settings('open'),
            accelerator = 'Ctrl+O',
            command = self.master.open_file
        )
        self.file_option.add_command(
            label = get_settings('save'),
            accelerator = 'Ctrl+S',
            command = self.master.save_file
        )
        self.file_option.add_command(
            label = get_settings('save_as'),
            accelerator = 'Ctrl+Alt+S',
            command = self.master.save_file_as
        )

        # File List
        self.file_list = tk.Menu(
            self.file_option,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7',
            postcommand = self._get_file_list
        )

        self.file_option.add_cascade(label = get_settings('open_recently'), menu = self.file_list)

        self.file_option.add_separator()

        # Tab List
        self.tab_list = tk.Menu(
            self.file_option,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7',
            postcommand = self._get_tab_list
        )

        self.file_option.add_cascade(label = get_settings('tab'), menu = self.tab_list)

        self.file_option.add_command(
            label = get_settings('close'),
            accelerator = 'Ctrl+F4',
            command = self.master.custom_notebook.safely_close_file
        )
        self.file_option.add_separator()
        self.file_option.add_command(
            label = get_settings('exit'),
            accelerator = 'Alt+F4',
            command = self.master.exiting
        )

        self.add_cascade(label = get_settings('file'), menu = self.file_option)

        # Edit
        self.edit_option = tk.Menu(
            self,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7'
        )

        self.edit_option.add_command(
            label = get_settings('undo'),
            accelerator = 'Ctrl+Z',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.undo()
        )
        self.edit_option.add_command(
            label = get_settings('redo'),
            accelerator = 'Ctrl+Y',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.redo()
        )
        self.edit_option.add_separator()
        self.edit_option.add_command(
            label = get_settings('copy'),
            accelerator = 'Ctrl+C',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.copy()
        )
        self.edit_option.add_command(
            label = get_settings('cut'),
            accelerator = 'Ctrl+X',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.cut()
        )
        self.edit_option.add_command(
            label = get_settings('paste'),
            accelerator = 'Ctrl+V',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.paste()
        )
        self.edit_option.add_separator()
        self.edit_option.add_command(
            label = get_settings('select_all'),
            accelerator = 'Ctrl+A',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.select_all()
        )
        self.edit_option.add_separator()
        self.edit_option.add_command(
            label = get_settings('find'),
            accelerator = 'Ctrl+F',
            command = self.popup_find_dialog
        )

        self.add_cascade(label = get_settings('edit'), menu = self.edit_option)

        # View
        self.view_option = tk.Menu(
            self,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7'
        )

        self.view_option.add_command(
            label = get_settings('zoom_in'),
            accelerator = 'Ctrl++',
            command = self.zoom_in_font
        )
        self.view_option.add_command(
            label = get_settings('zoom_out'),
            accelerator = 'Ctrl+-',
            command = self.zoom_out_font
        )
        self.view_option.add_command(
            label = get_settings('original_size'),
            command = lambda : self.font_size.set(13)
        )

        self.add_cascade(label = get_settings('view'), menu = self.view_option)

        # About
        self.about_option = tk.Menu(
            self,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7'
        )

        self.about_option.add_command(
            label = get_settings('about'),
            command = show_about_dialog
        )
        self.about_option.add_command(
            label = get_settings('feedback'),
            command = lambda : webbrowser.open('https://github.com/SkyElysium/RNoTe/issues/new')
        )

        self.add_cascade(label = get_settings('about'), menu = self.about_option)

    def _change_status_of_options(self):

        status = 'disabled' if not self.master.custom_notebook.tabs() else 'normal'

        for option in ['file', 'edit', 'view']:
            for each in eval(f'self.{option}_option_checklist'):
                eval(f'self.{option}_option.entryconfig("{each}", state = "{status}")')

        try:
            self.master.clipboard_get()
            if self.master.custom_notebook.tabs():
                self.edit_option.entryconfig(get_settings('paste'), state = 'normal')
        except tk.TclError:
            self.edit_option.entryconfig(get_settings('paste'), state = 'disabled')

        self.view_option.entryconfig(
            get_settings('original_size'),
            state = 'disabled' if self.font_size.get() == 13 else 'normal'
        )

    def _get_file_list(self):

        try:
            with open(get_path('file_history'), 'r', encoding = 'utf-8') as f:
                paths = f.read().splitlines()

                if not paths:
                    self.file_option.entryconfig(get_settings('open_recently'), state = 'disabled')

                    return
                else: self.file_option.entryconfig(get_settings('open_recently'), state = 'normal')
        except FileNotFoundError:
            self.file_option.entryconfig(get_settings('open_recently'), state = 'disabled')

            return

        self.file_list.delete('0', 'end')

        for path in reversed(paths):
            self.file_list.add_command(
                label = path,
                command = lambda path = path: self.master.open_file(file_path = path)
            )

        self.file_list.add_separator()
        self.file_list.add_command(label = get_settings('clean_records'), command = self._clean_records)

    def record_new_file(self, file_path):

        with open(get_path('file_history'), 'a+', encoding = 'utf-8') as f:
            f.seek(0)
            paths = f.readlines()

            if file_path + '\n' in paths:
                return

            if len(paths) == 8:  # The max number of records
                paths.pop(0)
                paths.append(file_path + '\n')

                f.truncate(0)

                f.writelines(paths)
            else:
                f.seek(0, 2)
                f.write(file_path + '\n')

    def _clean_records(self):

        with open(get_path('file_history'), 'w', encoding = 'utf-8') as f:
            f.truncate(0)

    def _get_tab_list(self):

        if not self.master.custom_notebook.tabs():
            return

        self.tab_list.delete('0', 'end')

        tabs_id = self.master.custom_notebook.tabs()

        for tab_id in tabs_id:
            tab = self.master.custom_notebook.get_tab(tab_id)
            now_tab_id, _ = self.master.custom_notebook.get_tab()

            tab_name = tab.label

            self.tab_list.add_command(
                label = tab_name,
                command = lambda tab_id = tab_id: self.master.custom_notebook.select(tab_id)
            )

            if tab_id == now_tab_id:
                self.tab_list.entryconfig(tabs_id.index(tab_id), state = 'disabled')

    def zoom_in_font(self, event = None):

        if not self.master.custom_notebook.tabs() or self.font_size.get() == 60:
            return

        self.font_size.set(self.font_size.get() + 1)

    def zoom_out_font(self, event = None):

        if not self.master.custom_notebook.tabs() or self.font_size.get() == 1:
            return

        self.font_size.set(self.font_size.get() - 1)

    def popup_find_dialog(self, event = None):

        show_find_dialog()
