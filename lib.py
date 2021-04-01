#
#  lib.py
#  Unbound Bible Python Edition
#

import os
import locale

def languageCode() -> str:
    try:
        return locale.getdefaultlocale()[0][0:2]
    except:
        return "en"

