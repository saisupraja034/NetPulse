from importlib.metadata import distribution

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.routes.devices import router


app = FastAPI(title="NetPulse", version="1.0.0", docs_url=None)
app.mount(
	"/swagger-assets",
	StaticFiles(directory=distribution("swagger-ui-py").locate_file("swagger_ui/static")),
	name="swagger-assets",
)
app.include_router(router)


@app.get("/docs", include_in_schema=False)
def swagger_docs():
	return get_swagger_ui_html(
		openapi_url=app.openapi_url,
		title=f"{app.title} - Swagger UI",
		swagger_js_url="/swagger-assets/swagger-ui-bundle.js",
		swagger_css_url="/swagger-assets/swagger-ui.css",
		swagger_favicon_url="/swagger-assets/favicon-32x32.png",
	)