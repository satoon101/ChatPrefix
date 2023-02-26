# ../chat_prefix/chat_prefix.py

"""Add user group prefixes to chat messages."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import json
import warnings

# Source.Python
from colors import *  # pylint: disable=wildcard-import
from listeners.tick import Delay
from messages import SayText2
from messages.hooks import HookUserMessage
from players.entity import Player

# Plugin
from .config import (
    CHAT_HOOK_CONFIG_FILE, fix_escaped_prefix_characters,
    get_user_and_permissions_prefixes,
)
from .strings import CHAT_STRINGS, LOCATION_STRINGS


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
with CHAT_HOOK_CONFIG_FILE.open() as _json:
    CHAT_HOOK_CONFIG = json.load(_json)

USER_PREFIXES, PERMISSION_PREFIXES = get_user_and_permissions_prefixes(
    CHAT_HOOK_CONFIG
)

fix_escaped_prefix_characters(CHAT_HOOK_CONFIG)

for _color, _value in CHAT_HOOK_CONFIG.get('colors', {}).items():
    try:
        # pylint: disable=undefined-variable
        globals()[_color] = Color(*map(int, _value.split(',')))
    except ValueError:
        warnings.warn(f'Invalid Color value "{_value}".')

# pylint: disable=undefined-variable
VALID_COLORS = {k: v for k, v in globals().items() if isinstance(v, Color)}


# =============================================================================
# >> USER MESSAGE HOOKS
# =============================================================================
@HookUserMessage('SayText2')
def _saytext2_hook(recipients, data):
    """Hooks SayText2 for chat messages to send a modified version."""
    key = data.message

    # Is this message from a player sending chat?
    if key not in CHAT_STRINGS.keys():
        return

    # Does the chatting player belong to any group?
    index = data.index
    group = _get_group(index)
    if group is None:
        return

    full_prefix = CHAT_HOOK_CONFIG['groups'][group]['prefix']
    tokens = {
        'data': data,
        'prefix': full_prefix.format(**VALID_COLORS),
    }

    # Add the location information if it is needed
    location = LOCATION_STRINGS.get(data.param3, data.param3)
    if location:
        tokens['location'] = location

    # Use a delay to avoid crashing the server
    Delay(0, _send_new_message, (key, index, list(recipients)), tokens)

    # Remove all recipients for the current message to block it
    recipients.remove_all_players()


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def _get_group(index):
    """Return the group to use for the given player."""
    player = Player(index)
    steamid = player.raw_steamid.to_uint64()

    # Is the player hard-coded into the config?
    if steamid in USER_PREFIXES:
        return USER_PREFIXES[steamid]

    # Does the player carry the permission of any group?
    permissions = player.permissions
    for permission, prefix in PERMISSION_PREFIXES.items():
        if permission in permissions:
            return prefix

    return None


def _send_new_message(key, index, *ply_indexes, **tokens):
    """Send the message to the given players."""
    message = SayText2(
        message=CHAT_STRINGS[key],
        index=index,
    )
    message.send(*ply_indexes, **tokens)
