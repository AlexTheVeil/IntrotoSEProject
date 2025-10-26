from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProductForm
from .models import Product
from rapidfuzz import fuzz, process

# Create your views here.
def index(request):
    return render(request, 'core/index.html')

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if request.user.is_authenticated:
                product.user = request.user
            product.save()
            messages.success(request, f"Product '{product.title}' added successfully!")
            return redirect('add_product')
    else:
        form = ProductForm()

    products = Product.objects.all().order_by('-date')  # show newest first
    return render(request, 'core/add_product.html', {'form': form, 'products': products})

def search_view(request):
    query = request.GET.get("q", "")
    products = Product.objects.all()

    if query:
        titles = list(products.values_list("title", flat=True))

        # Find best fuzzy matches (by similarity ratio)
        best_matches = [match[0] for match in process.extract(query, titles, limit=5, scorer=fuzz.token_sort_ratio)]

        products = products.filter(
            models.Q(title__in=best_matches)
            | models.Q(title__icontains=query)
            | models.Q(description__icontains=query)
        ).order_by("-date")

    context = {"products": products, "query": query}
    return render(request, "core/search.html", context)

def home(request):
    query = request.GET.get('q')
    products = Product.objects.all()

    if query:
        products = products.filter(title__icontains=query)

    return render(request, 'core/home.html', {'products': products, 'query': query})