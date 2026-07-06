from typing import Optional

import tkinter as tk
import tkinter.ttk as ttk

import webbrowser

from core.config import *


class MainMenu(tk.Menu):
    def __init__(self, master: tk.Misc) -> None:

        super().__init__(master)

        self.main_notebook = master.custom_notebook
        self.master = master

        self.font_size = tk.IntVar(self, 13)
        self.font_size.trace('w', self._change_font_size)

        self['postcommand'] = self._change_status_of_options

        # Options that need checking the status in "_change_status_of_options"
        self.file_option_checklist = [CLOSE, SAVE, SAVE_AS, TAB]
        self.edit_option_checklist = [UNDO, REDO, COPY, CUT, PASTE, SELECT_ALL]
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
            command = self.main_notebook.add_tab
        )
        self.file_option.add_separator()
        self.file_option.add_command(
            label = OPEN,
            accelerator = 'Ctrl+O',
            command = self.main_notebook.open_file
        )
        self.file_option.add_command(
            label = SAVE,
            accelerator = 'Ctrl+S',
            command = self.main_notebook.save_file
        )
        self.file_option.add_command(
            label = SAVE_AS,
            accelerator = 'Ctrl+Alt+S',
            command = self.main_notebook.save_file_as
        )
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
            command = self.main_notebook.safely_close_file
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
            command = lambda : self.main_notebook.get_tab()[1].undo()
        )
        self.edit_option.add_command(
            label = REDO,
            accelerator = 'Ctrl+Y',
            command = lambda : self.main_notebook.get_tab()[1].redo()
        )
        self.edit_option.add_separator()
        self.edit_option.add_command(
            label = COPY,
            accelerator = 'Ctrl+C',
            command = lambda : self.main_notebook.get_tab()[1].copy()
        )
        self.edit_option.add_command(
            label = CUT,
            accelerator = 'Ctrl+X',
            command = lambda : self.main_notebook.get_tab()[1].cut()
        )
        self.edit_option.add_command(
            label = PASTE,
            accelerator = 'Ctrl+V',
            command = lambda : self.main_notebook.get_tab()[1].paste()
        )
        self.edit_option.add_separator()
        self.edit_option.add_command(
            label = SELECT_ALL,
            accelerator = 'Ctrl+A',
            command = lambda : self.main_notebook.get_tab()[1].select_all()
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
            command = self._popup_about_dialog
        )
        self.about_option.add_command(
            label = REPORT,
            command = self._link_to_issue
        )

        self.add_cascade(label = ABOUT, menu = self.about_option)

    def _change_status_of_options(self) -> None:

        status = 'disabled' if not self.main_notebook.tabs() else 'normal'

        for each in self.file_option_checklist:
            self.file_option.entryconfig(each, state = status)
        for each in self.edit_option_checklist:
            self.edit_option.entryconfig(each, state = status)
        for each in self.view_option_checklist:
            self.view_option.entryconfig(each, state = status)

        try:
            self.master.clipboard_get()
            if self.main_notebook.tabs():
                self.edit_option.entryconfig(PASTE, state = 'normal')
        except tk.TclError:
            self.edit_option.entryconfig(PASTE, state = 'disabled')

    def _get_tab_list(self) -> None:

        if not self.main_notebook.tabs(): return

        self.tab_list.delete('0', 'end')

        list_ = self.main_notebook.tabs()

        for tab_id in list_:
            tab = self.main_notebook.nametowidget(tab_id)
            now_tab_id, _ = self.main_notebook.get_tab()

            tab_name = tab.label

            self.tab_list.add_command(
                label = tab_name,
                command = lambda tab_id = tab_id: self.main_notebook.select(tab_id)
            )

            if tab_id == now_tab_id: self.tab_list.entryconfig(tab_name, state = 'disabled')

    def _change_font_size(self, *args) -> None:

        for tab_id in self.main_notebook.tabs():
            tab = self.main_notebook.nametowidget(tab_id)

            tab.line_number_bar.config(font = ('Consolas', self.font_size.get()))
            tab.text.config(font = ('Consolas', self.font_size.get()))

    def zoom_in_font(self, event: Optional[tk.Event] = None) -> None:

        if self.font_size.get() == 60: return

        self.font_size.set(self.font_size.get() + 1)

    def zoom_out_font(self, event: Optional[tk.Event] = None) -> None:

        if self.font_size.get() == 1: return

        self.font_size.set(self.font_size.get() - 1)

    def _popup_about_dialog(self) -> None:

        dialog = tk.Toplevel()
        dialog.title(TITLE)

        x, y = self.master.winfo_x(), self.master.winfo_y()
        dialog.geometry('350x120')
        dialog.geometry(f'+{x + 200}+{y + 200}')

        self.master.wm_attributes('-disabled', True)
        dialog.bind('<Destroy>', lambda _: self.master.wm_attributes('-disabled', False))

        dialog.resizable(False, False)
        dialog.focus()

        tk.Label(dialog, text = MAIN_WINDOW_TITLE, font = ('Consolas', 15)).pack()
        ttk.Separator(dialog).pack(fill = 'x')
        tk.Message(dialog, text = FIRST_INFO, width = 600).pack()
        tk.Message(dialog, text = SECOND_INFO, width = 600, justify = 'center').pack(side = 'bottom')

    def _link_to_issue(self) -> None:

        webbrowser.open(ISSUE_URL)
