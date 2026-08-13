import sys
import os

# Basic Settings
SETTINGS = {
    'win_title': 'RNoTe',
    'win_size' : '800x500',

    'file'         : '文件',
    'new'          : '新建',
    'open'         : '打开',
    'save'         : '保存',
    'save_as'      : '另存为...',
    'open_recently': '最近打开',
    'clean_records': '删除记录',
    'tab'          : '标签',
    'close'        : '关闭',
    'exit'         : '退出',
    'edit'         : '编辑',
    'undo'         : '撤销',
    'redo'         : '重做',
    'copy'         : '复制',
    'cut'          : '剪切',
    'paste'        : '粘贴',
    'select_all'   : '全选',
    'find'         : '查找',
    'view'         : '视图',
    'zoom_in'      : '放大',
    'zoom_out'     : '缩小',
    'original_size': '恢复默认大小',
    'about'        : '关于',
    'feedback'     : '反馈',

    'copy_present_path' : '复制当前文件路径'
}

def get_settings(*names):

    if len(names) != 1:
        return [SETTINGS[name] for name in names]
    return SETTINGS[names[0]]

RES_RELATIVE_PATHS = {
    'win_icon': 'data/icon.png',

    'tab_x': 'data/close.png',

    'file_history': 'data/config/recent_files.txt'
}

def get_path(name):

    if hasattr(sys, '_MEIPASS'):
        # On Windows, running from the program icon menu on
        # the task bar will cause wrong paths. (Pyinstaller)
        return os.path.join(sys._MEIPASS, '..', RES_RELATIVE_PATHS[name])
    return RES_RELATIVE_PATHS[name]

# Styles
CUSTOM_NOTEBOOK_STYLE = [
    (
        "CustomNotebook.tab",
        {
            "sticky": "nswe",
            "children": [
                (
                    "CustomNotebook.padding",
                    {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            (
                                "CustomNotebook.focus",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "CustomNotebook.label",
                                            {"side": "left", "sticky": ""},
                                        ),
                                        (
                                            "CustomNotebook.close",
                                            {"side": "right", "sticky": ""},
                                        ),
                                    ],
                                },
                            )
                        ],
                    },
                )
            ],
        },
    )
]

CUSTOM_X_SCROLLBAR_STYLE = [
    (
        "Custom.Horizontal.TScrollbar.trough",
        {
            "children": [
                (
                    "Custom.Horizontal.TScrollbar.thumb",
                    {
                        "unit": "1",
                        "children": [
                            ("Custom.Horizontal.TScrollbar.grip", {"sticky": ""})
                        ],
                        "sticky": "nswe",
                    },
                )
            ],
            "sticky": "we",
        },
    )
]
