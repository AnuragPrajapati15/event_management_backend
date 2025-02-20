from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Event
from .serializers import UserRegisterSerializer, UserLoginSerializer, EventSerializer, TicketPurchaseSerializer
from rest_framework.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from event_api.permissions import IsAdminUser, IsRegularUser

class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.

    This view allows users to register by providing their details.
    It handles validation errors, integrity errors (e.g., duplicate usernames),
    and other unexpected exceptions.

    Attributes:
        queryset (QuerySet): A queryset of all User objects.
        serializer_class (Serializer): Serializer used for user registration.
        permission_classes (list): List of permissions required (AllowAny).
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Handles user registration.

        Validates the provided data, saves the user if valid, and returns a success response.
        Catches and handles validation errors, integrity errors, and other exceptions.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A success response if registration is successful,
                      or an error response if an exception occurs.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({"message": "Registered successfully"}, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError:
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Something went wrong", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        

class LoginView(generics.GenericAPIView):
    """
    API view for user login.

    This view handles user authentication and JWT token generation.
    It validates user credentials and returns access and refresh tokens if successful.
    Handles validation errors, user not found errors, and other unexpected exceptions.

    Attributes:
        serializer_class (Serializer): Serializer used for user login.
        permission_classes (list): List of permissions required (AllowAny).
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handles user login.

        Validates the provided credentials, authenticates the user, and generates JWT tokens.
        Catches and handles validation errors, user not found errors, and other exceptions.

        Args:
            request (Request): The HTTP request object containing login credentials.

        Returns:
            Response: A success response with JWT tokens if authentication is successful,
                      or an error response if an exception occurs.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data

            # Generate JWT Token
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": "Something went wrong", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class LogoutView(generics.GenericAPIView):
    """
    API view for user logout.

    This view handles logging out by blacklisting the provided refresh token.
    Only authenticated users can log out.

    Attributes:
        permission_classes (list): List of permissions required (IsAuthenticated).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handles user logout.

        Extracts the refresh token from the request data and blacklists it to invalidate the session.
        Returns a success message if the token is valid, or an error message if invalid.

        Args:
            request (Request): The HTTP request object containing the refresh token.

        Returns:
            Response: A success response if logout is successful,
                      or an error response if the token is invalid.
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)



class EventAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating events.

    This view allows authenticated admin users to create new events and 
    authenticated users to retrieve a list of events.

    Attributes:
        queryset (QuerySet): A queryset containing all Event objects.
        serializer_class (Serializer): Serializer used for event representation.
        permission_classes (list): List of permissions required 
                                   (IsAuthenticated for listing, IsAdminUser for creation).
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  

    def create(self, request, *args, **kwargs):
        """
        Handles event creation.

        Validates the provided event data and saves it to the database.
        Returns a success message upon successful creation.

        Args:
            request (Request): The HTTP request object containing event data.

        Returns:
            Response: A success response if event creation is successful,
                      or an error response if validation fails.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Event created successfully"},
            status=status.HTTP_201_CREATED
        )
    

class TicketPurchaseAPIView(generics.CreateAPIView):
    """
    API view for purchasing tickets to an event.

    This view allows authenticated regular users to purchase tickets for a specific event.
    It ensures concurrency safety and validates event existence before processing the purchase.

    Attributes:
        serializer_class (Serializer): Serializer used for ticket purchase processing.
        permission_classes (list): List of permissions required (IsAuthenticated, IsRegularUser).
    """
    serializer_class = TicketPurchaseSerializer
    permission_classes = [IsAuthenticated, IsRegularUser]

    def create(self, request, *args, **kwargs):
        """
        Handles ticket purchase for a specific event.

        Validates the event ID, ensures the event exists, and processes the ticket purchase
        using the provided data. If successful, returns a success message with ticket details.

        Args:
            request (Request): The HTTP request object containing ticket purchase data.
            kwargs (dict): Additional keyword arguments (event ID).

        Returns:
            Response: A success response with ticket details if purchase is successful,
                      or an error response if the event is not found or validation fails.
        """
        try:
            id=kwargs.get('id')
            event = Event.objects.get(id=id)
        except Event.DoesNotExist:
            return Response({"error": "Event not found."},status=404)

        serializer = self.get_serializer(data=request.data, context={'user': request.user, 'event': event})
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()

        return Response(
            {"message": "Ticket purchased successfully", "ticket": {"quantity": ticket.quantity}},
            status=status.HTTP_201_CREATED
        )