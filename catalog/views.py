import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from catalog.models import Book, Author, BookInstance, Genre
# from catalog.forms import RenewBookForm
from catalog.forms import RenewBookModelForm, StatusBookModelForm

def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    # Book instances (title__icontains = 'poder')
    num_books_contains_poder = BookInstance.objects.filter(book__title__icontains='poder').count()
    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_books_contains_poder':num_books_contains_poder,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)
        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.status = form.cleaned_data['status']
            book_instance.borrower = form.cleaned_data['borrower']
            book_instance.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )
    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        # form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
        form = RenewBookModelForm(
            initial={
                'due_back': proposed_renewal_date,
                'status': book_instance.status,
                'borrower':book_instance.borrower})  
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'catalog/book_renew_librarian.html', context)

@login_required
@permission_required('catalog.can_loan_book', raise_exception=True)
def status_book_librarian(request, pk):
    """Change the status (mainly) of a book instance"""
    book_instance = get_object_or_404(BookInstance, pk=pk)
    original_status = book_instance.get_status_display().lower()
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = StatusBookModelForm(request.POST)
        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.status = form.cleaned_data['status']
            book_instance.borrower = form.cleaned_data['borrower']
            book_instance.save()
            if original_status == 'on loan':
            # redirect to a new URL:
                return HttpResponseRedirect(reverse('all-borrowed'))
            return HttpResponseRedirect(reverse(f'all-{original_status}'))

    # If this is a GET (or any other method) create the default form.
    else:
        form = StatusBookModelForm(
            initial={
                'due_back': None,
                'status': 'a',
                'borrower':None}) 
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'catalog/book_change_status.html', context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AllLoanedBooksByUserListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to all users."""
    model = BookInstance
    template_name ='catalog/all_bookinstance_list_borrowed.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

class AllAvailableBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing books available to borrow."""
    model = BookInstance
    template_name ='catalog/all_bookinstance_list_available.html'
    paginate_by = 10
    permission_required = 'catalog.can_loan_book'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='a').order_by('due_back')

class AllReservedBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing reserved books."""
    model = BookInstance
    template_name ='catalog/all_bookinstance_list_reserved.html'
    paginate_by = 10
    permission_required = 'catalog.can_loan_book'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='r').order_by('due_back')

class AllMaintainedBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing reserved books."""
    model = BookInstance
    template_name ='catalog/all_bookinstance_list_mantained.html'
    paginate_by = 10
    permission_required = 'catalog.can_loan_book'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='m').order_by('due_back')

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    permission_required = 'catalog.add_book'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__' 
    permission_required = 'catalog.change_book'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'