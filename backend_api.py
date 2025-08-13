# backend_api.py

#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------
#------------------------------------------NOT BEING USED CURRENTLY-----------------------------------------------
#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------


from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger("fastapi-backend")
app = FastAPI()

# Enable CORS for your frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/token")
# async def create_token(room_name: str, user_identity: str):
#     logger.info(f"Received request to create token for room: {room_name}, user: {user_identity}")
async def create_token(request: Request):
    try:
        # Log when the request arrives
        logger.info("Received request to /api/token")

        # Grab the request body
        body = await request.json()
        room_name = body.get("roomName")
        user_identity = body.get("identity")

        # Log the parameters for you
        logger.info(f"Room Name: {room_name}, User Identity: {user_identity}")

        if not room_name or not user_identity:
            raise HTTPException(status_code=400, detail="Missing roomName or identity")

        # Here’s where you’d generate your token (this is just a placeholder)
        token = "dummy_token"  # Swap this out with your real token logic

        # Log the token that was created
        logger.info(f"Generated token: {token}")

        return {"token": token}
    except Exception as e:
        logger.error(f"Error in /api/token: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



@app.post("/api/end-room")
async def end_room(request: Request):
    data = await request.json()
    room_name = data.get("roomName")
    if not room_name:
        raise HTTPException(status_code=400, detail="roomName is required")
    logger.info(f"Ending room: {room_name}")
    # TODO: call LiveKit Admin API to close the room
    return {"message": f"Room {room_name} is being closed"}

@app.get("/api/health")
async def health():
    return {"status": "ok"}
