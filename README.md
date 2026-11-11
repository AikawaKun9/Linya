# Linya

Linya is a queue system for the campus registrar. Students get a queue number for requests like the Transcript of Records (TOR), see how many people are ahead of them, and know when and where to go, so they can sit down instead of standing in line. Registrar staff use a dashboard to call the next student to a window and mark tickets served or no-show.

## Run it

    copy .env.example .env          # then put your own password in .env
    docker compose up -d            # starts PostgreSQL 17
    python -m venv .venv
    .venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
    pip install -r requirements.txt
    flask --app app db upgrade      # creates the tables
    flask --app app seed            # adds the services and windows
    flask --app app run --debug

  Then open http://127.0.0.1:5000.

  Requirements: [docs/requirements.md](docs/requirements.md)

## Screens

| URL | Screen |
| --- | --- |
| `/` | Home |
| `/join` | Join the queue |
| `/queue/<number>` | My place (ticket number, status, people ahead) |
| `/staff` | Staff dashboard |

Note: the staff dashboard has no login yet. Staff login is planned for a later week. Tickets are now stored into PostgreSQL.