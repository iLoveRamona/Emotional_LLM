from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from starlette.staticfiles import StaticFiles

from src.view.router import router as router_user
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(router_user)