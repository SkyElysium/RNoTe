import tkinter as tk
import tkinter.ttk as ttk

from core.constants import *


class Dialog(tk.Toplevel):
    def __init__(self, master: tk.Misc) -> None:

        super().__init__(master)

        self.master = master

        self.transient(self.master)

        self.attributes('-topmost', True)
        self.resizable(False, False)

        self.focus()

    def set_dialog(self, dialog_title: str, dialog_size: str) -> None:

        win_x = self.master.winfo_x()
        win_y = self.master.winfo_y()

        win_width = self.master.winfo_width()
        win_height = self.master.winfo_height()

        width, height = dialog_size.split('x')

        dx = int(win_width / 2 - int(width) / 2 + win_x)
        dy = int(win_height / 2 - int(height) / 2 + win_y)

        self.title(dialog_title)
        self.geometry(f'{dialog_size}+{dx}+{dy}')


class FindDialog(Dialog):

    _DIALOG_TITLE = '查找'
    _DIALOG_SIZE = '330x30'

    instance = None
    is_alive = False

    def __new__(cls, *args) -> object:

        if cls.instance is None:
            cls.instance = object.__new__(cls)

        return cls.instance

    def __init__(self, master: tk.Misc) -> None:

        if self.is_alive:
            self.instance.focus()

            return

        self.is_alive = True

        super().__init__(master)

        self.master = master

        self.set_dialog(self._DIALOG_TITLE, self._DIALOG_SIZE)

        self.word_indexes = []
        self.current = -1
        self.present_pos = tk.StringVar(self, '0/0')

        self.is_regexp_on = False

        self.bind('<FocusOut>', self._focus_out_of_dialog)
        self.bind('<Destroy>', self._exiting)

        self._interface()

    def _interface(self) -> None:

        self.regexp_toggle = ttk.Button(
            self,
            text = '.*' if not self.is_regexp_on else '.-',
            width = 2,
            takefocus = False,
            padding = 0.1,
            command = self._change_status_of_regexp,
        )
        self.regexp_toggle.place(x = 20, y = 2)

        self.search_entry = ttk.Entry(self)
        self.search_entry.place(x = 50, y = 3)

        self.search_entry.bind('<Return>', self._search_for_words)

        self.present_pos_label = tk.Label(self, textvariable = self.present_pos)
        self.present_pos_label.place(x = 215, y = 3)

        self.search_up_button = ttk.Button(
            self,
            text = '<',
            width = 2,
            takefocus = False,
            command = self._search_up,
            state = 'disabled'
        )
        self.search_up_button.place(x = 260, y = 1)

        self.search_down_button = ttk.Button(
            self,
            text = '>',
            width = 2,
            takefocus = False,
            command = self._search_down,
            state = 'disabled'
        )
        self.search_down_button.place(x = 285, y = 1)

    def _change_status_of_regexp(self) -> None:

        if not self.is_regexp_on:
            self.is_regexp_on = True
            self.regexp_toggle.config(text = '.-')
        else:
            self.is_regexp_on = False
            self.regexp_toggle.config(text = '.*')

    def _search_for_words(self, event: tk.Event) -> None:

        if not self.master.custom_notebook.tabs():
            return

        _, tab = self.master.custom_notebook.get_tab()

        tab.text_panel.tag_remove('searched', '1.0', 'end')
        tab.text_panel.tag_remove('selected', '1.0', 'end')

        text = self.search_entry.get()
        start = '1.0'

        length = tk.StringVar()

        self.current = -1
        self.word_indexes.clear()

        while text:
            try:
                start_pos = tab.text_panel.search(text, start, 'end', regexp = self.is_regexp_on, count = length)
            except tk.TclError:
                start_pos = ''  # When RegExp grammar is wrong, enter.

            if not start_pos:
                self.search_entry.bell()

                break

            end_pos = f'{start_pos}+{length.get()}c'

            self.word_indexes.append((start_pos, end_pos))
            tab.text_panel.tag_add('searched', start_pos, end_pos)

            start = end_pos

        state = 'normal' if self.word_indexes else 'disabled'

        self.search_up_button.config(state = state)
        self.search_down_button.config(state = state)

        self.present_pos.set(f'0/{len(self.word_indexes)}')

    def _search_up(self) -> None:

        if self.current >= 0:
            if self.current != 0:
                self.current -= 1

            self._dump_to_word()

    def _search_down(self) -> None:

        if len(self.word_indexes) - 1 >= self.current:
            if len(self.word_indexes) - 1 != self.current:
                self.current += 1

            self._dump_to_word()

    def _dump_to_word(self) -> None:

        _, tab = self.master.custom_notebook.get_tab()

        tab.text_panel.see(self.word_indexes[self.current][0])
        tab.line_number_bar.scroll_when_searching()

        tab.text_panel.tag_remove('searched', '1.0', 'end')
        tab.text_panel.tag_add('selected', self.word_indexes[self.current][0], self.word_indexes[self.current][1])

        self.present_pos.set(f'{self.current + 1}/{len(self.word_indexes)}')

    def _focus_out_of_dialog(self, event: tk.Event) -> None:

        self.search_up_button.config(state = 'disabled')
        self.search_down_button.config(state = 'disabled')

        self.present_pos.set('0/0')

        if self.master.custom_notebook.tabs():
            _, tab = self.master.custom_notebook.get_tab()

            tab.text_panel.tag_remove('searched', '1.0', 'end')
            tab.text_panel.tag_remove('selected', '1.0', 'end')

    def _exiting(self, event: tk.Event) -> None:

        if self.master.custom_notebook.tabs():
            _, tab = self.master.custom_notebook.get_tab()

            tab.text_panel.tag_remove('searched', '1.0', 'end')
            tab.text_panel.tag_remove('selected', '1.0', 'end')

        self.instance = None
        self.is_alive = False


class AboutDialog(Dialog):

    _DIALOG_TITLE = '关于'
    _DIALOG_SIZE  = '350x120'

    def __init__(self, master: tk.Misc) -> None:

        super().__init__(master)

        self.master = master

        self.set_dialog(self._DIALOG_TITLE, self._DIALOG_SIZE)

        self.master.wm_attributes('-disabled', True)
        self.bind('<Destroy>', lambda event: self.master.wm_attributes('-disabled', False))

        self._interface()

    def _interface(self) -> None:

        tk.Label(self, text = MAIN_WINDOW_TITLE, font = ('Consolas', 15)).pack()

        tk.Message(self, text = REPO_URL, width = 600, fg = 'blue').pack()
        tk.Message(self, text = COPYRIGHT, width = 600, justify = 'center').pack()
