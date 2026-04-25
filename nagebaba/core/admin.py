from django.contrib import admin
from .models import Customer, Item, Order, OrderItem, Payment, Expense

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'address', 'created_at']
    search_fields = ['name', 'phone']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'total_amount', 'order_date']
    list_filter = ['status']
    search_fields = ['order_number', 'customer__name']
    inlines = [OrderItemInline, PaymentInline]

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'default_price']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'date']
    list_filter = ['date']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'method', 'date']
