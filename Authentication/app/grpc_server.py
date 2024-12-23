import grpc
from concurrent import futures
from sqlalchemy.orm import Session
import app.api.auth_pb2 as auth_pb2
import app.api.auth_pb2_grpc as auth_pb2_grpc
from app.core.config import settings
from app.crud import get_user_by_email
from app.core.db import SessionLocal

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def ValidateUser(self, request, context):
        email = request.email

        try:
            db: Session = SessionLocal()
            user = get_user_by_email(email, db)
            if not user or not user.is_email_verified:
                return auth_pb2.ValidateUserResponse(is_valid=False)
                        
            return auth_pb2.ValidateUserResponse(is_valid=True)

        except Exception as e:
            # Handle unexpected errors
            context.set_details(f"Internal server error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.ValidateUserResponse(is_valid=False)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port(f"[::]:{settings.GRPC_PORT}")
    server.start()
    server.wait_for_termination()