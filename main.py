from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from api import user_router, health_router
from api.member_routes import router as member_router
from api.member_group_routes import router as member_group_router
from api.loan_routes import router as loan_router
from api.loan_member_routes import router as loan_member_router
from api.loan_member_emi_routes import router as loan_member_emi_router
from api.collection_routes import router as collection_router
from api.billing_routes import router as billing_router
from api.staff_routes import router as staff_router
from api.reports_routes import router as reports_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VGreen Backend API",
    description="Backend API for VGreen application",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(user_router)
app.include_router(member_router)
app.include_router(member_group_router)
app.include_router(loan_router)
app.include_router(loan_member_router)
app.include_router(loan_member_emi_router)
app.include_router(collection_router)
app.include_router(billing_router)
app.include_router(staff_router)
app.include_router(reports_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to VGreen Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
