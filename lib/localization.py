# lib/localization.py

import configparser

_L = None

def set_language(lang_code):
    global _L
    if lang_code == 'ru':
        from lang.ru import L as lang_L, texts as lang_texts
    else:
        from lang.en import L as lang_L, texts as lang_texts

    _L = {**lang_L, **lang_texts}


def get_texts():
    global _L
    if _L is None:
        config = configparser.ConfigParser()
        config.read("settings.ini")
        lang_code = config.get("LANG", "language", fallback="en")
        set_language(lang_code)
    return _L
