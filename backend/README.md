Smart Bonus backend (Flask + SQLAlchemy)

Structure:
- app.py
- config.py
- extensions.py
- models/, routes/, services/, tests/

How to run (dev):
1. Create virtualenv and install requirements:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Set environment variables:
   export DATABASE_URL=postgresql://user:pass@localhost:5432/smart_bonus
   export JWT_SECRET_KEY=your_jwt_secret
   export TELEGRAM_BOT_TOKEN=your_bot_token

3. Initialize DB and run:
   flask db init
   flask db migrate -m "initial"
   flask db upgrade
   flask run

Notes:
- Some SQL functions/triggers referenced in services (calculate_session_results) should be created in DB as in project documentation.
