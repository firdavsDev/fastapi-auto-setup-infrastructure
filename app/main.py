import os

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import engine, get_db
from .models import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pet Project API", version="1.0.0")

# Mount static files for media
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get("/")
async def root():
    return {
        "message": "Pet Project API is running!",
        "server": os.getenv("SERVER_NAME", "unknown"),
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "server": os.getenv("SERVER_NAME", "unknown"),
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Database connection failed: {str(e)}"
        )


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Ensure media directory exists
        os.makedirs("media", exist_ok=True)

        # Save file
        file_path = f"media/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return {"filename": file.filename, "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
