from rest_framework import serializers
from django.contrib.auth import authenticate
from event_api.models import *
from django.db import transaction
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password and confirm password do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove before creating user

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['user', 'created_at', 'updated_at']
    

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    This serializer handles user authentication by validating the provided
    username and password. It ensures that both fields are provided,
    verifies credentials, and checks if the user account is active.

    Attributes:
        username (CharField): Field for the user's username.
        password (CharField): Write-only field for the user's password.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validates the provided username and password.

        Ensures that both fields are present, checks authentication,
        and verifies that the user account is active.

        Args:
            data (dict): Dictionary containing 'username' and 'password'.

        Returns:
            User: The authenticated user instance.

        Raises:
            serializers.ValidationError: If authentication fails or 
                                         the user account is disabled.
        """
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required")

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        return user 


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for the Event model.

    This serializer handles serialization and deserialization of Event instances,
    allowing all model fields to be included in API responses.

    Meta:
        model (Event): The Event model being serialized.
        fields (str): Specifies that all fields of the model should be included.
    """
    class Meta:
        model = Event
        fields = '__all__'


class TicketPurchaseSerializer(serializers.Serializer):
    """
    Serializer for ticket purchase.

    This serializer handles ticket purchasing by validating the requested quantity 
    and ensuring availability. It updates the number of sold tickets safely using 
    a database transaction.

    Attributes:
        quantity (IntegerField): The number of tickets the user wants to purchase.
    """

    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        """
        Validates if the requested tickets are available.

        Ensures that the requested quantity does not exceed the available tickets 
        for the event.

        Args:
            data (dict): Dictionary containing 'quantity'.

        Returns:
            dict: Validated data.

        Raises:
            serializers.ValidationError: If the requested quantity exceeds availability.
        """
        event = self.context['event']
        quantity = data['quantity']

        if event.tickets_sold + quantity > event.total_tickets:
            raise serializers.ValidationError(f"Only {event.total_tickets - event.tickets_sold} tickets left.")

        return data

    def create(self, validated_data):
        """
        Creates a ticket purchase entry and updates the event's sold tickets count safely.

        Uses a database transaction to ensure atomic updates and prevent race conditions.

        Args:
            validated_data (dict): Validated purchase data including 'quantity'.

        Returns:
            Ticket: The newly created ticket purchase instance.

        Raises:
            serializers.ValidationError: If the requested quantity exceeds available tickets.
        """
        user = self.context['user']
        event = self.context['event']
        quantity = validated_data['quantity']
        with transaction.atomic(): 
            event = Event.objects.get(id=event.id)
            if event.tickets_sold + quantity > event.total_tickets:
                raise serializers.ValidationError(f"Only {event.total_tickets - event.tickets_sold} tickets left.")

            event.tickets_sold += quantity
            event.tickets_sold += quantity
            event.save(update_fields=['tickets_sold'])

            return Ticket.objects.create(user=user, event=event, quantity=quantity)