from __future__ import annotations

from typing import Optional, Tuple

import tkinter as tk
import tkinter.ttk as ttk

from tkinter import filedialog, messagebox
from pathlib import Path

from core.config import *
from core.line_number_bar import LineNumberBar


class CustomNotebook(ttk.Notebook):
    def __init__(self, master: tk.Misc) -> None:

        super().__init__(master)

        self.main_window = master

        # Create the closing button.
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

        # Binding part
        self.bind('<Button-1>', self._on_pressing_close)
        self.bind('<B1-Motion>', self._move_selected_tab)

        self.bind('<<NotebookTabChanged>>', self._update_info_on_title)

    def _on_pressing_close(self, event: tk.Event) -> None:

        if self.identify(event.x, event.y) == 'close':
            tab_id = f'@{event.x}, {event.y}'

            self.safely_close_file(tab_id = tab_id)

    def safely_close_file(self, event: Optional[tk.Event] = None, tab_id: str = '') -> None:

        tab = self.tabs()[self.index(tab_id)] if tab_id else self.select()

        if self.nametowidget(tab).text.edit_modified():
            reply = messagebox.askyesnocancel(
                title = MAIN_WINDOW_TITLE,
                message = '是否在关闭之前保存文件？'
            )
            if reply:
                if self.save_file(file_path = self.nametowidget(tab).path) == 'NotSaved': return
            if reply is None: return

        self.remove_tab(tab_id = tab_id)

    def _move_selected_tab(self, event: tk.Event) -> None:

        # Use try-except to prevent the cursor from moving on nothing.
        try:
            tab_index = self.index(f'@{event.x}, {event.y}')

            self.insert(tab_index, self.select())
        except tk.TclError: pass

    def _update_info_on_title(self, event: Optional[tk.Event] = None) -> None:

        self.main_window.title(MAIN_WINDOW_TITLE)

        if not self.tabs(): return

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

        self.forget(tab)
        self.nametowidget(tab).destroy()

        self._update_info_on_title()

    def get_tab(self) -> Tuple[str, TextTab]:

        tab = self.select()
        text_tab = self.nametowidget(tab)

        return tab, text_tab

    def open_file(self, event: Optional[tk.Event] = None) -> None:

        path = filedialog.askopenfilename(
            title = f'打开',
            filetypes = [('文本文档', '*.txt'), ('所有类型', '*.*')]
        )

        if not path: return

        try:
            file = Path(path)
            text = file.read_text(encoding = 'utf-8')

            text_tab = self.add_tab(tab_name = file.name)
            text_tab.text.insert('end', text)
        except UnicodeDecodeError:
            messagebox.showerror(
                title = MAIN_WINDOW_TITLE,
                message = '无法打开此文件，因为不是 UTF-8 格式，或者这是一个程序文件'
            )

            return

        text_tab.path = path
        text_tab.label = file.name

        text_tab.text.edit_modified(False)

        text_tab.text.mark_set('insert', '1.0')
        text_tab.text.focus_set()

        text_tab.line_number_bar.update_line_number()

    def save_file(self, event: Optional[tk.Event] = None, file_path: str = '') -> Optional[str]:

        _, text_tab = self.get_tab()

        if file_path:
            file = Path(file_path)
        elif text_tab.path:
            file = Path(text_tab.path)
        else:
            self.save_file_as()

            return 'NotSaved' if not text_tab.path else None

        text = text_tab.text.get('1.0', 'end-1c')  # No self adding "new line".
        file.write_text(text, encoding = 'utf-8')

        text_tab.text.edit_modified(False)

    def save_file_as(self, event: Optional[tk.Event] = None) -> None:

        path = filedialog.asksaveasfilename(
            title = '另存为...',
            defaultextension = '.txt',
            filetypes = [('文本文档', '*.txt'), ('所有类型', '*.*')]
        )

        if not path: return

        tab, text_tab = self.get_tab()

        if text_tab.path:  # When the file has been, enter this fork.
            self.save_file(file_path = path)

            return

        text_tab.path = path
        text_tab.label = Path(path).name

        self.save_file()

        self.tab(tab, text = text_tab.label)
        self._update_info_on_title()


