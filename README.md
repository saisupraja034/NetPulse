# NetPulse

A small modular FastAPI network-device monitoring API. Device and alert state is
stored in MySQL and persists across application restarts. The API does not
contact or probe real devices.

## Run

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Configure `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` in the
ignored `.env` file. `DATABASE_URL` can optionally provide the complete
`mysql+pymysql` connection URL. Create or select the target database, then apply
the schema with `alembic upgrade head` before starting the API.

Open `http://127.0.0.1:8000/docs` for the six endpoints. FastAPI builds
`/openapi.json` from the route declarations, request/response models, examples,
and documented error responses.

The API provides `POST /devices` (201), `GET /devices`,
`GET /devices/{device_id}`, `PATCH /devices/{device_id}/status`, `GET /alerts`,
and `GET /health` (`{"status":"ok"}`). Duplicate IDs return 409 and unknown
device IDs return 404.

## Swagger Walkthrough

In `POST /devices`, register this device and expect HTTP 201:

```json
{
	"device_id": "RTR-101",
	"name": "Branch Router",
	"device_type": "router",
	"ip_address": "192.168.10.1",
	"status": "online"
}
```

In `PATCH /devices/{device_id}/status`, set `device_id` to `RTR-101` and send
`{"status":"offline"}`. Expect HTTP 200 and an offline response. Run
`GET /alerts`: it should contain one alert for `RTR-101`. Repeat the PATCH and
GET; the alert count remains one. Re-registering `RTR-101` returns HTTP 409.
Restart the server for a clean run because in-memory data resets on restart.

## Architecture

- Routes validate HTTP requests and translate service exceptions into HTTP errors.
- The service owns registration, lookup, and online-to-offline transition rules.
- The repository owns in-memory dictionaries/lists and returns copies of stored data.
- The event function creates and stores an alert through the repository interface.

The repository is passed into `DeviceService`, so the MySQL-backed repository
can replace the in-memory implementation without moving business rules into the
storage layer. NetPulse remains one deployable modular monolith: all layers run
in one application process and are packaged as one service.

## Tests

```bash
python -m pytest -q
```