import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox

from .config import (
    get_settings,
    get_path,
    _,
    CUSTOM_X_SCROLLBAR_STYLE,
    CUSTOM_NOTEBOOK_STYLE
)
from .line_number_bar import LineNumberBar


class CustomNotebook(ttk.Notebook):
    def __init__(self, master: 'Editor'):

        super().__init__(master)
        self.editor = master

        self.font_size = tk.IntVar(self, 13)
        self.is_tab_on = tk.BooleanVar(self, False)

        # Create the "close" button.
        self.close_image = tk.PhotoImage(file = get_path('tab_x'))

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
        self.bind('<ButtonRelease-1>', self._move_selected_tab)

        self.bind('<<NotebookTabChanged>>', self.update_info_on_title)

    def _on_pressing_close(self, event):

        if self.identify(event.x, event.y) == 'close':
            tab_id = f'@{event.x}, {event.y}'

            self.safely_close_file(tab_id = tab_id)

    def _move_selected_tab(self, event):

        # Use try-except to prevent the cursor from moving on nothing.
        try:
            if self.identify(event.x, event.y) != 'close':
                tab_index = self.index(f'@{event.x}, {event.y}')

                self.insert(tab_index, self.get_tab()[0])
        except tk.TclError:
            pass

    def update_info_on_title(self, event = None):

        if not self.tabs():
            self.editor.title(get_settings('win_title'))

            return

        _, text_tab = self.get_tab()

        if text_tab.path:
            self.editor.title(f'{get_settings("win_title")} - {text_tab.path}')
        else:
            self.editor.title(get_settings('win_title'))

    def safely_close_file(self, event = None, tab_id = None):

        if not self.tabs():
            return

        text_tab = self.get_tab()[1] if not tab_id else self.get_tab(tab_id)

        if text_tab.text_panel.edit_modified():
            reply = messagebox.askyesnocancel(
                title = get_settings('win_title'),
                message = _('Save the file before closing?')
            )
            if reply and self.editor.save_file(file_path = text_tab.path) == 'NotSaved':
                return
            elif reply is None:
                return

        if text_tab.path:
            self.editor.main_menu.record_new_file(text_tab.path)

        self.remove_tab(tab_id = tab_id)

    def add_tab(self, event = None, tab_name = _('Untitled')):

        text_tab = TextTab(self)
        text_tab.label = tab_name

        self.add(text_tab, text = tab_name)

        self.select(text_tab)

        return text_tab

    def remove_tab(self, event = None, tab_id = None):

        text_tab = self.get_tab()[1] if not tab_id else self.get_tab(tab_id)

        self.forget(text_tab)
        text_tab.destroy()

    def get_tab(self, which = None):

        if not which:
            tab = self.select()
            text_tab = self.nametowidget(tab)

            return tab, text_tab
        else:
            # All ids will be transformed to numeric ids because
            # "nametowidget" doesn't accept the format: @x, y.
            id = self.tabs()[self.index(which)]
            text_tab = self.nametowidget(id)

            return text_tab


