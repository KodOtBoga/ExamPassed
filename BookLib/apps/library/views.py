
import re
import logging

from django.shortcuts import render, get_object_or_404
from rest_framework import status
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from apps.library.serializers import *
import pickle
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
import jwt, datetime

logger = logging.getLogger('__name__')

@api_view(['GET', 'POST', 'DELETE'])
def books_list(request):
    if request.method == 'GET':
        books = Book.objects.all()
        books.query = pickle.loads(pickle.dumps(books.query))
        title = request.GET.get('title', None)
        if title is not None:
            books = books.filter(movie__icontains=title)
        books_serializer = BookSerializer(books, many=True)
        return JsonResponse(books_serializer.data, safe=False)

    elif request.method == 'POST':
        book_data = JSONParser().parse(request)
        book_serializer = BookSerializer(data=book_data)
        if book_serializer.is_valid():
            book_serializer.save()
            return JsonResponse(book_serializer.data, status=status.HTTP_201_CREATED)
        logger.critical(status)
        return JsonResponse(book_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Book.objects.all().delete()
        return JsonResponse({'message': '{} Книги были удалены!'.format(count[0])},
                            status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST', 'DELETE'])
def books_by_id(request, id):
    try:
        book = Book.objects.get(id=id)
    except Book.DoesNotExist:
        return JsonResponse({'message: Book does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        try:
            book = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return JsonResponse({"message": "Book does not exist"}, status=status.HTTP_404_NOT_FOUND)
        book_serializer = BookSerializer(book)
        return JsonResponse(book_serializer.data)

    elif request.method == "PUT":
        new_data = JSONParser().parse(request)
        book_serializer = BookSerializer(book, data=new_data)
        if book_serializer.is_valid():
            book_serializer.save()
            return JsonResponse(book_serializer.data)
        return JsonResponse(book_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        book.delete()
        return JsonResponse({'message: the book was deleted'}, status=status.HTTP_204_NO_CONTENT)

class RegisterView(APIView):

    def post(self, request):
        email = request.data['email']
        serializer = UserSerializer(data=request.data)
        patternEmail = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
        if re.search(patternEmail, email):
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print("OK")
            return Response(serializer.data)
        else:
            raise AuthenticationFailed("Error email")

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("Пользователь не найден")

        if not user.check_password(password):
            raise AuthenticationFailed("Не правильный пароль")

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        user.last_login = datetime.datetime.utcnow()
        user.is_active = True
        user.save()
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            "jwt": token,
        }
        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Пользователь не авторизован")

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Пользователь не авторизован")

        user = User.objects.filter(id=payload['id']).first()

        serializer = UserSerializer(user)
        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):

        email = request.data['email']
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("Пользователь не найден")

        if user.is_active == True:
            user.is_active = False
            user.save()

        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Успешно вышли из аккаунта'
        }

        return response

class CommentsByIDView(APIView):
    def get(self, request, pk):
        comments = Comments.objects.filter(pk=pk)
        comments.query = pickle.loads(pickle.dumps(comments.query))
        comments_serializer = CommentsSerializer(comments, many=True)
        return JsonResponse(comments_serializer.data, safe=False)

class CommentsView(APIView):
    def get(self, request):
        comments = Comments.objects.all()
        comments.query = pickle.loads(pickle.dumps(comments.query))
        comments_serializer = CommentsSerializer(comments, many=True)
        return JsonResponse(comments_serializer.data, safe=False)

    def post(self, request, *args, **kwargs):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Не авторизованый пользователь")

        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        user = get_object_or_404(User, pk=payload['id'])

        comment_data = JSONParser().parse(request)
        comment_data.update(
            {'userId': user.id}
        )
        comment_serializer = CommentsSerializer(data=comment_data)

        if comment_serializer.is_valid(raise_exception=True):
            comment_serializer.save()
            return JsonResponse(comment_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WritersView(APIView):
    def get(self, request):
        writers = Writers.objects.all()
        writers.query = pickle.loads(pickle.dumps(writers.query))
        writers_serializer = WritersSerializer(writers, many=True)
        return JsonResponse(writers_serializer.data, safe=False)
    def post(self, request):
        writers_data = JSONParser().parse(request)
        writers_serializer = WritersSerializer(data=writers_data)
        if writers_serializer.is_valid():
            writers_serializer.save()
            return JsonResponse(writers_serializer.data, status=status.HTTP_201_CREATED)
        logging.critical(status)
        return JsonResponse(writers_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PagesView(APIView):
    def get(self, request):
        pages = Page.objects.all()
        pages.query = pickle.loads(pickle.dumps(pages.query))
        pages_serializer = PageSerializer(pages, many=True)
        return JsonResponse(pages_serializer.data, safe=False)

    def post(self, request):
        pages_data = JSONParser().parse(request)
        pages_serializer = PageSerializer(data=pages_data)
        if pages_serializer.is_valid():
            pages_serializer.save()
            return JsonResponse(pages_serializer.data, status=status.HTTP_201_CREATED)
        logging.critical(status)
        return JsonResponse(pages_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
def page_by_id(request, id):
    try:
        page = Page.objects.get(bookId=id)
    except Page.DoesNotExist:
        return JsonResponse({'message: Page does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        page_serializer = PageSerializer(page)
        return JsonResponse(page_serializer.data)


@api_view(['GET'])
def comments_bookId(request, bookId):
    comment = Comments.objects.filter(bookId__pk=bookId)
    if request.method == 'GET':
        comment_serializer = CommentsSerializer(comment, many=True)
        return Response(comment_serializer.data, safe=False)