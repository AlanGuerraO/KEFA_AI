from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)
        extra_kwargs = {
            "email": {"required": True, "allow_blank": False},
        }

    def validate(self, attrs):
        user = User(
            username=attrs["username"],
            email=attrs["email"],
        )
        try:
            validate_password(attrs["password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {"password": list(exc.messages)}
            ) from exc
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)



class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=False, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[User.USERNAME_FIELD].required = False

    def validate(self, attrs):
        email = attrs.pop("email", None)

        if email:
            user = User.objects.filter(email__iexact=email.strip()).first()

            # Si el correo no existe, se deja un usuario imposible
            # para que SimpleJWT rechace las credenciales con HTTP 401.
            attrs[User.USERNAME_FIELD] = (
                user.get_username() if user else ""
            )

        if not attrs.get(User.USERNAME_FIELD):
            from rest_framework_simplejwt.exceptions import AuthenticationFailed

            raise AuthenticationFailed(
                "Correo electrónico o contraseña incorrectos."
            )
        return super().validate(attrs)
