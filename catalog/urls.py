from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),

    # For example, given the path shown below, for a request to /myurl/halibut/ 
    # Django will call views.my_view(request, fish=halibut, my_template_name='some_path').
    # path('myurl/<int:fish>', views.my_view, {'my_template_name': 'some_path'}, name='aurl'),
]

urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
]

urlpatterns += [
    path('books/loaned/', views.AllLoanedBooksByUserListView.as_view(), name='all-borrowed'),
]

urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
]

urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]

urlpatterns += [
    path('books/available/', views.AllAvailableBooksListView.as_view(), name='all-available'),
    path('books/reserved/', views.AllReservedBooksListView.as_view(), name='all-reserved'),
    path('books/maintenance/', views.AllMaintainedBooksListView.as_view(), name='all-maintenance'),
]

urlpatterns += [
    path('books/<uuid:pk>/change-status/', views.status_book_librarian, name='change-status'),
]