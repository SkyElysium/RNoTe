import sys
import os
import gettext
import configparser

# Basic Settings
SETTINGS = {
    'win_title': 'RNoTe',
    'win_size' : '800x500',

    'all_lang': [('简体中文', 'zh-CN'), ('English', 'en')]
}

def get_settings(*names):

    if len(names) != 1:
        return [SETTINGS[name] for name in names]
    return SETTINGS[names[0]]

RES_RELATIVE_PATHS = {
    'win_icon': 'data/icon.png',
    'tab_x'   : 'data/close.png',

    'file_history': 'data/config/recent_files.txt',

    'lang'    : 'lang',
    'langconf': 'data/config/config.ini'
}

def get_path(name):

    if hasattr(sys, '_MEIPASS'):
        # On Windows, running from the program icon menu on
        # the task bar will cause wrong paths. (Pyinstaller)
        return os.path.join(sys._MEIPASS, '..', RES_RELATIVE_PATHS[name])
    return RES_RELATIVE_PATHS[name]

# Languages
parser = configparser.ConfigParser()

parser.read(get_path('langconf'))
lang = parser.get('lang', 'lang')

# en: default
if lang == 'en':
    lang = ''

t = gettext.translation(
    'messages',
    get_path('lang'),
    fallback = True,
    languages = [lang]
)
_ = t.gettext

# Styles
CUSTOM_NOTEBOOK_STYLE = [
    (
        'CustomNotebook.tab',
        {
            'sticky': 'nswe',
            'children': [
                (
                    'CustomNotebook.padding',
                    {
                        'side': 'top',
                        'sticky': 'nswe',
                        'children': [
                            (
                                'CustomNotebook.focus',
                                {
                                    'side': 'top',
                                    'sticky': 'nswe',
                                    'children': [
                                        (
                                            'CustomNotebook.label',
                                            {'side': 'left', 'sticky': ''},
                                        ),
                                        (
                                            'CustomNotebook.close',
                                            {'side': 'right', 'sticky': ''},
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
        'Custom.Horizontal.TScrollbar.trough',
        {
            'children': [
                (
                    'Custom.Horizontal.TScrollbar.thumb',
                    {
                        'unit': '1',
                        'children': [
                            ('Custom.Horizontal.TScrollbar.grip', {'sticky': ''})
                        ],
                        'sticky': 'nswe',
                    },
                )
            ],
            'sticky': 'we',
        },
    )
]
