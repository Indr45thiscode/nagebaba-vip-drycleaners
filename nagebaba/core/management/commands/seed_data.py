from django.core.management.base import BaseCommand
from core.models import Customer, Order, OrderItem, Payment, Expense, Item
from django.utils import timezone
import datetime, random

class Command(BaseCommand):
    help = 'Seed sample data'

    def handle(self, *args, **kwargs):
        items_data = [('Saree',80),('Shirt',40),('Pant',40),('Saree Blouse',30),('Top',35),('Ghagra',60),('Coat/Blazer',100),('Blanket',120),('Mandap',500),('Cushion',50),('Shoes',80),('Jacket',90)]
        for name, price in items_data:
            Item.objects.get_or_create(name=name, defaults={'default_price': price})

        customers_data = [('Priya Sharma','9876543210','Koregaon Park'),('Rahul Mehta','9765432109','Baner'),('Sunita Patil','9654321098','Kothrud'),('Amit Joshi','9543210987','Aundh'),('Rekha Singh','9432109876','Viman Nagar')]
        customers = []
        for name, phone, addr in customers_data:
            c, _ = Customer.objects.get_or_create(phone=phone, defaults={'name':name,'address':addr})
            customers.append(c)

        item_names = ['Saree','Shirt','Pant','Coat/Blazer','Blanket','Ghagra']
        item_prices = {'Saree':80,'Shirt':40,'Pant':40,'Coat/Blazer':100,'Blanket':120,'Ghagra':60}
        for i in range(20):
            customer = random.choice(customers)
            status = random.choice(['pending','in_process','ready','delivered'])
            days_ago = random.randint(0,30)
            order_date = timezone.now() - datetime.timedelta(days=days_ago)
            order = Order(customer=customer, status=status, order_date=order_date, delivery_date=(order_date+datetime.timedelta(days=3)).date())
            order.save()
            total = 0
            for _ in range(random.randint(1,3)):
                iname = random.choice(item_names)
                qty = random.randint(1,2)
                price = item_prices[iname]
                oi = OrderItem(order=order,item_name=iname,quantity=qty,price=price)
                oi.save()
                total += oi.total
            order.total_amount = total
            order.save()
            if status in ['delivered','ready']:
                Payment.objects.create(order=order,amount=total,method=random.choice(['cash','upi','gpay']),date=order_date)
            elif status == 'in_process':
                Payment.objects.create(order=order,amount=float(total)*0.5,method='cash',date=order_date)

        today = datetime.date.today()
        for title, amount in [('Detergent',500),('Electricity',1200),('Salary',8000),('Pressing fuel',300)]:
            Expense.objects.get_or_create(title=title,date=today,defaults={'amount':amount})

        self.stdout.write(self.style.SUCCESS('Data seeded!'))
