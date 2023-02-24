from fastapi import FastAPI,Response
from fastapi.responses import JSONResponse

from api import jwt,metadata_geos,metadata_nexrad,file_url_generator,nexrad_coords,file_url_generator,file_transfer,file_transfer_nexrad

app = FastAPI()

app.include_router(jwt.router_jwt)
app.include_router(metadata_geos.router_metadata_geos)
app.include_router(metadata_nexrad.router_metadata_nexrad)
app.include_router(file_url_generator.router_file_url_generator)
app.include_router(file_transfer.router_file_transfer)
app.include_router(file_transfer_nexrad.router_file_transfer_nexrad)
app.include_router(nexrad_coords.router_nexrad_coords)

#app.default_response_class = JSONResponse

@app.get("/test")
async def root():
    return {"message": "Hello Bigger Applications!"}
