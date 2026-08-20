import sys
from pathlib import Path

import tkinter as tk
from tkinter import messagebox, filedialog

from .config import get_settings, get_path, _
from .main_menu import MainMenu
from .custom_notebook import CustomNotebook


class Editor(tk.Tk):
    def __init__(self):

        super().__init__()

        self.title(get_settings('win_title'))
        self.geometry(get_settings('win_size'))

        self.iconphoto(True, tk.PhotoImage(file = get_path('win_icon')))

        self.custom_notebook = CustomNotebook(self)
        self.custom_notebook.pack(fill = 'both', expand = True)

        self.main_menu = MainMenu(self)
        self.config(menu = self.main_menu)

        self.custom_notebook.add_tab()

        bindings = {
            ('<Control-n>', '<Control-N>')        : self.custom_notebook.add_tab,
            ('<Control-o>', '<Control-O>')        : self.open_file,
            ('<Control-s>', '<Control-S>')        : self.save_file,
            ('<Control-Alt-s>', '<Control-Alt-S>'): self.save_file_as,
            ('<Control-F4>',)                     : self.custom_notebook.safely_close_file,
            ('<Control-f>', '<Control-F>')        : self.main_menu.popup_find_dialog,
            ('<Control-plus>',)                   : self.main_menu.zoom_in_font,
            ('<Control-minus>',)                  : self.main_menu.zoom_out_font
        }

        for shortcuts, method in bindings.items():
            for shortcut in shortcuts:
                self.bind(shortcut, method)

        self.protocol('WM_DELETE_WINDOW', self.exiting)

    def open_file(self, event = None, file_path = ''):

        path = filedialog.askopenfilename(
            title = _('Open'),
            filetypes = [(_('Text File'), '*.txt'), (_('All Types'), '*.*')]
        ) if not file_path else file_path

        if not path:
            return

        for tab_id in self.custom_notebook.tabs():
            text_tab = self.custom_notebook.get_tab(tab_id)

            if path == text_tab.path:
                return

        try:
            file = Path(path)

            if not file.exists():
                messagebox.showwarning(
                    title = get_settings('win_title'),
                    message = _('The file path you open is not exist')
                )
                return

            text = file.read_text(encoding = 'utf-8')

            text_tab = self.custom_notebook.add_tab(tab_name = file.name)
            text_tab.text_panel.insert('end', text)
        except UnicodeDecodeError:
            messagebox.showerror(
                title = get_settings('win_title'),
                message = _('Cannot open this file, not UTF-8 format or a program')
            )

            return

        text_tab.path = path

        text_tab.text_panel.edit_modified(False)

        text_tab.text_panel.mark_set('insert', '1.0')
        text_tab.text_panel.focus_set()

        text_tab.line_number_bar.update_line_number()

    def save_file(self, event = None, file_path = '') :

        if not self.custom_notebook.tabs():
            return

        _, text_tab = self.custom_notebook.get_tab()

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

    def save_file_as(self, event = None):

        if not self.custom_notebook.tabs():
            return

        path = filedialog.asksaveasfilename(
            title = _('Save As...'),
            defaultextension = '.txt',
            filetypes = [(_('Text File'), '*.txt'), (_('All Types'), '*.*')]
        )

        if not path:
            return

        tab, text_tab = self.custom_notebook.get_tab()

        if text_tab.path:  # When the file has been, enter.
            self.save_file(file_path = path)

            return

        text_tab.path = path
        text_tab.label = Path(path).name

        self.save_file()

        self.custom_notebook.tab(tab, text = text_tab.label)
        self.custom_notebook.update_info_on_title()

    def exiting(self):

        if_saved = []

        for tab_id in self.custom_notebook.tabs():
            text_tab = self.custom_notebook.get_tab(tab_id)

            if text_tab.path:
                self.main_menu.record_new_file(text_tab.path)
            if_saved.append(text_tab.text_panel.edit_modified())

        if any(if_saved):
            reply = messagebox.askyesnocancel(
                title = get_settings('win_title'),
                message = _('Save all of the unsaved files by hand?')
            )
            if reply or reply is None:
                return

        self._fix_win_clipboard()

        sys.exit()

    def _fix_win_clipboard(self):

        # https://github.com/python/cpython/issues/84632
        if sys.platform == 'win32':
            from ctypes import windll

            user32 = windll.user32

            user32.OpenClipboard(0)
            user32.GetClipboardData(1)
            user32.CloseClipboard()
