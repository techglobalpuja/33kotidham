from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from app.database import engine
from app.models import Base
from app.config import settings
from app.routers import auth, users, pujas, plans, chadawas, bookings, payments, admin, uploads, blogs
from app.routers import temples, products, promo_orders, order_payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    pass


app = FastAPI(
    title="33 Koti Dham API",
    description="Online platform for booking Puja with prasad and chadawa",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (only if directory exists)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(pujas.router, prefix="/api/v1")
app.include_router(plans.router, prefix="/api/v1")
app.include_router(chadawas.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
app.include_router(blogs.router, prefix="/api/v1")
app.include_router(temples.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(promo_orders.router, prefix="/api/v1")
app.include_router(order_payments.router, prefix="/api/v1")


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to 33 Koti Dham API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Error handlers
from fastapi.responses import JSONResponse

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