class TextTab(tk.Frame):
    def __init__(self, master) -> None:

        super().__init__(master)

        self.notebook = master

        # Tab config
        self.path = ''
        self.label = ''  # A variable displayed on tab

        self.grid_columnconfigure(1, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        # Wigets
        font_size = self.notebook.main_window.main_menu.font_size.get()

        self.text = tk.Text(
            self,
            wrap = 'none',
            undo = True,
            bd = 0,
            font = ('Consolas', font_size),
            selectbackground = '#d3e9fc',
            selectforeground = 'black'
        )

        self.line_number_bar = LineNumberBar(self)
        self.line_number_bar.grid(row = 0, column = 0, rowspan = 2, sticky = 'ns')

        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.grid(row = 0, column = 2, sticky = 'ns')

        self.x_scrollbar = ttk.Scrollbar(self, orient = 'horizontal', style = 'Custom.Horizontal.TScrollbar')
        self.x_scrollbar.grid(row = 0, column = 1, sticky = 'sew')

        self.text['xscrollcommand'] = self._is_out_of_text
        self.x_scrollbar.config(command = self.text.xview)

        self.text.grid(row = 0, column = 1, sticky = 'nsew')

        self.text['yscrollcommand'] = self.scrollbar.set

        self.scrollbar.config(command = self.line_number_bar.scroll)

        self.right_click_menu()

        self.text.bind('<Control-o>', self._ctrl_o)
        self.text.bind('<Button-3>', self._popup_menu)

        self.text.bind('<<Modified>>', self._text_is_changed)

        # For the line number bar
        self.text.bind('<Any-KeyPress>', self._delay_to_update_line_number)
        self.text.bind('<B2-Motion>', self._selecting_scrolling)

        self.line_number_bar.bind('<Button-1>', self._no_clicking_line_number_bar)
        self.line_number_bar.bind('<B2-Motion>', self._no_clicking_line_number_bar)

        self.text.bind('<MouseWheel>', self.line_number_bar.wheel)
        self.line_number_bar.bind('<MouseWheel>', self.line_number_bar.wheel)

        self.text.bind('<<Selection>>', self._selecting_scrolling)

        # For highlighting the current line
        self.text.bind('<Button-1>', self._delay_to_highlight)

        self.line_number_bar.update_line_number()

    def right_click_menu(self) -> None:

        self.menu = tk.Menu(self, tearoff = False, activeforeground = 'black', activebackground = '#91c9f7')

        self.menu.add_command(label = '复制', accelerator = 'Ctrl+C', command = self.copy)
        self.menu.add_command(label = '剪切', accelerator = 'Ctrl+X', command = self.cut)
        self.menu.add_command(label = '粘贴', accelerator = 'Ctrl+V', command = self.paste)
        self.menu.add_separator()
        self.menu.add_command(label = '复制当前文件路径', command = self.copy_file_path)

    def _popup_menu(self, event: tk.Event) -> None:

        self.text.focus_set()
        self.text.mark_set('insert', f'@{event.x}, {event.y}')

        self._delay_to_highlight()

        self._check_status_of_options()

        self.menu.post(event.x_root, event.y_root)

    def _check_status_of_options(self) -> None:

        if self.path:
            self.menu.entryconfig('复制当前文件路径', state = 'normal')
        else:
            self.menu.entryconfig('复制当前文件路径', state = 'disabled')

        try:
            self.notebook.main_window.clipboard_get()
            self.menu.entryconfig('粘贴', state = 'normal')
        except tk.TclError:
            self.menu.entryconfig('粘贴', state = 'disabled')

    def _delay_to_update_line_number(self, event: Optional[tk.Event] = None) -> None:

        # Wait until entering successfully.
        self.after(1, self.line_number_bar.update_line_number)

    def _delay_to_highlight(self, event: Optional[tk.Event] = None) -> None:

        # Wait until clicking successfully.
        self.after(1, self.line_number_bar.update_highlight_current_line)

    def _ctrl_o(self, event: tk.Event) -> None: return None  # Tkinter has bound ctrl+o inside "Text".

    def _is_out_of_text(self, upper, lower) -> None:

        if self.text.xview() != (0.0, 1.0):
            self.x_scrollbar.lift(self.text)
        else:
            self.x_scrollbar.lower(self.text)

        self.x_scrollbar.set(upper, lower)

    def _text_is_changed(self, event: tk.Event) -> None:

        if self.text.edit_modified():
            self.notebook.tab(self.notebook.get_tab()[0], text = f'*{self.label}')
        else:
            self.notebook.tab(self.notebook.get_tab()[0], text = self.label)

    def _no_clicking_line_number_bar(self, event: tk.Event) -> str: return 'break'

    def _selecting_scrolling(self, event: tk.Event) -> None:

        # Important in B2-Motion for not strange yview.
        self.after(1, self.line_number_bar.scroll_when_selecting)

    def copy(self) -> None:

        self.text.event_generate('<<Copy>>')

        self._update_ui()

    def cut(self) -> None:

        self.text.event_generate('<<Cut>>')

        self._update_ui()

    def paste(self) -> None:

        self.text.event_generate('<<Paste>>')

        self._update_ui()

    def select_all(self) -> None:

        self.text.event_generate('<<SelectAll>>')

        self._update_ui()

    def undo(self) -> None:

        self.text.event_generate('<<Undo>>')

        self._update_ui()

    def redo(self) -> None:

        self.text.event_generate('<<Redo>>')

        self._update_ui()

    def _update_ui(self) -> None:

        self.line_number_bar.update_line_number()

    def copy_file_path(self) -> None:

        self.notebook.main_window.clipboard_clear()
        self.notebook.main_window.clipboard_append(self.path)
