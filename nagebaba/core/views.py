from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
import json, datetime
from .models import Customer, Item, Order, OrderItem, Payment, Expense

PREDEFINED_ITEMS = [
    {"name": "Saree", "price": 80},
    {"name": "Shirt", "price": 40},
    {"name": "Pant", "price": 40},
    {"name": "Saree Blouse", "price": 30},
    {"name": "Top", "price": 35},
    {"name": "Ghagra", "price": 60},
    {"name": "Coat/Blazer", "price": 100},
    {"name": "Blanket", "price": 120},
    {"name": "Mandap", "price": 500},
    {"name": "Cushion", "price": 50},
    {"name": "Shoes", "price": 80},
    {"name": "Jacket", "price": 90},
]

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    today = timezone.localdate()
    today_orders = Order.objects.filter(order_date__date=today)
    today_revenue = Payment.objects.filter(date__date=today).aggregate(t=Sum('amount'))['t'] or 0
    today_expenses = Expense.objects.filter(date=today).aggregate(t=Sum('amount'))['t'] or 0
    net_profit = today_revenue - today_expenses
    open_orders = Order.objects.filter(status__in=['pending', 'in_process', 'ready']).select_related('customer').prefetch_related('payments')
    pending = Order.objects.filter(status__in=['pending', 'in_process']).count()
    ready_count = Order.objects.filter(status='ready').count()
    total_customers = Customer.objects.count()
    recent_orders = Order.objects.select_related('customer').order_by('-order_date')[:10]
    ready_orders = Order.objects.filter(status='ready').select_related('customer')[:10]
    due_today = Order.objects.filter(delivery_date=today, status__in=['pending', 'in_process', 'ready']).count()
    outstanding_amount = sum(order.balance() for order in open_orders)
    delivered_today = Order.objects.filter(status='delivered', order_date__date=today).count()
    completion_rate = round((delivered_today / today_orders.count()) * 100) if today_orders.exists() else 0

    return render(request, 'dashboard.html', {
        'today_orders': today_orders.count(),
        'today_revenue': today_revenue,
        'today_expenses': today_expenses,
        'net_profit': net_profit,
        'pending': pending,
        'ready_count': ready_count,
        'total_customers': total_customers,
        'due_today': due_today,
        'outstanding_amount': outstanding_amount,
        'completion_rate': completion_rate,
        'recent_orders': recent_orders,
        'ready_orders': ready_orders,
    })

@login_required
def orders_list(request):
    qs = Order.objects.select_related('customer').order_by('-order_date')
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')
    date_filter = request.GET.get('date', '')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if search:
        qs = qs.filter(Q(customer__name__icontains=search) | Q(customer__phone__icontains=search) | Q(order_number__icontains=search))
    if date_filter == 'today':
        qs = qs.filter(order_date__date=timezone.localdate())

    stats_source = qs
    orders = list(qs)
    total_value = sum(order.total_amount for order in orders)
    paid_count = sum(1 for order in orders if order.payment_status() == 'paid')

    return render(request, 'orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'search': search,
        'date_filter': date_filter,
        'predefined_items': PREDEFINED_ITEMS,
        'order_count': len(orders),
        'pending_count': stats_source.filter(status='pending').count(),
        'ready_count': stats_source.filter(status='ready').count(),
        'paid_count': paid_count,
        'total_value': total_value,
    })

@login_required
def create_order(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        address = request.POST.get('address', '')
        delivery_date = request.POST.get('delivery_date') or None
        notes = request.POST.get('notes', '')
        status = request.POST.get('status', 'pending')
        customer, _ = Customer.objects.get_or_create(phone=phone, defaults={'name': name, 'address': address})
        if customer.name != name and name:
            customer.name = name
            customer.save()

        order = Order(customer=customer, delivery_date=delivery_date, notes=notes, status=status)
        order.save()

        item_names = request.POST.getlist('item_name[]')
        quantities = request.POST.getlist('quantity[]')
        prices = request.POST.getlist('price[]')
        total = 0
        for i, iname in enumerate(item_names):
            if iname:
                qty = int(quantities[i]) if quantities[i] else 1
                price = float(prices[i]) if prices[i] else 0
                oi = OrderItem(order=order, item_name=iname, quantity=qty, price=price)
                oi.save()
                total += oi.total
        order.total_amount = total
        order.save()

        # advance payment
        advance = request.POST.get('advance_amount', '0')
        pay_method = request.POST.get('pay_method', 'cash')
        if advance and float(advance) > 0:
            Payment.objects.create(order=order, amount=float(advance), method=pay_method)

        messages.success(request, f'Order {order.order_number} created!')
        return redirect('order_detail', pk=order.pk)
    customers = Customer.objects.all().order_by('name')
    return render(request, 'create_order.html', {'customers': customers, 'predefined_items': PREDEFINED_ITEMS})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'order_detail.html', {'order': order, 'predefined_items': PREDEFINED_ITEMS})

@login_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.status = request.POST.get('status', order.status)
        order.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': order.status, 'status_display': order.get_status_display()})
    return redirect('order_detail', pk=pk)

@login_required
def add_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        method = request.POST.get('method', 'cash')
        notes = request.POST.get('notes', '')
        if amount > 0:
            Payment.objects.create(order=order, amount=amount, method=method, notes=notes)
            messages.success(request, 'Payment recorded!')
    return redirect('order_detail', pk=pk)

@login_required
def receipt(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'receipt.html', {'order': order})

