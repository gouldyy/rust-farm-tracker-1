# Rust Farming Discord Tracker

This is a cloud-friendly replacement for the original Chrome/Playwright tracker.

It polls the Limitless Rust leaderboard API, remembers the previous snapshot,
calculates the amount gained since the previous run, and sends the result to
Discord.

## What changed from the original

The original tracker connects to a local Chrome instance on port 9222.
This version does not need Chrome, Playwright, or your PC running.

It calls:

`https://limitlessrust.com/api/v3/leaderboard`

with:

- `serverId=limitless-us-2x-quad-monthly`
- `group=gathered`
- `sortBy=gathered_metal.ore`
- `search=<SteamID64>`

The `search` parameter is the part inferred from the website behaviour used
by the original Playwright script. If Limitless changes its frontend/API,
`SEARCH_PARAM` can be changed without rewriting the tracker.

## Discord setup

1. In Discord, open the channel where you want updates.
2. Edit Channel -> Integrations -> Webhooks.
3. Create a webhook and copy its URL.
4. In GitHub, open your repository:
   Settings -> Secrets and variables -> Actions.
5. Add a repository secret:
   - Name: `DISCORD_WEBHOOK_URL`
   - Value: your Discord webhook URL.

Do not put the webhook URL directly in `tracker.py`.

## Free hosting with GitHub Actions

1. Create a GitHub repository.
2. Upload:
   - `tracker.py`
   - `requirements.txt`
   - `.github/workflows/tracker.yml`
   - `state.json`
3. `state.json` can start as:
   `{}` 
4. Add the `DISCORD_WEBHOOK_URL` repository secret.
5. Make sure Actions have permission to write to the repository:
   Settings -> Actions -> General -> Workflow permissions ->
   "Read and write permissions".
6. Run the workflow manually once with "Run workflow".

After that GitHub will run it every 20 minutes.

## Important

GitHub scheduled workflows are not a guaranteed exact timer. They can start
a little late when GitHub is busy. For a tracker that only needs an update
roughly every 20 minutes, this is normally acceptable.

The first run establishes the baseline, so its `+` values are zero.
Subsequent runs show the amount gained since the previous successful run.

If the server wipes/reset the leaderboard and a player's current value becomes
smaller than the previous value, the tracker treats the current value as the
new baseline instead of reporting a negative gain.