class TextTab(tk.Frame):
    def __init__(self, master: 'CustomNotebook'):

        super().__init__(master)
        self.editor = master.editor
        self.notebook = master
        self.font_size = master.font_size
        self.is_tab_on = master.is_tab_on

        # Tab Info
        self.path = ''
        self.label = ''

        self.font_trace_id = self.font_size.trace('w', self._change_font_size)

        # Interface
        self.grid_columnconfigure(1, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        self.line_number_bar = LineNumberBar(self)
        self.line_number_bar.grid(row = 0, column = 0, rowspan = 2, sticky = 'ns')

        self.text_panel = TextPanel(self)
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

    def delay_to_update_line_number(self, event):

        # The timer prevents from being called before executing "enter".
        self.after(1, self.line_number_bar.update_line_number)

    def delay_to_highlight(self, event = None):

        # The timer prevents from being called before executing "click".
        self.after(1, self.line_number_bar.update_highlight_current_line)

    def _change_font_size(self, *args):

        self.line_number_bar.config(font = ('Consolas', self.font_size.get()))
        self.text_panel.config(font = ('Consolas', self.font_size.get()))

    def destroy(self):

        self.font_size.trace_vdelete('w', self.font_trace_id)
        super().destroy()


class TextPanel(tk.Text):
    def __init__(self, master: 'TextTab'):

        super().__init__(master)
        self.editor = master.editor
        self.notebook = master.notebook
        self.tab = master
        self.font_size = master.font_size
        self.is_tab_on = master.is_tab_on

        self.config(
            wrap = 'none',
            undo = True,
            bd = 0,
            font = ('Consolas', self.font_size.get()),
            selectbackground = '#d3e9fc',
            selectforeground = 'black'
        )

        self.tag_config('searched', background = '#caebcb')
        self.tag_config('selected', underline = True)

        self.bind('<Button-3>', self._popup_menu)
        self.bind('<Control-o>', self._ctrl_o)
        self.bind('<<Modified>>', self._text_is_changed)
        self.bind('<Tab>', self._indent)

        # For highlighting the current line
        self.bind('<Button-1>', self.tab.delay_to_highlight)

        # For the line number bar
        self.bind('<B2-Motion>', self._b2_motion)
        self.bind('<<Selection>>', self.tab.line_number_bar.scroll_when_selecting)
        self.bind('<Any-KeyPress>', self.tab.delay_to_update_line_number)

        self.bind('<MouseWheel>', self.tab.line_number_bar.wheel)

        self._right_click_menu()

    def _right_click_menu(self):

        self.menu = tk.Menu(self, tearoff = False, activeforeground = 'black', activebackground = '#91c9f7')

        self.menu.add_command(label = _('Copy'), accelerator = 'Ctrl+C', command = self.copy)
        self.menu.add_command(label = _('Cut'), accelerator = 'Ctrl+X', command = self.cut)
        self.menu.add_command(label = _('Paste'), accelerator = 'Ctrl+V', command = self.paste)
        self.menu.add_separator()
        self.menu.add_command(label = _('Copy Present Path'), command = self._copy_file_path)

    def _popup_menu(self, event):

        self.focus_set()
        self.mark_set('insert', f'@{event.x}, {event.y}')

        self.tab.delay_to_highlight()

        self._check_status_of_options()

        self.menu.post(event.x_root, event.y_root)

    def _check_status_of_options(self):

        if self.tab.path:
            self.menu.entryconfig(_('Copy Present Path'), state = 'normal')
        else:
            self.menu.entryconfig(_('Copy Present Path'), state = 'disabled')

        try:
            self.editor.clipboard_get()
            self.menu.entryconfig(_('Paste'), state = 'normal')
        except tk.TclError:
            self.menu.entryconfig(_('Paste'), state = 'disabled')

    def copy(self):

        if not self.notebook.tabs():
            return

        self.event_generate('<<Copy>>')

    def cut(self):

        if not self.notebook.tabs():
            return

        self.event_generate('<<Cut>>')
        self.tab.line_number_bar.update_line_number()

    def paste(self):

        if not self.notebook.tabs():
            return

        self.event_generate('<<Paste>>')
        self.tab.line_number_bar.update_line_number()

    def select_all(self):

        if not self.notebook.tabs():
            return

        self.event_generate('<<SelectAll>>')

    def undo(self):

        if not self.notebook.tabs():
            return

        self.event_generate('<<Undo>>')
        self.tab.line_number_bar.update_line_number()

    def redo(self):

        if not self.notebook.tabs():
            return

        self.event_generate('<<Redo>>')
        self.tab.line_number_bar.update_line_number()

    def _copy_file_path(self):

        self.editor.clipboard_clear()
        self.editor.clipboard_append(self.tab.path)

    def _b2_motion(self, event):

        return 'break'

    def _ctrl_o(self, event):

        # Tkinter has bound ctrl+o inside "Text".
        self.editor.open_file()

        return 'break'

    def _is_out_of_text(self, upper, lower):

        if self.xview() != (0.0, 1.0):
            self.tab.x_scrollbar.lift(self)
        else:
            self.tab.x_scrollbar.lower(self)

        self.tab.x_scrollbar.set(upper, lower)

    def _text_is_changed(self, event):

        if self.edit_modified():
            self.notebook.tab(self.tab, text = f'*{self.tab.label}')
        else:
            self.notebook.tab(self.tab, text = self.tab.label)

    def _indent(self, event):

        if not self.is_tab_on.get():
            self.insert('insert', ' ' * 4)

            return 'break'
