import grpc
from concurrent import futures
from sqlalchemy.orm import Session
import logging

from app.services import auth_pb2, auth_pb2_grpc
from app.core.config import settings
from app.crud import get_user_by_email
from app.core.db import SessionLocal

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    """
    gRPC service implementation for user authentication.

    Provides methods to validate a user's email and check whether it is verified.
    """

    def ValidateUser(self, request, context):
        """
        Validate a user by email.

        Args:
            request: gRPC request containing the email to validate.
            context: gRPC context to set error details and status code.

        Returns:
            A ValidateUserResponse indicating whether the email is valid and verified.
        """
        email = request.email

        try:
            # Using context manager for database session to ensure it's properly closed
            with SessionLocal() as db:
                user = get_user_by_email(email, db)

                # Check if the user exists and has a verified email
                if not user or not user.is_email_verified:
                    logger.warning(f"User {email} not found or not verified.")
                    return auth_pb2.ValidateUserResponse(is_valid=False)

                return auth_pb2.ValidateUserResponse(is_valid=True)

        except Exception as e:
            # Log the error and set the context details and status code
            logger.error(f"Error occurred during ValidateUser: {str(e)}")
            context.set_details(f"Internal server error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return auth_pb2.ValidateUserResponse(is_valid=False)

def serve():
    """
    Start the gRPC server to handle incoming authentication requests.

    The server will listen on the specified port and handle requests using the AuthService.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    try:
        auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
        server.add_insecure_port(f"[::]:{settings.GRPC_PORT}")
        logger.info(f"gRPC server started on port {settings.GRPC_PORT}.")
        server.start()
        server.wait_for_termination()

    except Exception as e:
        # Log and handle server startup errors
        logger.error(f"Error starting the gRPC server: {str(e)}")
        raise RuntimeError("Failed to start gRPC server.") from e
