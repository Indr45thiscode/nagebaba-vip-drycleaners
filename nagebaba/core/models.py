from django.db import models
from django.utils import timezone
import datetime


class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

    def total_spent(self):
        return sum(order.total_amount for order in self.orders.all())

    def last_visit(self):
        last = self.orders.order_by('-order_date').first()
        return last.order_date if last else None


class Item(models.Model):
    name = models.CharField(max_length=100)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_process', 'In Process'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
    ]
    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.order_number

    def paid_amount(self):
        return sum(payment.amount for payment in self.payments.all())

    def balance(self):
        return self.total_amount - self.paid_amount()

    def payment_status(self):
        paid = self.paid_amount()
        if paid <= 0:
            return 'unpaid'
        if paid >= self.total_amount:
            return 'paid'
        return 'partial'

    @classmethod
    def generate_order_number(cls):
        last = cls.objects.order_by('-id').first()
        num = (last.id + 1) if last else 1
        return f"DC-{num:04d}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            last = Order.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.order_number = f"DC-{num:04d}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('phonepe', 'PhonePe'),
        ('gpay', 'Google Pay'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    date = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.order.order_number} - Rs. {self.amount}"


class Expense(models.Model):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - Rs. {self.amount}"
