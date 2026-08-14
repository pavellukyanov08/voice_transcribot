import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.admin.app:app",
        host="0.0.0.0",
        port=2000,
        reload=True,
    )