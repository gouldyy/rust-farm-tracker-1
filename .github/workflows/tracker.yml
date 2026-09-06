import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

SERVER_ID = os.getenv("SERVER_ID", "limitless-us-2x-quad-monthly")
STEAM_IDS = [
    x.strip() for x in os.getenv(
        "STEAM_IDS",
        "76561198398162714,76561199151909126,76561199576924698,76561198996827770",
    ).split(",") if x.strip()
]

# The endpoint is the same /api/v3/leaderboard endpoint your original
# Playwright script captures. The website UI appears to send the player
# search as a query parameter; "search" is the default here.
API_URL = os.getenv("API_URL", "https://limitlessrust.com/api/v3/leaderboard")
SEARCH_PARAM = os.getenv("SEARCH_PARAM", "search")
GROUP = os.getenv("GROUP", "gathered")
SORT_BY = os.getenv("SORT_BY", "gathered_metal.ore")

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
STATE_FILE = Path("state.json")

TIMEOUT = 30


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state):
    STATE_FILE.write_text(
        json.dumps(state, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def extract_entries(payload):
    if isinstance(payload, list):
        return payload, None

    if not isinstance(payload, dict):
        return [], None

    data = payload.get("data")

    if isinstance(data, list):
        return data, None

    if isinstance(data, dict):
        entries = data.get("entries", [])
        return (
            entries if isinstance(entries, list) else [],
            data.get("userEntry"),
        )

    return [], None


def find_entry(payload, steam_id):
    entries, user_entry = extract_entries(payload)

    for entry in entries:
        if isinstance(entry, dict) and str(entry.get("steamId")) == steam_id:
            return entry

    if isinstance(user_entry, dict) and str(user_entry.get("steamId")) == steam_id:
        return user_entry

    if isinstance(payload, dict) and str(payload.get("steamId")) == steam_id:
        return payload

    return None


def get_player(steam_id):
    params = {
        "serverId": SERVER_ID,
        "group": GROUP,
        "sortBy": SORT_BY,
        SEARCH_PARAM: steam_id,
    }

    headers = {
        "User-Agent": "RustFarmTracker/1.0",
        "Accept": "application/json",
        "Referer": "https://limitlessrust.com/leaderboards",
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=headers,
        timeout=TIMEOUT,
    )
    response.raise_for_status()

    payload = response.json()
    entry = find_entry(payload, steam_id)

    if entry is None:
        entries, user_entry = extract_entries(payload)
        raise RuntimeError(
            f"No player {steam_id} in API response "
            f"(entries={len(entries)}, userEntry={bool(user_entry)}). "
            f"Request URL: {response.url}"
        )

    stats = entry.get("stats", {}) or {}

    def number(key):
        try:
            return int(stats.get(key, 0) or 0)
        except (TypeError, ValueError):
            return 0

    return {
        "steam_id": steam_id,
        "name": entry.get("username") or steam_id,
        "stone": number("gathered_stones"),
        "metal": number("gathered_metal.ore"),
        "sulfur": number("gathered_sulfur.ore"),
    }


def delta(current, previous):
    if previous is None:
        return 0
    # A wipe/reset can make the current value smaller. Don't report a
    # giant negative number; treat the new value as the new baseline.
    return max(0, current - previous)


def make_message(players, first_run=False):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "📊 **RUST FARMING UPDATE**",
        f"🕒 {now}",
        "",
    ]

    total = {"stone": 0, "metal": 0, "sulfur": 0}
    total_delta = {"stone": 0, "metal": 0, "sulfur": 0}

    for p in players:
        d = p["delta"]
        total["stone"] += p["stone"]
        total["metal"] += p["metal"]
        total["sulfur"] += p["sulfur"]
        total_delta["stone"] += d["stone"]
        total_delta["metal"] += d["metal"]
        total_delta["sulfur"] += d["sulfur"]

        lines.extend([
            f"**{p['name']}**",
            f"🪨 Stone: `{p['stone']:,}`  **(+{d['stone']:,})**",
            f"⛏️ Metal: `{p['metal']:,}`  **(+{d['metal']:,})**",
            f"💥 Sulfur: `{p['sulfur']:,}`  **(+{d['sulfur']:,})**",
            f"📦 Combined: `{p['stone'] + p['metal'] + p['sulfur']:,}`  "
            f"**(+{d['stone'] + d['metal'] + d['sulfur']:,})**",
            "",
        ])

    combined = sum(total.values())
    combined_delta = sum(total_delta.values())

    lines.extend([
        "━━━━━━━━━━━━━━━━━━",
        "**QUAD TOTAL**",
        f"🪨 Stone: `{total['stone']:,}`  **(+{total_delta['stone']:,})**",
        f"⛏️ Metal: `{total['metal']:,}`  **(+{total_delta['metal']:,})**",
        f"💥 Sulfur: `{total['sulfur']:,}`  **(+{total_delta['sulfur']:,})**",
        f"📦 Combined: `{combined:,}`  **(+{combined_delta:,})**",
    ])

    if first_run:
        lines.extend([
            "",
            "ℹ️ First run: the `+` values are 0 because there is no previous snapshot yet.",
        ])

    return "\n".join(lines)


def send_discord(content):
    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={
            "content": content,
            "allowed_mentions": {"parse": []},
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()


def main():
    state = load_state()
    players = []
    new_state = {}

    for steam_id in STEAM_IDS:
        player = get_player(steam_id)
        old = state.get(steam_id)

        d = {
            "stone": delta(player["stone"], old.get("stone") if old else None),
            "metal": delta(player["metal"], old.get("metal") if old else None),
            "sulfur": delta(player["sulfur"], old.get("sulfur") if old else None),
        }

        player["delta"] = d
        players.append(player)

        new_state[steam_id] = {
            "name": player["name"],
            "stone": player["stone"],
            "metal": player["metal"],
            "sulfur": player["sulfur"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    first_run = not bool(state)
    message = make_message(players, first_run=first_run)
    send_discord(message)
    save_state(new_state)

    print(message)
    print("\nSnapshot saved successfully.")


if __name__ == "__main__":
    main()
