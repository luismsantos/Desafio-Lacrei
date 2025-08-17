from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True, min_length=8, source='password')
    confirmar_senha = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'senha', 'confirmar_senha')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirmar_senha']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirmar_senha')
        user = User.objects.create_user(**validated_data)
        return user


class UsuarioLoginSerializer(serializers.Serializer):
    nome_usuario = serializers.CharField(source='username')
    senha = serializers.CharField(source='password')

    def validate(self, attrs):
        nome_usuario = attrs.get('username')
        senha = attrs.get('password')

        if nome_usuario and senha:
            user = authenticate(username=nome_usuario, password=senha)
            if not user:
                raise serializers.ValidationError("Credenciais inválidas.")
            if not user.is_active:
                raise serializers.ValidationError("Usuário inativo.")
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Nome de usuário e senha são obrigatórios.")


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'username', 'date_joined')
