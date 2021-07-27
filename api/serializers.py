from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Category, Comment, Genre, Review, Title, User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['id']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ['id']


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.FloatField()

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    text = serializers.CharField()
    author = serializers.ReadOnlyField(source='author.username')

    def validate(self, data):
        request = self.context['request']

        if request.method != 'POST':
            return data

        user = request.user
        title_id = (
            request.parser_context['kwargs']['title_id']
        )
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise serializers.ValidationError(
                'Review must be unique')
        return data

    class Meta:
        fields = [
            'id',
            'text',
            'author',
            'score',
            'pub_date'
        ]
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            'id',
            'text',
            'author',
            'pub_date'
        ]


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role'
        ]


class AdminSerializer(serializers.ModelSerializer):
    """
    Allow admins to set/change roles for users
    """

    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'bio',
            'email',
            'role'
        ]


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class EmailConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirmation_code = serializers.CharField(max_length=50, required=True)

    def validate(self, data):
        email = data['email']
        code = data['confirmation_code']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Unverified email')
        if not default_token_generator.check_token(user, code):
            raise serializers.ValidationError('Invalid confirmation code')
        return data
