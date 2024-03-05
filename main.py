import uvicorn
from fastapi import FastAPI

from src.routes import routes, auth

app = FastAPI()

app.include_router(routes.router, prefix='/api')
app.include_router(auth.router, prefix='/auth')


@app.get("/")
def read_root():
    return {"message": "GoIT homework #11-13 - REST API via FastAPI"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
