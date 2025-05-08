# ../chat_prefix/config.py

"""Configuration functionality."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
import json
import warnings

# Source.Python
from core import GAME_NAME
from paths import CFG_PATH
from steam import SteamID
from translations.strings import LangStrings

# Plugin
from .info import info

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
CHAT_HOOK_CONFIG_FILE = CFG_PATH / info.name + ".json"


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def get_user_and_permissions_prefixes(config):
    """Return the user/permission prefix dictionaries."""
    user_prefixes = {}
    permission_prefixes = {}
    for prefix, group in config["groups"].items():
        for value in group.get("users", []):
            try:
                user_prefixes[SteamID.parse(str(value)).to_uint64()] = prefix
            except ValueError:
                warnings.warn(
                    f'Invalid SteamID value "{value}".',
                    stacklevel=2,
                )
        permission = group.get("permission")
        if permission:
            permission_prefixes[permission] = prefix
    return user_prefixes, permission_prefixes


def fix_escaped_prefix_characters(config):
    """Update all prefixes to fix any escaped characters."""
    for group in config["groups"].values():
        # ruff: noqa: SLF001
        group["prefix"] = LangStrings._replace_escaped_sequences(
            group["prefix"],
        )


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def _create_config_file():
    """Create the config file if it does not already exist."""
    if CHAT_HOOK_CONFIG_FILE.is_file():
        return

    if GAME_NAME == "csgo":
        default = {
            "groups": {
                "ADMIN": {
                    "prefix": "\\x09[\\x06Admin\\x09]",
                    "permission": "chat.admin",
                },
                "CLAN": {
                    "prefix": "\\x09[\\x06G.O.D.S.\\x09]",
                    "users": [
                        123456789101112,
                        "[U:1:2345678]",
                    ],
                },
                "MOD": {
                    "prefix": "\\x09[\\x06Moderator\\x09]",
                    "permission": "chat.moderator",
                },
                "DONOR": {
                    "prefix": "\\x09[\\x06Donor\\x09]",
                    "users": [
                        "STEAM_0:0:1234567",
                        "12345678910111213",
                    ],
                },
            },
        }
    else:
        default = {
            "groups": {
                "ADMIN": {
                    "prefix": "{WHITE}[{GOLD}Admin{WHITE}]",
                    "permission": "chat.admin",
                },
                "CLAN": {
                    "prefix": "{WHITE}[{MAROON}G.O.D.S.{WHITE}]",
                    "users": [
                        123456789101112,
                        "[U:1:2345678]",
                    ],
                },
                "MOD": {
                    "prefix": "{WHITE}[{FUCHSIA}Moderator{WHITE}]",
                    "permission": "chat.moderator",
                },
                "DONOR": {
                    "prefix": "{WHITE}[{PURPLE}Donor{WHITE}]",
                    "users": [
                        "STEAM_0:0:1234567",
                        "12345678910111213",
                    ],
                },
            },
            "colors": {
                "GOLD": "175,175,95",
                "MAROON": "128,0,64",
                "FUCHSIA": "253,63,146",
                "PURPLE": "160,32,240",
            },
        }

    with CHAT_HOOK_CONFIG_FILE.open("w") as open_file:
        json.dump(default, open_file, indent=4)


_create_config_file()
