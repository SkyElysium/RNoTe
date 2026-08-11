import tkinter as tk


class LineNumberBar(tk.Text):
    def __init__(self, master: 'TextTab', font_size: tk.IntVar) -> None:

        super().__init__(master)

        self.max_width = 5

        self.config(
            width = self.max_width,
            bg = '#e8e8e8',
            fg = '#8f8f8f',
            state = 'disabled',
            cursor = 'arrow',
            bd = 0,
            font = ('Consolas', font_size.get())
        )

        self.tag_config('center', justify = 'center')
        self.tag_config('current_line', foreground = '#3e3e3e')

        self.bind('<Button-1>', self._not_respond_to_cursor)
        self.bind('<B2-Motion>', self._not_respond_to_cursor)

        self.bind('<MouseWheel>', self.wheel)

    def _not_respond_to_cursor(self, event: tk.Event) -> str:

        return 'break'

    def scroll(self, *xy: tuple) -> None:

        self.master.text_panel.yview(*xy)
        self.yview(*xy)

    def scroll_when_selecting(self, event: tk.Event) -> None:

        self.yview_moveto(self.master.text_panel.yview()[0])

        self.update_highlight_current_line()

    def scroll_when_searching(self) -> None:

        self.yview_moveto(self.master.text_panel.yview()[0])

    def wheel(self, event: tk.Event) -> None:

        speed = int(-1 * (event.delta / 60))

        self.yview_scroll(speed, 'units')
        self.master.text_panel.yview_scroll(speed, 'units')

        return 'break'

    def update_line_number(self) -> None:

        line_num = self.master.text_panel.index('end').split('.')[0]

        line_num_text = '\n'.join([str(num) for num in range(1, int(line_num))])

        # Can't get out of the line number bar
        if len(line_num) > self.max_width:
            self.config(width = len(line_num))
        else:
            self.config(width = self.max_width)

        self.config(state = 'normal')

        self.replace('1.0', 'end', line_num_text)

        self.config(state = 'disabled')

        self.yview_moveto(self.master.text_panel.yview()[0])

        self.tag_add('center', '1.0', 'end')

        self.update_highlight_current_line()

    def update_highlight_current_line(self, event: tk.Event = None) -> None:

        self.tag_remove('current_line', '1.0', 'end')

        current_line = self.master.text_panel.index('insert').split('.')[0]

        start = f'{current_line}.0'
        end = f'{current_line}.end'

        self.tag_add('current_line', start, end)
