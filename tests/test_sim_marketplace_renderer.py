from __future__ import annotations

import pytest


def test_marketplace_renderer_pins_existing_projection_commit() -> None:
    from tools.render_sim_marketplace import render_marketplace

    p = "a" * 40
    payload = render_marketplace(p)
    plugin = payload["plugins"][0]

    assert payload == {
        "name": "sim-certification",
        "interface": {"displayName": "SIM"},
        "plugins": [
            {
                "name": "sim",
                "source": {
                    "source": "git-subdir",
                    "url": "https://github.com/heraklist/Standalone-ChatGPT-Project-for-Software-Inc-modding.git",
                    "path": "./plugins/sim",
                    "sha": p,
                },
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Developer Tools",
            }
        ],
    }
    assert plugin["source"]["sha"] == p


@pytest.mark.parametrize(
    "value",
    (
        "",
        "a" * 39,
        "a" * 41,
        "g" * 40,
        "refs/heads/main",
        "-deadbeef",
    ),
)
def test_marketplace_renderer_rejects_non_commit_sha(value: str) -> None:
    from tools.render_sim_marketplace import render_marketplace

    with pytest.raises(ValueError, match="40-hex"):
        render_marketplace(value)


def test_marketplace_renderer_normalizes_hex_case() -> None:
    from tools.render_sim_marketplace import render_marketplace

    payload = render_marketplace("A" * 40)
    assert payload["plugins"][0]["source"]["sha"] == "a" * 40
