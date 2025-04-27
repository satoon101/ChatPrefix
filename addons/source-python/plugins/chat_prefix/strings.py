# ../chat_prefix/strings.py

"""Contains all translation variables for the base plugin."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from core import GAME_NAME
from paths import TRANSLATION_PATH
from translations.strings import LangStrings

# Plugin
from .info import info


# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = (
    'CHAT_STRINGS',
    'LOCATION_STRINGS',
)


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
if (TRANSLATION_PATH / info.name / GAME_NAME + '_strings.ini').is_file():
    CHAT_STRINGS = LangStrings(f'{info.name}/{GAME_NAME}_strings')
else:
    CHAT_STRINGS = LangStrings(f'{info.name}/strings')
LOCATION_STRINGS = LangStrings(f'{info.name}/locations')
