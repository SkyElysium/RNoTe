from __future__ import annotations
from typing import Optional, Tuple

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

from pathlib import Path

from core.constants import *
from core.line_number_bar import LineNumberBar


class CustomNotebook(ttk.Notebook):
    def __init__(self, master: tk.Misc) -> None:

        super().__init__(master)

        self.main_window = master

        # Create the "close" button.
        self.close_image = tk.PhotoImage(file = 'data/close.png')

        self.custom_style = ttk.Style()

        # Regard "close" as a command that lets the tab destory.
        self.custom_style.element_create('close', 'image', self.close_image)

        self.custom_style.layout('CustomNotebook', [('CustomNotebook.client', {'sticky': 'nswe'})])
        self.custom_style.layout('CustomNotebook.Tab', CUSTOM_NOTEBOOK_STYLE)

        self['style'] = 'CustomNotebook'

        # X Scrollbar in each tab
        self.custom_style.element_create("Custom.Horizontal.TScrollbar.trough", "from", "clam")
        self.custom_style.element_create("Custom.Horizontal.TScrollbar.thumb", "from", "clam")
        self.custom_style.element_create("Custom.Horizontal.TScrollbar.grip", "from", "clam")

        self.custom_style.layout("Custom.Horizontal.TScrollbar", CUSTOM_X_SCROLLBAR_STYLE)

        self.custom_style.configure("Custom.Horizontal.TScrollbar",
            gripcount = 0,
            background = "#c0c0c0",
            troughcolor = '#f0f0f0',
            bordercolor = "#f0f0f0",
            lightcolor = '#c0c0c0',
            darkcolor = '#c0c0c0',
            arrowsize = 6
        )

        self.bind('<Button-1>', self._on_pressing_close)
        self.bind('<B1-Motion>', self._move_selected_tab)

        self.bind('<<NotebookTabChanged>>', self._update_info_on_title)

    def _on_pressing_close(self, event: tk.Event) -> None:

        if self.identify(event.x, event.y) == 'close':
            tab_id = f'@{event.x}, {event.y}'

            self.safely_close_file(tab_id = tab_id)

    def safely_close_file(self, event: Optional[tk.Event] = None, tab_id: str = '') -> None:

        if not self.tabs():
            return

        tab = self.tabs()[self.index(tab_id)] if tab_id else self.select()

        if self.nametowidget(tab).text_panel.edit_modified():
            reply = messagebox.askyesnocancel(
                title = MAIN_WINDOW_TITLE,
                message = '是否在关闭之前保存文件？'
            )
            if reply and self.save_file(file_path = self.nametowidget(tab).path) == 'NotSaved':
                return
            elif reply is None:
                return

        if self.nametowidget(tab).path:
            self.main_window.main_menu.record_new_file(self.nametowidget(tab).path)

        self.remove_tab(tab_id = tab_id)

    def _move_selected_tab(self, event: tk.Event) -> None:

        # Use try-except to prevent the cursor from moving on nothing.
        try:
            tab_index = self.index(f'@{event.x}, {event.y}')

            self.insert(tab_index, self.select())
        except tk.TclError:
            pass

    def _update_info_on_title(self, event: Optional[tk.Event] = None) -> None:

        self.main_window.title(MAIN_WINDOW_TITLE)

        if not self.tabs():
            return

        _, text_tab = self.get_tab()

        if text_tab.path:
            self.main_window.title(f'{MAIN_WINDOW_TITLE} - {text_tab.path}')

    def add_tab(self, event: Optional[tk.Event] = None, tab_name: str = '未命名') -> TextTab:

        text_tab = TextTab(self)
        text_tab.label = tab_name

        self.add(text_tab, text = tab_name)

        self.select(text_tab)

        return text_tab

    def remove_tab(self, event: Optional[tk.Event] = None, tab_id: str = '') -> None:

        # TabId for @x, y should be turned into ".!".
        tab = self.tabs()[self.index(tab_id)] if tab_id else self.select()

        self.main_window.main_menu.font_size.trace_vdelete('w', self.nametowidget(tab).font_tracker)

        self.forget(tab)
        self.nametowidget(tab).destroy()

        self._update_info_on_title()

    def get_tab(self) -> Tuple[str, TextTab]:

        tab = self.select()
        text_tab = self.nametowidget(tab)

        return tab, text_tab

    def open_file(self, event: Optional[tk.Event] = None, file_path: str = '') -> None:

        path = filedialog.askopenfilename(
            title = f'打开',
            filetypes = [('文本文档', '*.txt'), ('所有类型', '*.*')]
        ) if not file_path else file_path

        if not path:
            return

        try:
            file = Path(path)

            if not file.exists():
                messagebox.showwarning(
                    title = MAIN_WINDOW_TITLE,
                    message = '打开的文件路径不存在'
                )
                return

            text = file.read_text(encoding = 'utf-8')

            text_tab = self.add_tab(tab_name = file.name)
            text_tab.text_panel.insert('end', text)
        except UnicodeDecodeError:
            messagebox.showerror(
                title = MAIN_WINDOW_TITLE,
                message = '无法打开此文件，因为不是 UTF-8 格式，或者这是一个程序文件'
            )

            return

        text_tab.path = path
        text_tab.label = file.name

        text_tab.text_panel.edit_modified(False)

        text_tab.text_panel.mark_set('insert', '1.0')
        text_tab.text_panel.focus_set()

        text_tab.line_number_bar.update_line_number()

    def save_file(self, event: Optional[tk.Event] = None, file_path: str = '') -> Optional[str]:

        if not self.tabs():
            return

        _, text_tab = self.get_tab()

        if file_path:
            file = Path(file_path)
        elif text_tab.path:
            file = Path(text_tab.path)
        else:
            self.save_file_as()

            return 'NotSaved' if not text_tab.path else None

        text = text_tab.text_panel.get('1.0', 'end-1c')  # No self adding "new line".
        file.write_text(text, encoding = 'utf-8')

        text_tab.text_panel.edit_modified(False)

    def save_file_as(self, event: Optional[tk.Event] = None) -> None:

        if not self.tabs():
            return

        path = filedialog.asksaveasfilename(
            title = '另存为...',
            defaultextension = '.txt',
            filetypes = [('文本文档', '*.txt'), ('所有类型', '*.*')]
        )

        if not path:
            return

        tab, text_tab = self.get_tab()

        if text_tab.path:  # When the file has been, enter.
            self.save_file(file_path = path)

            return

        text_tab.path = path
        text_tab.label = Path(path).name

        self.save_file()

        self.tab(tab, text = text_tab.label)
        self._update_info_on_title()


