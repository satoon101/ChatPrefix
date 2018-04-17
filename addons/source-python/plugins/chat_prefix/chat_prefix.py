# ../chat_prefix/chat_prefix.py

"""Add user group prefixes to chat messages."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import json
import warnings

# Source.Python
from colors import *
from core import GAME_NAME
from filters.recipients import RecipientFilter
from listeners.tick import Delay
from messages import SayText2
from messages.hooks import HookUserMessage
from paths import PLUGIN_DATA_PATH
from players.entity import Player
from steam import SteamID
from translations.strings import LangStrings

# Plugin
from .info import info


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
CHAT_STRINGS = LangStrings(f'{info.name}/strings')
LOCATION_STRINGS = LangStrings(f'{info.name}/locations')

with (PLUGIN_DATA_PATH / info.name + '.json').open() as _json:
    CHAT_HOOK_CONFIG = json.load(_json)

user_prefixes = {}
permission_prefixes = {}
for prefix, group in CHAT_HOOK_CONFIG['groups'].items():
    for value in group.get('users', []):
        try:
            user_prefixes[SteamID.parse(str(value)).to_uint64()] = prefix
        except ValueError:
            warnings.warn(f'Invalid SteamID value "{value}".')
    permission = group.get('permission')
    if permission:
        permission_prefixes[permission] = prefix

for color, value in CHAT_HOOK_CONFIG.get('colors', {}).items():
    try:
        globals()[color] = Color(*map(int, value.split(',')))
    except ValueError:
        warnings.warn(f'Invalid Color value "{value}".')

valid_colors = {k: v for k, v in globals().items() if isinstance(v, Color)}


# =============================================================================
# >> USER MESSAGE HOOKS
# =============================================================================
@HookUserMessage('SayText' if GAME_NAME == 'dod' else 'SayText2')
def _saytext2_hook(recipients, data):
    key = data.message
    print(data)
    if not key in CHAT_STRINGS.keys():
        return

    index = data.index
    prefix = _get_prefix(index)
    if prefix is None:
        return

    full_prefix = CHAT_HOOK_CONFIG['groups'][prefix]['prefix']
    tokens = {
        'data': data,
        'prefix': full_prefix.format(**valid_colors),
    }
    location = LOCATION_STRINGS.get(data.param3, data.param3)
    if location:
        tokens['location'] = location
    Delay(0, _send_new_message, (key, index, list(recipients)), tokens)
    recipients.remove_all_players()


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def _get_prefix(index):
    player = Player(index)
    steamid = player.raw_steamid.to_uint64()
    if steamid in user_prefixes:
        return user_prefixes[steamid]
    permissions = player.permissions
    permissions.add('chat.moderator')
    for permission, prefix in permission_prefixes.items():
        if permission in permissions:
            return prefix
    return None


def _send_new_message(key, index, *ply_indexes, **tokens):
    message = SayText2(
        message=CHAT_STRINGS[key],
        index=index,
    )
    message.send(*ply_indexes, **tokens)
