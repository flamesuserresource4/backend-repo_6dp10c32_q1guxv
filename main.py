import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import ContactInquiry

app = FastAPI(title="Forevergreen Homes and Gardens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Forevergreen Homes and Gardens Backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Contact inquiry endpoint
@app.post("/api/contact")
async def submit_contact(inquiry: ContactInquiry):
    try:
        inserted_id = create_document("contactinquiry", inquiry)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple services endpoint for the frontend to display
@app.get("/api/services")
async def get_services():
    services = [
        {"title": "Lawn Care", "description": "Mowing, edging, fertilization, and seasonal maintenance.", "icon": "leaf"},
        {"title": "Garden Design", "description": "Custom garden planning, planting, and hardscaping.", "icon": "flower"},
        {"title": "Irrigation", "description": "Smart irrigation systems and water management.", "icon": "sprout"},
        {"title": "Hedge & Tree Care", "description": "Pruning, trimming, and health checks for shrubs and trees.", "icon": "trees"}
    ]
    return {"services": services}

# Testimonials endpoint
@app.get("/api/testimonials")
async def get_testimonials():
    testimonials = [
        {"name": "Ava M.", "quote": "They transformed our yard into a lush oasis.", "rating": 5},
        {"name": "Daniel K.", "quote": "Reliable, professional, and the lawn has never looked better!", "rating": 5},
        {"name": "Priya S.", "quote": "Designs are stunning and maintenance is hassle-free.", "rating": 5}
    ]
    return {"testimonials": testimonials}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
