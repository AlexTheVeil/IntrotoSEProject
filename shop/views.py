from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F, DecimalField, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import Product, OrderItem, Payout
from .forms import PayoutRequestForm
def is_seller(user):
    return user.is_authenticated and user.groups.filter(name="Sellers").exists()

def seller_dashboard(request):
    user = request.user
    now = timezone.now()
    start_30 = now - timedelta(days=30)

    qs = OrderItem.objects.filter(
        order__paid=True,
        order__created_at__gte=start_30,
        product__owner=user
    ).annotate(
        line_total=F("unit_price") * F("quantity")
    )

    last_30_total = qs.aggregate(total=Sum("line_total", output_field=DecimalField()))["total"] or Decimal("0.00")

    # Daily series for chart
    daily = (qs
        .annotate(day=TruncDate("order__created_at"))
        .values("day")
        .annotate(amount=Sum("line_total", output_field=DecimalField()))
        .order_by("day"))

    # Top products (last 30 days)
    top = (qs.values("product__name")
             .annotate(amount=Sum("line_total", output_field=DecimalField()))
             .order_by("-amount")[:5])

    # Lifetime total (optional)
    lifetime = (OrderItem.objects
                .filter(order__paid=True, product__owner=user)
                .annotate(line_total=F("unit_price") * F("quantity"))
                .aggregate(total=Sum("line_total", output_field=DecimalField()))["total"] or Decimal("0.00"))

    context = {
        "last_30_total": last_30_total,
        "lifetime_total": lifetime,
        "daily": list(daily),           # [{day: date, amount: Decimal}, ...]
        "top": list(top),               # [{product__name: str, amount: Decimal}, ...]
    }
    return render(request, "shop/seller_dashboard.html", context)



def payout_list(request):
    payouts = Payout.objects.filter(seller=request.user).order_by("-created_at")
    return render(request, "shop/payout_list.html", {"payouts": payouts})



def payout_request(request):
    if request.method == "POST":
        form = PayoutRequestForm(request.POST)
        if form.is_valid():
            s = form.cleaned_data["period_start"]
            e = form.cleaned_data["period_end"]

            # Calculate unpaid revenue in that window
            items = (OrderItem.objects
                .filter(order__paid=True,
                        order__created_at__date__gte=s,
                        order__created_at__date__lte=e,
                        product__owner=request.user)
                .annotate(line_total=F("unit_price") * F("quantity")))

            amount = items.aggregate(total=Sum("line_total", output_field=DecimalField()))["total"] or Decimal("0.00")

            
            overlap = Payout.objects.filter(
                seller=request.user,
                period_start__lte=e,
                period_end__gte=s,
                status__in=["pending","paid"],
            ).exists()
            if overlap:
                form.add_error(None, "There is already a payout covering this period.")
            else:
                Payout.objects.create(
                    seller=request.user,
                    period_start=s,
                    period_end=e,
                    amount=amount,
                    status="pending",
                )
                return redirect("shop:payout_list")
    else:
        form = PayoutRequestForm()

    return render(request, "shop/payout_request.html", {"form": form})

def product_list(request):
    products = Product.objects.all()
    return render(request, "shop/product_list.html", {"products": products})  

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "shop/product_detail.html", {"product": product})
    
