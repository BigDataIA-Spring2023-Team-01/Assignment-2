from fastapi import FastAPI,Response
from fastapi.responses import JSONResponse
import jwt, metadata_geos,metadata_nexrad

app = FastAPI()

app.include_router(jwt.router1)
app.include_router(metadata_geos.router2)
app.include_router(metadata_nexrad.router3)

#app.default_response_class = JSONResponse

@app.get("/test")
async def root():
    return {"message": "Hello Bigger Applications!"}
