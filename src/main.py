from fastapi import FastAPI, Request, responses
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

from .routes import api


response_index_html = responses.FileResponse(
    'src/templates/index.html',
    status_code=200
)
response_404_html = responses.FileResponse(
    path='src/templates/404.html',
    status_code=404
)


app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def custom_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return response_404_html
    else:
        return await http_exception_handler(request, exc)


app.mount("/api", api.app, name="api")


@app.get("/", tags=["root"])
async def root():
    return response_index_html
