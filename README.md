# Zoom-style video app prototype

This project is a Django + Channels starter for a Zoom-like video conferencing app. It follows the roadmap described in the project brief and implements the foundation for room creation, realtime signaling, and a modern call UI.

## Included

- Django project scaffold
- PostgreSQL-ready settings with SQLite fallback for local development
- Room model for create/join by room code
- REST API for room management
- ASGI + Django Channels websocket signaling layer
- Browser-based WebRTC starter with a dark Zoom-inspired UI
- Lobby screen for mic/camera preview before joining

## Phases represented

- Phase 1: foundation and room setup
- Phase 2: websocket signaling layer
- Phase 3: browser WebRTC flow
- Phase 4: modern UI shell

## Quick start

1. Create a virtual environment:

   python -m venv .venv
   .venv\Scripts\activate

2. Install dependencies:

   pip install -r requirements.txt

3. Apply database migrations:

   python manage.py makemigrations
   python manage.py migrate

4. Run the development server:

   python manage.py runserver

For production, run the ASGI application so WebSocket signaling works:

```bash
daphne -b 0.0.0.0 -p $PORT zoom_app.asgi:application
```

Configure `REDIS_URL` in production so all application instances share the
Channels room groups. For users on restrictive networks, also configure
`TURN_URL`, `TURN_USERNAME`, and `TURN_CREDENTIAL` for a TURN server.

5. Open the app:

   http://localhost:8000/

## Local PostgreSQL configuration

Set these environment variables before running the app if you want to use PostgreSQL instead of the default SQLite database:

```bash
export DB_NAME=zoom_app
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_PORT=5432
```

## Notes

- The project uses Redis for Channels when available. If Redis is not running locally, the app will still start in a development fallback and websocket features will not fully work until Redis is configured.
- This is a production-minded starter rather than a full end-to-end Zoom clone. It is intentionally scoped to the core architectural pieces needed before expanding into TURN, SFU, and group calls.
