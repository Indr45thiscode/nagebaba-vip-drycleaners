from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('orders/', views.orders_list, name='orders'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:pk>/payment/', views.add_payment, name='add_payment'),
    path('orders/<int:pk>/receipt/', views.receipt, name='receipt'),
    path('customers/', views.customers_list, name='customers'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/search/', views.get_customer_by_phone, name='customer_search'),
    path('expenses/', views.expenses_list, name='expenses'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/<int:pk>/delete/', views.delete_expense, name='delete_expense'),
    path('analytics/', views.analytics, name='analytics'),
    path('payments/', views.payments_list, name='payments'),
]
