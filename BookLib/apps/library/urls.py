from django.urls import re_path, path
from apps.library import views
from .views import RegisterView, LoginView, UserView, LogoutView, CommentsView, WritersView, CommentsByIDView, PagesView

urlpatterns = [
    re_path(r'^/', views.books_list),
    re_path(r'^api/library/books', views.books_list),
    re_path(r'^api/library/book/(?P<id>[0-9]+)', views.books_by_id),
    re_path(r'^api/library/pages', views.books_by_id),
    re_path(r'^api/library/comments', CommentsView.as_view()),
    re_path(r'^api/library/comments/<int:id>', CommentsByIDView.as_view()),
    path('api/library/comments/book/<int:id>', views.comments_bookId),
    path('api/library/register', RegisterView.as_view()),
    path('api/library/login', LoginView.as_view()),
    path('api/library/user', UserView.as_view()),
    path('api/library/logout', LogoutView.as_view()),
    path('api/library/pages', PagesView.as_view()),
    path('api/library/pages/<int:id>', PagesView.as_view()),
    re_path(r'^api/library/writers', WritersView.as_view())
]