@login_required
def customers_list(request):
    search = request.GET.get('q', '')
    qs = Customer.objects.all().order_by('name')
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(phone__icontains=search))
    customers = list(qs)
    month_start = timezone.localdate().replace(day=1)
    return render(request, 'customers.html', {
        'customers': customers,
        'search': search,
        'customer_count': len(customers),
        'new_this_month': Customer.objects.filter(created_at__date__gte=month_start).count(),
        'active_customers': Customer.objects.filter(orders__status__in=['pending', 'in_process', 'ready']).distinct().count(),
    })

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.order_by('-order_date')
    return render(request, 'customer_detail.html', {'customer': customer, 'orders': orders})

@login_required
def add_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already exists!')
        else:
            Customer.objects.create(name=name, phone=phone, address=address)
            messages.success(request, 'Customer added!')
        return redirect('customers')
    return redirect('customers')

@login_required
def get_customer_by_phone(request):
    phone = request.GET.get('phone', '')
    try:
        c = Customer.objects.get(phone=phone)
        return JsonResponse({'found': True, 'name': c.name, 'address': c.address, 'id': c.id})
    except Customer.DoesNotExist:
        return JsonResponse({'found': False})

@login_required
def expenses_list(request):
    period = request.GET.get('period', 'month')
    today = timezone.localdate()
    if period == 'today':
        qs = Expense.objects.filter(date=today)
    elif period == 'year':
        qs = Expense.objects.filter(date__year=today.year)
    else:
        qs = Expense.objects.filter(date__year=today.year, date__month=today.month)
    expenses = list(qs.order_by('-date'))
    total = qs.aggregate(t=Sum('amount'))['t'] or 0
    average = (total / len(expenses)) if expenses else 0
    return render(request, 'expenses.html', {
        'expenses': expenses,
        'total': total,
        'period': period,
        'expense_count': len(expenses),
        'average_expense': average,
    })

@login_required
def add_expense(request):
    if request.method == 'POST':
        Expense.objects.create(
            title=request.POST.get('title'),
            amount=float(request.POST.get('amount', 0)),
            date=request.POST.get('date') or datetime.date.today(),
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Expense added!')
    return redirect('expenses')

@login_required
def delete_expense(request, pk):
    get_object_or_404(Expense, pk=pk).delete()
    messages.success(request, 'Expense deleted!')
    return redirect('expenses')

@login_required
def analytics(request):
    today = timezone.localdate()
    # Last 7 days revenue
    days_labels, days_revenue, days_expenses = [], [], []
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        rev = Payment.objects.filter(date__date=d).aggregate(t=Sum('amount'))['t'] or 0
        exp = Expense.objects.filter(date=d).aggregate(t=Sum('amount'))['t'] or 0
        days_labels.append(d.strftime('%d %b'))
        days_revenue.append(float(rev))
        days_expenses.append(float(exp))

    # Monthly revenue (last 12 months)
    months_labels, months_revenue = [], []
    for i in range(11, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12; y -= 1
        rev = Payment.objects.filter(date__year=y, date__month=m).aggregate(t=Sum('amount'))['t'] or 0
        months_labels.append(datetime.date(y, m, 1).strftime('%b %Y'))
        months_revenue.append(float(rev))

    # Payment method breakdown
    from django.db.models import Sum as S
    pm = Payment.objects.values('method').annotate(total=S('amount')).order_by('-total')
    pm_labels = [x['method'] for x in pm]
    pm_data = [float(x['total']) for x in pm]

    # Order status breakdown
    statuses = Order.objects.values('status').annotate(cnt=Count('id'))
    status_labels = [x['status'] for x in statuses]
    status_data = [x['cnt'] for x in statuses]

    # Item analytics
    from django.db.models import Sum as S2
    item_stats = OrderItem.objects.values('item_name').annotate(
        total_qty=Sum('quantity'), total_revenue=Sum('total')
    ).order_by('-total_qty')[:10]

    # Top customers
    top_customers = Customer.objects.annotate(
        total_orders=Count('orders'), total_paid=Sum('orders__payments__amount')
    ).order_by('-total_orders')[:5]

    # Monthly total revenue/expenses
    month_rev = Payment.objects.filter(date__year=today.year, date__month=today.month).aggregate(t=Sum('amount'))['t'] or 0
    month_exp = Expense.objects.filter(date__year=today.year, date__month=today.month).aggregate(t=Sum('amount'))['t'] or 0
    year_rev = Payment.objects.filter(date__year=today.year).aggregate(t=Sum('amount'))['t'] or 0
    year_exp = Expense.objects.filter(date__year=today.year).aggregate(t=Sum('amount'))['t'] or 0

    return render(request, 'analytics.html', {
        'days_labels': json.dumps(days_labels),
        'days_revenue': json.dumps(days_revenue),
        'days_expenses': json.dumps(days_expenses),
        'months_labels': json.dumps(months_labels),
        'months_revenue': json.dumps(months_revenue),
        'pm_labels': json.dumps(pm_labels),
        'pm_data': json.dumps(pm_data),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'item_stats': item_stats,
        'top_customers': top_customers,
        'month_rev': month_rev, 'month_exp': month_exp,
        'year_rev': year_rev, 'year_exp': year_exp,
        'month_profit': month_rev - month_exp,
        'year_profit': year_rev - year_exp,
    })

@login_required
def payments_list(request):
    payments = Payment.objects.select_related('order__customer').order_by('-date')[:100]
    orders_with_balance = Order.objects.filter(status__in=['pending','in_process','ready']).select_related('customer')
    pending_list = [o for o in orders_with_balance if o.balance() > 0]
    return render(request, 'payments.html', {
        'payments': payments,
        'pending_list': pending_list,
        'payment_total': sum(payment.amount for payment in payments),
        'pending_total': sum(order.balance() for order in pending_list),
    })
