# Telegram Hisaab Bot

A Telegram polling bot for tracking USDT deposits, INR withdrawals, exchange rates, and balances.

## Render deployment

This repository includes `render.yaml` for a background worker. Create a Render Blueprint from this repository and set the `TELEGRAM_BOT_TOKEN` secret when prompted.

Manual settings: build command `pip install -e .`; start command `python main.py`.

## Bot commands

- `+50` or `+50U` adds a USDT deposit.
- `-1000`, `-1000 INR`, or `-₹1000` records an INR withdrawal.
- `rate 140` changes the exchange rate.
- `total`, `hisaab`, or `hisab` shows the current summary.
- `reset` or `clear` clears the in-memory history.
