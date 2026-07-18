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

        # Config of "find"
        self.pos_list = []
        self.current = -1
        self.is_find_alive = False
        self.is_regexp_on = False
        self.idx = tk.StringVar(self, '0/0')

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

    def _get_file_list(self) -> None:

        with open('data/config/recent_files.txt', 'r', encoding = 'utf-8') as f:
            paths = f.read().splitlines()

            if not paths:
                self.file_option.entryconfig(OPEN_RECENTLY, state = 'disabled')

                return
            else: self.file_option.entryconfig(OPEN_RECENTLY, state = 'normal')

        self.file_list.delete('0', 'end')

        for path in reversed(paths):
            self.file_list.add_command(
                label = path,
                command = lambda path = path: self.main_notebook.open_file(file_path = path)
            )

    def add_new_file_record(self, file_path: str) -> None:

        # TODO: suggested to use cache (read once)

        with open('data/config/recent_files.txt', 'a+', encoding = 'utf-8') as f:
            f.seek(0)
            paths = f.read().splitlines()

            if file_path in paths: return

            if len(paths) == 5:
                paths.pop(0)
                paths.append(file_path + '\n')

                f.truncate(0)

                f.writelines(paths)
            else:
                f.seek(0, 2)
                f.write(file_path + '\n')

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

        if not self.main_notebook.tabs(): return
        if self.font_size.get() == 60: return

        self.font_size.set(self.font_size.get() + 1)

    def zoom_out_font(self, event: Optional[tk.Event] = None) -> None:

        if not self.main_notebook.tabs(): return
        if self.font_size.get() == 1: return

        self.font_size.set(self.font_size.get() - 1)

    def popup_find_dialog(self, event: tk.Event = None) -> None:

        if not self.main_notebook.tabs(): return

        if self.is_find_alive: return
        self.is_find_alive = True

        dialog = tk.Toplevel()
        dialog.title(TITLE_FIND)

        x, y = self.master.winfo_x(), self.master.winfo_y()
        dialog.geometry('330x30')
        dialog.geometry(f'+{x}+{y}')

        dialog.attributes('-toolwindow', True)
        dialog.attributes('-topmost', True)

        dialog.resizable(False, False)
        dialog.focus()

        dialog.bind('<FocusOut>', lambda event: self._focus_out_of_find(find_up_button, find_down_button))
        dialog.bind('<Destroy>', self._exit)

        regexp = ttk.Button(
            dialog,
            text = '.*' if not self.is_regexp_on else '.-',
            width = 2,
            takefocus = False,
            padding = 0.1,
            command = lambda : self._change_status_of_regexp(regexp),
        )
        regexp.place(x = 20, y = 2)

        find_entry = ttk.Entry(dialog)
        find_entry.place(x = 50, y = 3)

        self.pos_list.clear()
        self.current = -1

        find_entry.bind(
            '<Return>',
            lambda event: self._search_for_words(find_entry, find_up_button, find_down_button)
        )

        index_label = tk.Label(dialog, textvariable = self.idx)
        index_label.place(x = 215, y = 3)

        find_up_button = ttk.Button(
            dialog,
            text = '<',
            width = 2,
            takefocus = False,
            command = self._search_up,
            state = 'disabled'
        )
        find_up_button.place(x = 260, y = 1)

        find_down_button = ttk.Button(
            dialog,
            text = '>',
            width = 2,
            takefocus = False,
            command = self._search_down,
            state = 'disabled'
        )
        find_down_button.place(x = 285, y = 1)

    def _change_status_of_regexp(self, regexp_button: ttk.Button) -> None:

        if not self.is_regexp_on:
            self.is_regexp_on = True
            regexp_button.config(text = '.-')
        else:
            self.is_regexp_on = False
            regexp_button.config(text = '.*')

    def _search_for_words(self, entry: ttk.Entry, up: ttk.Button, down: ttk.Button) -> None:

        _, tab = self.main_notebook.get_tab()
        tab.text.tag_remove('search', '1.0', 'end')

        word = entry.get()
        length = tk.StringVar()
        start = '1.0'

        self.current = -1
        self.main_notebook.get_tab()[1].text.tag_remove('search', '1.0', 'end')
        self.main_notebook.get_tab()[1].text.tag_remove('search_selected', '1.0', 'end')

        self.pos_list.clear()

        while word:
            try:
                pos = tab.text.search(word, start, 'end', regexp = self.is_regexp_on, count = length)
            except: pass  # When RegExp grammar is wrong, enter.

            if not pos: break

            self.pos_list.append((pos, f'{pos}+{length.get()}c'))
            tab.text.tag_add('search', pos, f'{pos}+{length.get()}c')

            start = f'{pos}+{length.get()}c'

        state = 'normal' if self.pos_list else 'disabled'

        up.config(state = state)
        down.config(state = state)

        self.idx.set(f'0/{len(self.pos_list)}')

    def _search_up(self) -> None:

        if self.current >= 0:
            if self.current != 0: self.current -= 1

            self._dump_to_word()

    def _search_down(self) -> None:

        if len(self.pos_list) - 1 >= self.current:
            if len(self.pos_list) - 1 != self.current: self.current += 1

            self._dump_to_word()

    def _dump_to_word(self) -> None:

        _, tab = self.main_notebook.get_tab()

        tab.text.see(self.pos_list[self.current][0])
        tab.line_number_bar.scroll_when_searching()

        tab.text.tag_remove('search_selected', '1.0', 'end')
        tab.text.tag_add('search_selected', self.pos_list[self.current][0], self.pos_list[self.current][1])

        self.idx.set(f'{self.current + 1}/{len(self.pos_list)}')

    def _focus_out_of_find(self, up: ttk.Button, down: ttk.Button) -> None:

        up.config(state = 'disabled')
        down.config(state = 'disabled')

        self.main_notebook.get_tab()[1].text.tag_remove('search', '1.0', 'end')
        self.main_notebook.get_tab()[1].text.tag_remove('search_selected', '1.0', 'end')

        self.idx.set('0/0')

    def _exit(self, event: tk.Event = None) -> None:

        self.is_find_alive = False

        self.main_notebook.get_tab()[1].text.tag_remove('search', '1.0', 'end')
        self.main_notebook.get_tab()[1].text.tag_remove('search_selected', '1.0', 'end')

        self.idx.set('0/0')

    def _popup_about_dialog(self) -> None:

        dialog = tk.Toplevel()
        dialog.title(TITLE_ABOUT)

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
