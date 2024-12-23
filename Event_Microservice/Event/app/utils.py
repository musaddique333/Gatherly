import grpc
from app.api import auth_pb2, auth_pb2_grpc
from fastapi import HTTPException
import os


AUTH_SERVICE_HOST: str = os.getenv("AUTH_SERVICE_HOST")
AUTH_SERVICE_PORT: int = os.getenv("AUTH_SERVICE_PORT")

def validate_user(email: str):
    try:
        channel = grpc.insecure_channel(f"{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}")
        stub = auth_pb2_grpc.AuthServiceStub(channel)
        request = auth_pb2.ValidateUserRequest(email=email)
        response = stub.ValidateUser(request)
        if not response.is_valid:
            raise HTTPException(status_code=404, detail="User not found")
    except grpc.RpcError as e:
        raise HTTPException(status_code=503, detail=f"gRPC error: {e.details()}")