from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListBookView.as_view(), name='list-book'),
    path('book/<int:pk>/detail/', views.DetailBookView.as_view(), name='detail-book'),
    path('book/create/', views.CreateBookView.as_view(), name='create-book'),
    path('book/<int:pk>/delete/', views.DeleteBookView.as_view(), name='delete-book'),
    path('book/<int:pk>/update/', views.UpdateBookView.as_view(), name='update-book'),
    path('book/<int:book_id>/review/', views.CreateReviewView.as_view(), name='review'),
    path('book/<int:book_id>/favorite/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('favorites/', views.FavoriteListView.as_view(), name='favorite_list'),
]