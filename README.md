# Engineering Society Bot

A modular Telegram bot for managing the Manufacturing Engineering Society at Mohaghegh Ardabili University.

## Project Structure

```
engineering-society-bot/
├── database/          # Database models and manager
│   ├── models.py     # Database schema definitions
│   ├── manager.py    # Database operations
├── main/             # Main bot implementation
│   ├── handlers/     # Command and message handlers
│   ├── utils/        # Utility functions
│   ├── middleware/   # Middleware for channel verification
├── admin/            # Admin bot implementation
│   ├── handlers/     # Admin-specific handlers
├── config.py         # Configuration settings
├── .env              # Environment variables
├── requirements.txt  # Python dependencies
├── run_main.sh       # Script to run main bot
├── run_admin.sh      # Script to run admin bot
├── run_both.sh       # Script to run both bots
└── stop_both.sh      # Script to stop both bots
```

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env` (use `.env.example` as template)

3. Run the bots:
   - Main bot: `./run_main.sh`
   - Admin bot: `./run_admin.sh`
   - Both bots: `./run_both.sh`

4. Stop bots: `./stop_both.sh`

## Features

- Channel membership verification
- Event and workshop registration
- Admin message management system
- Modular handler structure
- Database management with SQLAlchemy
- Proxy support
- Comprehensive logging

## Development

To add new features:
1. Add handlers in `main/handlers/` or `admin/handlers/`
2. Add utilities in `main/utils/`
3. Update database models in `database/models.py`
4. Add middleware in `main/middleware/`
