from fastapi import Depends, FastAPI
from app.utils.lifespan import lifespan
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.log_middleware import LoggingMiddleware

from app.modules.telegram.router import router
from app.modules.auth.api.auth_route import router as auth_router
from app.dependencies.current_user import get_current_user


# Application settings
app = FastAPI(
    title="Test API",
    description="This is a test API built with FastAPI.",
    version="1.0.0",
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# routers
app.include_router(
    router=auth_router,
    tags=["auth"]
)

app.include_router(
    router=router,
    tags=["telegram"]
)


# Root endpoint
@app.get("/")
async def root(current_user=Depends(get_current_user)):
    return {
        "message": "Welcome to the Test API!",
        "documentations":{
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            }
        }
