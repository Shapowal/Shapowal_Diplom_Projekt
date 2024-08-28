from django.contrib import admin
from django.urls import path, include
from sklad1.views import *

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('production/', production_view, name='production'),
    path('warehouse/', warehouse_view, name='warehouse'),
    path('finished_goods_warehouse/', finished_goods_warehouse_view, name='finished_goods_warehouse'),
    path('', home, name='home'),
    path('production_main/', production_main, name='production_main'),
    path('create_line/', create_line, name='create_line'),
    path('add-product/', add_product_to_line, name='add_product_to_line'),  # Изменил название пути
    path('create_batch/', create_batch, name='create_batch'),
    path('view_stock/', view_stock, name='view_stock'),
    path('receive_materials/', receive_materials, name='receive_materials'),
    path('write_off_stock/', write_off_stock, name='write_off_stock'),
    path('check_expenses/', check_expenses, name='check_expenses'),
    path('view_finished_goods_stock/', view_finished_goods_stock, name='view_finished_goods_stock'),
    path('receive_finished_goods/', receive_finished_goods, name='receive_finished_goods'),
    path('ship_finished_goods/', ship_finished_goods, name='ship_finished_goods'),
    path('lines/', LineListView.as_view(), name='line_list'),
    path('product-list/', product_list, name='product_list'),
    path('batch_list/', batch_list, name='batch_list'),

    path('create_material/', create_material, name='create_material'),
    path('material_list/', material_list, name='material_list'),
    path('create_product_material/', create_product_material, name='create_product_material'),
    path('product_material_list/', product_material_list, name='product_material_list'),
    path('release_products/', release_products, name='release_products'),
    path('add_stock/', add_stock, name='add_stock'),
    path('edit_stock/<int:stock_id>/', edit_stock, name='edit_stock'),
    path('view_and_edit_stock/', view_and_edit_stock, name='view_and_edit_stock'),
    path('create_shipment/', create_shipment, name='create_shipment'),
    path('view_shipments/', view_shipments, name='view_shipments'),
    path('check_incoming/', check_incoming, name='check_incoming'),
    path('create_counterparty/', create_counterparty, name='create_counterparty'),
    path('counterparty_list/', counterparty_list, name='counterparty_list'),
    path('finished_goods_stock_list/', finished_goods_stock_list, name='finished_goods_stock_list'),
]