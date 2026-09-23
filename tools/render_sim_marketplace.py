from __future__ import annotations

import re

COMMIT_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def render_marketplace(projection_commit: str) -> dict:
    if (
        not isinstance(projection_commit, str)
        or COMMIT_RE.fullmatch(projection_commit) is None
    ):
        raise ValueError("projection commit must be exactly 40-hex characters")

    commit = projection_commit.lower()
    return {
        "name": "sim-certification",
        "interface": {
            "displayName": "SIM",
        },
        "plugins": [
            {
                "name": "sim",
                "source": {
                    "source": "git-subdir",
                    "url": "https://github.com/heraklist/Standalone-ChatGPT-Project-for-Software-Inc-modding.git",
                    "path": "./plugins/sim",
                    "sha": commit,
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Developer Tools",
            }
        ],
    }
