from fastapi import FastAPI

from app.routes.devices import router


app = FastAPI(title="NetPulse - Network Monitoring API")
app.include_router(router)