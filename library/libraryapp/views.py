from django.shortcuts import render
from django.views import generic

# Create your views here.
from libraryapp.models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_of_think = Book.objects.filter(title__contains='Think').count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_of_think': num_of_think,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book

    paginate_by = 4


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    """list view for the author"""
    model = Author

class AuthorDetailView(generic.DetailView):
    """detail view for the author"""
    model = Author