class TextTab(tk.Frame):
    def __init__(self, master: tk.Misc) -> None:

        super().__init__(master)

        self.notebook = master

        # Tab Info
        self.path = ''
        self.label = ''  # The label of tab

        self.font_size = self.notebook.main_window.main_menu.font_size
        self.font_tracker = self.font_size.trace('w', self._change_font_size)

        # Interface
        self.grid_columnconfigure(1, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        self.line_number_bar = LineNumberBar(self, self.font_size)
        self.line_number_bar.grid(row = 0, column = 0, rowspan = 2, sticky = 'ns')

        self.text_panel = TextPanel(self, self.font_size)
        self.text_panel.grid(row = 0, column = 1, sticky = 'nsew')

        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.grid(row = 0, column = 2, sticky = 'ns')

        self.x_scrollbar = ttk.Scrollbar(self, orient = 'horizontal', style = 'Custom.Horizontal.TScrollbar')
        self.x_scrollbar.grid(row = 0, column = 1, sticky = 'sew')

        self.text_panel['xscrollcommand'] = self.text_panel._is_out_of_text
        self.text_panel['yscrollcommand'] = self.scrollbar.set

        self.x_scrollbar.config(command = self.text_panel.xview)
        self.scrollbar.config(command = self.line_number_bar.scroll)

        self.line_number_bar.update_line_number()

    def delay_to_update_line_number(self, event: tk.Event) -> None:

        # The timer prevents from being called before executing "enter".
        self.after(1, self.line_number_bar.update_line_number)

    def delay_to_highlight(self, event: tk.Event = None) -> None:

        # The timer prevents from being called before executing "click".
        self.after(1, self.line_number_bar.update_highlight_current_line)

    def _change_font_size(self, *args) -> None:

        self.line_number_bar.config(font = ('Consolas', self.font_size.get()))
        self.text_panel.config(font = ('Consolas', self.font_size.get()))

class TextPanel(tk.Text):
    def __init__(self, master: tk.Misc, font_size: tk.IntVar) -> None:

        super().__init__(master)

        self.master = master

        self.config(
            wrap = 'none',
            undo = True,
            bd = 0,
            font = ('Consolas', font_size.get()),
            selectbackground = '#d3e9fc',
            selectforeground = 'black'
        )

        self.tag_config('searched', background = '#caebcb')
        self.tag_config('selected', underline = True)

        self.bind('<Button-3>', self._popup_menu)
        self.bind('<Control-o>', self._ctrl_o)
        self.bind('<<Modified>>', self._text_is_changed)

        # For highlighting the current line
        self.bind('<Button-1>', self.master.delay_to_highlight)

        # For the line number bar
        self.bind('<B2-Motion>', self._b2_motion)
        self.bind('<<Selection>>', self.master.line_number_bar.scroll_when_selecting)
        self.bind('<Any-KeyPress>', self.master.delay_to_update_line_number)

        self.bind('<MouseWheel>', self.master.line_number_bar.wheel)

        self._right_click_menu()

    def _right_click_menu(self) -> None:

        self.menu = tk.Menu(self, tearoff = False, activeforeground = 'black', activebackground = '#91c9f7')

        self.menu.add_command(label = COPY, accelerator = 'Ctrl+C', command = self.copy)
        self.menu.add_command(label = CUT, accelerator = 'Ctrl+X', command = self.cut)
        self.menu.add_command(label = PASTE, accelerator = 'Ctrl+V', command = self.paste)
        self.menu.add_separator()
        self.menu.add_command(label = COPY_PRESENT_PATH, command = self._copy_file_path)

    def _popup_menu(self, event: tk.Event) -> None:

        self.focus_set()
        self.mark_set('insert', f'@{event.x}, {event.y}')

        self.master.delay_to_highlight()

        self._check_status_of_options()

        self.menu.post(event.x_root, event.y_root)

    def _check_status_of_options(self) -> None:

        if self.master.path:
            self.menu.entryconfig(COPY_PRESENT_PATH, state = 'normal')
        else:
            self.menu.entryconfig(COPY_PRESENT_PATH, state = 'disabled')

        try:
            self.master.notebook.main_window.clipboard_get()
            self.menu.entryconfig(PASTE, state = 'normal')
        except tk.TclError:
            self.menu.entryconfig(PASTE, state = 'disabled')

    def copy(self) -> None:

        if not self.master.notebook.tabs():
            return

        self.event_generate('<<Copy>>')

    def cut(self) -> None:

        if not self.master.notebook.tabs():
            return

        self.event_generate('<<Cut>>')

        self.master.line_number_bar.update_line_number()

    def paste(self) -> None:

        if not self.master.notebook.tabs():
            return

        self.event_generate('<<Paste>>')

        self.master.line_number_bar.update_line_number()

    def select_all(self) -> None:

        if not self.master.notebook.tabs():
            return

        self.event_generate('<<SelectAll>>')

    def undo(self) -> None:

        if not self.master.notebook.tabs():
            return

        self.event_generate('<<Undo>>')

        self.master.line_number_bar.update_line_number()

    def redo(self) -> None:

        if not self.master.notebook.tabs():
            return

        self.text_panel.event_generate('<<Redo>>')

        self.line_number_bar.update_line_number()

    def _copy_file_path(self) -> None:

        self.master.notebook.main_window.clipboard_clear()
        self.master.notebook.main_window.clipboard_append(self.master.path)

    def _b2_motion(self, event: tk.Event) -> str:

        return 'break'

    def _ctrl_o(self, event: tk.Event) -> str:

        # Tkinter has bound ctrl+o inside "Text".
        self.master.notebook.open_file()

        return 'break'

    def _is_out_of_text(self, upper, lower) -> None:

        if self.xview() != (0.0, 1.0):
            self.master.x_scrollbar.lift(self)
        else:
            self.master.x_scrollbar.lower(self)

        self.master.x_scrollbar.set(upper, lower)

    def _text_is_changed(self, event: tk.Event) -> None:

        if self.edit_modified():
            self.master.notebook.tab(self.master.notebook.get_tab()[0], text = f'*{self.master.label}')
        else:
            self.master.notebook.tab(self.master.notebook.get_tab()[0], text = self.master.label)
