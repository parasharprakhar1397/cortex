from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.clerk import ClerkVerifier
from auth.middleware import AuthMiddleware
from db.base import init_db
from routers import auth as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


def create_app(verifier: ClerkVerifier | None = None) -> FastAPI:
    """Build the Cortex FastAPI application.

    Args:
        verifier: ClerkVerifier used by the auth middleware. Defaults to one
            built from settings (CLERK_JWKS_URL / CLERK_ISSUER). Tests inject
            a verifier backed by locally generated keys so nothing hits the
            network.
    """
    app = FastAPI(title="Cortex", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Added after CORS so it sits outermost: every /api/v1/* request requires
    # a valid Clerk session token. /health and OpenAPI docs stay public.
    app.add_middleware(AuthMiddleware, verifier=verifier)

    app.include_router(auth_router.router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
