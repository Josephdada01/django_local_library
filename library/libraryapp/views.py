from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
# Create your views here.
from libraryapp.models import Book, Author, BookInstance, Genre, Language


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    #number of books that consist of thinks
    num_of_think = Book.objects.filter(title__contains='Think').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_of_think': num_of_think,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book

    paginate_by = 10


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    """list view for the author"""
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    """detail view for the author"""
    model = Author

class GenreDetailView(generic.DetailView):
    """Generic class-based detail view for a genre."""
    model = Genre

class GenreListView(generic.ListView):
    """Generic class-based list view for a list of genres."""
    model = Genre
    paginate_by = 10

class LanguageDetailView(generic.DetailView):
    """Generic class-based detail view for a genre."""
    model = Language

class LanguageListView(generic.ListView):
    """Generic class-based list view for a list of genres."""
    model = Language
    paginate_by = 10

class BookInstanceListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = BookInstance
    paginate_by = 10

class BookInstanceDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = BookInstance

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'libraryapp/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )
    

class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """List of all books on loan"""
    model = BookInstance
    template_name = 'libraryapp/all_loaned_books.html'
    paginate_by = 10
    permission_required = 'librayapp.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['borrowers'] = {
            book_instance.id: book_instance.borrower.get_full_name() if book_instance.borrower else "N/A"
            for book_instance in context['object_list']
        }
        return context


import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from libraryapp.forms import RenewBookForm

@login_required
@permission_required('libraryapp.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'libraryapp/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'libraryapp.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'libraryapp.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'libraryapp.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']
    permission_required = 'libraryapp.add_book'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']
    permission_required = 'libraryapp.change_book'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'libraryapp.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )

class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.add_genre'


class GenreUpdate(PermissionRequiredMixin, UpdateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.change_genre'


class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('genres')
    permission_required = 'catalog.delete_genre'


class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.add_language'


class LanguageUpdate(PermissionRequiredMixin, UpdateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.change_language'


class LanguageDelete(PermissionRequiredMixin, DeleteView):
    model = Language
    success_url = reverse_lazy('languages')
    permission_required = 'catalog.delete_language'


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = ['book', 'imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.add_bookinstance'


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    # fields = "_all_"
    fields = ['imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.change_bookinstance'


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    success_url = reverse_lazy('bookinstances')
    permission_required = 'catalog.delete_bookinstance'