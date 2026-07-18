# Used at editor.py for window config.
MAIN_WINDOW_TITLE = 'RNoTe'
MAIN_WINDOW_SIZE = '800x500'

# Used to display the menu info.
FILE          = '文件'
NEW           = '新建'
OPEN          = '打开'
SAVE          = '保存'
SAVE_AS       = '另存为...'
OPEN_RECENTLY = '最近打开'
TAB           = '标签'
CLOSE         = '关闭'
EXIT          = '退出'
EDIT          = '编辑'
UNDO          = '撤销'
REDO          = '重做'
COPY          = '复制'
CUT           = '剪切'
PASTE         = '粘贴'
SELECT_ALL    = '全选'
FIND          = '查找'
VIEW          = '视图'
ZOOM_IN       = '放大'
ZOOM_OUT      = '缩小'
ORIGINAL_SIZE = '恢复默认大小'
ABOUT         = '关于'
REPORT        = '报告问题'

COPY_PRESENT_PATH = '复制当前文件路径'

# Used at main_menu.pu for the "find" dialog.
TITLE_FIND = '查找'

# Used at main_menu.py for the "about" dialog.
TITLE_ABOUT = '关于 RNoTe'

FIRST_INFO = '项目开源在：https://github.com/SkyElysium/RNoTe'
SECOND_INFO = '''\n
Licensed Under the MIT License.
Copyright (c) 2025 SkyElysium.
'''

ISSUE_URL = 'https://github.com/SkyElysium/RNoTe/issues/new'

# Used at custom_notebook.py for the "layout" function.
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
