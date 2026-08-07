from typing import Optional

import tkinter as tk
import tkinter.ttk as ttk

import webbrowser

from core.constants import *
from core.dialogs import FindDialog, AboutDialog


class MainMenu(tk.Menu):
    def __init__(self, master: tk.Misc) -> None:

        super().__init__(master)

        self.master = master

        self.font_size = tk.IntVar(self, 13)
        self.font_size.trace('w', self._change_font_size)

        self['postcommand'] = self._change_status_of_options

        # Options that need checking the status in "_change_status_of_options"
        self.file_option_checklist = [CLOSE, SAVE, SAVE_AS, TAB]
        self.edit_option_checklist = [UNDO, REDO, COPY, CUT, PASTE, SELECT_ALL, FIND]
        self.view_option_checklist = [ZOOM_IN, ZOOM_OUT, ORIGINAL_SIZE]

        # File
        self.file_option = tk.Menu(
            self,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7'
        )

        self.file_option.add_command(
            label = NEW,
            accelerator = 'Ctrl+N',
            command = self.master.custom_notebook.add_tab
        )
        self.file_option.add_separator()
        self.file_option.add_command(
            label = OPEN,
            accelerator = 'Ctrl+O',
            command = self.master.custom_notebook.open_file
        )
        self.file_option.add_command(
            label = SAVE,
            accelerator = 'Ctrl+S',
            command = self.master.custom_notebook.save_file
        )
        self.file_option.add_command(
            label = SAVE_AS,
            accelerator = 'Ctrl+Alt+S',
            command = self.master.custom_notebook.save_file_as
        )

        # File List
        self.file_list = tk.Menu(
            self.file_option,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7',
            postcommand = self._get_file_list
        )

        self.file_option.add_cascade(label = OPEN_RECENTLY, menu = self.file_list)

        self.file_option.add_separator()

        # Tab List
        self.tab_list = tk.Menu(
            self.file_option,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7',
            postcommand = self._get_tab_list
        )

        self.file_option.add_cascade(label = TAB, menu = self.tab_list)

        self.file_option.add_command(
            label = CLOSE,
            accelerator = 'Ctrl+F4',
            command = self.master.custom_notebook.safely_close_file
        )
        self.file_option.add_separator()
        self.file_option.add_command(
            label = EXIT,
            accelerator = 'Alt+F4',
            command = self.master.exiting
        )

        self.add_cascade(label = FILE, menu = self.file_option)

        # Edit
        self.edit_option = tk.Menu(
            self,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7'
        )

        self.edit_option.add_command(
            label = UNDO,
            accelerator = 'Ctrl+Z',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.undo()
        )
        self.edit_option.add_command(
            label = REDO,
            accelerator = 'Ctrl+Y',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.redo()
        )
        self.edit_option.add_separator()
        self.edit_option.add_command(
            label = COPY,
            accelerator = 'Ctrl+C',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.copy()
        )
        self.edit_option.add_command(
            label = CUT,
            accelerator = 'Ctrl+X',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.cut()
        )
        self.edit_option.add_command(
            label = PASTE,
            accelerator = 'Ctrl+V',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.paste()
        )
        self.edit_option.add_separator()
        self.edit_option.add_command(
            label = SELECT_ALL,
            accelerator = 'Ctrl+A',
            command = lambda : self.master.custom_notebook.get_tab()[1].text_panel.select_all()
        )
        self.edit_option.add_separator()
        self.edit_option.add_command(
            label = FIND,
            accelerator = 'Ctrl+F',
            command = self.popup_find_dialog
        )

        self.add_cascade(label = EDIT, menu = self.edit_option)

        # View
        self.view_option = tk.Menu(
            self,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7'
        )

        self.view_option.add_command(
            label = ZOOM_IN,
            accelerator = 'Ctrl++',
            command = self.zoom_in_font
        )
        self.view_option.add_command(
            label = ZOOM_OUT,
            accelerator = 'Ctrl+-',
            command = self.zoom_out_font
        )
        self.view_option.add_command(
            label = ORIGINAL_SIZE,
            command = lambda : self.font_size.set(13)
        )

        self.add_cascade(label = VIEW, menu = self.view_option)

        # About
        self.about_option = tk.Menu(
            self,
            tearoff = False,
            activeforeground = 'black',
            activebackground = '#91c9f7'
        )

        self.about_option.add_command(
            label = ABOUT,
            command = lambda : AboutDialog(self.master)
        )
        self.about_option.add_command(
            label = FEEDBACK,
            command = lambda : webbrowser.open(ISSUE_URL)
        )

        self.add_cascade(label = ABOUT, menu = self.about_option)

    def _change_status_of_options(self) -> None:

        status = 'disabled' if not self.master.custom_notebook.tabs() else 'normal'

        for option in ['file', 'edit', 'view']:
            for each in eval(f'self.{option}_option_checklist'):
                eval(f'self.{option}_option.entryconfig("{each}", state = "{status}")')

        try:
            self.master.clipboard_get()
            if self.master.custom_notebook.tabs():
                self.edit_option.entryconfig(PASTE, state = 'normal')
        except tk.TclError:
            self.edit_option.entryconfig(PASTE, state = 'disabled')

        self.view_option.entryconfig(ORIGINAL_SIZE,
                                    state = 'disabled' if self.font_size.get() == 13 else 'normal')

    def _get_file_list(self) -> None:

        try:
            with open('data/config/recent_files.txt', 'r', encoding = 'utf-8') as f:
                paths = f.read().splitlines()

                if not paths:
                    self.file_option.entryconfig(OPEN_RECENTLY, state = 'disabled')

                    return
                else: self.file_option.entryconfig(OPEN_RECENTLY, state = 'normal')
        except FileNotFoundError:
            self.file_option.entryconfig(OPEN_RECENTLY, state = 'disabled')

            return

        self.file_list.delete('0', 'end')

        for path in reversed(paths):
            self.file_list.add_command(
                label = path,
                command = lambda path = path: self.master.custom_notebook.open_file(file_path = path)
            )

        self.file_list.add_separator()
        self.file_list.add_command(label = CLEAN_RECORDS, command = self._clean_records)

    def record_new_file(self, file_path: str) -> None:

        with open('data/config/recent_files.txt', 'a+', encoding = 'utf-8') as f:
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

    def _clean_records(self) -> None:

        with open('data/config/recent_files.txt', 'w', encoding = 'utf-8') as f:
            f.truncate(0)

    def _get_tab_list(self) -> None:

        if not self.master.custom_notebook.tabs():
            return

        self.tab_list.delete('0', 'end')

        tabs_id = self.master.custom_notebook.tabs()

        for tab_id in tabs_id:
            tab = self.master.custom_notebook.nametowidget(tab_id)
            now_tab_id, _ = self.master.custom_notebook.get_tab()

            tab_name = tab.label

            self.tab_list.add_command(
                label = tab_name,
                command = lambda tab_id = tab_id: self.master.custom_notebook.select(tab_id)
            )

            if tab_id == now_tab_id: self.tab_list.entryconfig(tabs_id.index(tab_id), state = 'disabled')

    def _change_font_size(self, *args) -> None:

        for tab_id in self.master.custom_notebook.tabs():
            tab = self.master.custom_notebook.nametowidget(tab_id)

            tab.line_number_bar.config(font = ('Consolas', self.font_size.get()))
            tab.text_panel.config(font = ('Consolas', self.font_size.get()))

    def zoom_in_font(self, event: Optional[tk.Event] = None) -> None:

        if not self.master.custom_notebook.tabs() or self.font_size.get() == 60:
            return

        self.font_size.set(self.font_size.get() + 1)

    def zoom_out_font(self, event: Optional[tk.Event] = None) -> None:

        if not self.master.custom_notebook.tabs() or self.font_size.get() == 1:
            return

        self.font_size.set(self.font_size.get() - 1)

    def popup_find_dialog(self, event: Optional[tk.Event] = None) -> None:

        FindDialog(self.master)
