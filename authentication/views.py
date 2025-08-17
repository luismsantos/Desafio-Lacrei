from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.contrib.auth.models import User

from .serializers import (
    UsuarioLoginSerializer,
    UsuarioPerfilSerializer,
    UsuarioRegistroSerializer,
)


@swagger_auto_schema(
    method="post",
    request_body=UsuarioRegistroSerializer,
    operation_description="Registra um novo usuário no sistema",
    responses={201: "Usuário criado com sucesso", 400: "Dados inválidos"},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def registrar(request):
    """Registro de novo usuário"""
    serializer = UsuarioRegistroSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "mensagem": "Usuário criado com sucesso!",
                "usuario": {
                    "id": user.id,
                    "nome_usuario": user.username,
                    "email": user.email,
                    "primeiro_nome": user.first_name,
                    "ultimo_nome": user.last_name,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=UsuarioLoginSerializer,
    operation_description="Realiza login e retorna tokens JWT",
    responses={200: "Login realizado com sucesso", 400: "Credenciais inválidas"},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def entrar(request):
    """Login do usuário"""
    serializer = UsuarioLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "mensagem": "Login realizado com sucesso!",
                "usuario": {
                    "id": user.id,
                    "nome_usuario": user.username,
                    "email": user.email,
                    "primeiro_nome": user.first_name,
                    "ultimo_nome": user.last_name,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=["get"],
    operation_description="Obtém informações do perfil do usuário autenticado",
    responses={200: UsuarioPerfilSerializer, 401: "Não autenticado"},
)
@swagger_auto_schema(
    methods=["patch"],
    request_body=UsuarioPerfilSerializer,
    operation_description="Atualiza informações do perfil do usuário autenticado",
    responses={
        200: UsuarioPerfilSerializer,
        400: "Dados inválidos",
        401: "Não autenticado",
    },
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def perfil(request):
    """Perfil do usuário autenticado"""
    user = request.user

    if request.method == "GET":
        serializer = UsuarioPerfilSerializer(user)
        return Response(serializer.data)

    elif request.method == "PATCH":
        serializer = UsuarioPerfilSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "refresh": openapi.Schema(
                type=openapi.TYPE_STRING, description="Refresh token para invalidar"
            )
        },
        required=["refresh"],
    ),
    operation_description="Realiza logout invalidando o refresh token",
    responses={
        200: "Logout realizado com sucesso",
        400: "Token inválido",
        401: "Não autenticado",
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sair(request):
    """Logout do usuário (invalidar refresh token)"""
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response(
            {"mensagem": "Logout realizado com sucesso!"}, status=status.HTTP_200_OK
        )
    except Exception:
        return Response({"erro": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)
