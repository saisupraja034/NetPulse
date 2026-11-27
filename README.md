# NetPulse

NetPulse is a small, single-process FastAPI device-monitoring exercise. It does not ping devices or persist data; devices and alerts are cleared when the server restarts.

## Setup and start

From the project root on Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

On Windows, activate with `.venv\Scripts\activate` instead. Select the `.venv` Python interpreter in VS Code. Open http://127.0.0.1:8000/docs for Swagger UI or http://127.0.0.1:8000/openapi.json for the generated API schema.

## Swagger walkthrough

Start with a freshly restarted server. In `POST /devices`, select **Try it out**, submit the following, and expect HTTP 201:

```json
{
  "device_id": "RTR-101",
  "name": "Branch Router",
  "device_type": "router",
  "ip_address": "192.168.10.1",
  "status": "online"
}
```

In `PATCH /devices/{device_id}/status`, enter `RTR-101` and submit `{"status":"offline"}`. Expect HTTP 200 and an offline device. Run `GET /alerts` to see one alert. Repeat the PATCH and GET: there is still one alert. Registering `RTR-101` again returns HTTP 409. If the ID already exists, restart the server or use `RTR-102`.

## Tests and architecture

Run `python -m pytest -q` from the project root with the environment activated. Each service test creates its own repository.

Routes validate requests, return responses, and translate service errors into HTTP status codes. The service owns registration and transition rules. The repository owns the in-memory devices and alerts, returning copies to callers. The event function creates and saves an offline alert. These layers ship as one deployable application, a modular monolith, not separate services.

A future database repository can implement the same repository methods and be injected into `DeviceService`; its business rules need not change. FastAPI generates `/openapi.json` from route declarations, response codes, and Pydantic models, and Swagger UI uses that schema to display the API.