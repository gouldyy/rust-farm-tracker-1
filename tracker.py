name: Rust Farming Tracker

on:
  schedule:
    
cron: "/20 * * *"
workflow_dispatch:

permissions:
  contents: write

jobs:
  track:
    runs-on: ubuntu-latest

    steps:
      
name: Checkout
      uses: actions/checkout@v4

      
name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"

      
name: Install dependencies
      run: pip install -r requirements.txt

      
name: Run tracker
      env:
        DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
        SERVER_ID: limitless-us-2x-quad-monthly
        STEAM_IDS: 76561198398162714,76561199151909126,76561199576924698,76561198996827770
        API_URL: https://limitlessrust.com/api/v3/leaderboard
        SEARCH_PARAM: search
        GROUP: gathered
        SORT_BY: gathered_metal.ore
      run: python tracker.py

      
name: Save tracker state
      run: |
        git config user.name "rust-farm-tracker[bot]"
        git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
        git add state.json
        git diff --cached --quiet || git commit -m "Update tracker state"
        git push
