import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME}...")
    print(f"Server accessible at: http://127.0.0.1:8000")
    print(f"API Docs accessible at: http://127.0.0.1:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
