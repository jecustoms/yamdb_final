from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .models import Category
from .models import Genre
from .models import Review
from .models import Title
from .models import User
from .permissions import IsAdminOrDenied
from .permissions import IsAdminOrReadOnly
from .permissions import PutNotAllowed
from .permissions import UserIsOwnerOrModeratorOrReadOnly
from .serializers import AdminSerializer
from .serializers import CategorySerializer
from .serializers import CommentSerializer
from .serializers import EmailConfirmationCodeSerializer
from .serializers import EmailSerializer
from .serializers import GenreSerializer
from .serializers import ReviewSerializer
from .serializers import TitleReadSerializer
from .serializers import TitleWriteSerializer
from .serializers import UserSerializer


class CustomViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleWriteSerializer
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = [IsAdminOrReadOnly, PutNotAllowed]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleWriteSerializer
        return TitleReadSerializer


class CategoryViewSet(CustomViewSet):
    """
    Category view class. Allowed only GET, POST and DELETE methods.
    Search by slug field is possible.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrReadOnly
    ]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class GenreViewSet(CustomViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrReadOnly
    ]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [UserIsOwnerOrModeratorOrReadOnly, PutNotAllowed]
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['title']

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        queryset = Review.objects.filter(title__id=self.kwargs.get('title_id'))
        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [UserIsOwnerOrModeratorOrReadOnly, PutNotAllowed]
    serializer_class = CommentSerializer

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, pk=review_id, title__id=title_id)
        all_comments_of_review = review.comments.all()
        return all_comments_of_review

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, pk=review_id, title__id=title_id)
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrDenied, PutNotAllowed]
    queryset = User.objects.all()
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['username', ]

    def get_serializer_class(self):
        if self.request.user.is_staff or self.request.user.is_admin:
            return AdminSerializer
        return UserSerializer

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=[permissions.IsAuthenticated],
            url_path='me', url_name='users_me')
    def get_update_user(self, request):
        user = get_object_or_404(User, email=request.user.email)
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def generate_code(request):
    serializer = EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username_from_email = email.split('@')[0]
    # We don't set username as required field in User model
    # but Users API use username lookup. Better assign
    # to part of email, later users can change it if necessary
    user = User.objects.get_or_create(email=email)[0]
    if user.username is None:
        user.username = username_from_email
        user.save()
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Confirmation code',
        f'Confirmation code for your account: {confirmation_code}',
        EMAIL_HOST_USER,
        [user.email]
    )
    return Response(status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    serializer = EmailConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    user = User.objects.get(email=email)
    token = RefreshToken.for_user(user).access_token
    return Response({'token': str(token)}, status=HTTP_201_CREATED)
