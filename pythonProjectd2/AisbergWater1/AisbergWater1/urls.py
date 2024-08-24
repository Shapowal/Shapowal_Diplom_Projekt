from django.contrib import admin
from django.urls import path, include
from sklad1.views import *

from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    # Административный интерфейс Django
    path('admin/', admin.site.urls),

    # Пользовательская регистрация
    path('register/', register, name='register'),

    # Пользовательский вход в систему
    path('login/', login_view, name='login'),

    # Производственные операции
    path('production/', production_view, name='production'),  # Страница для управления производственными процессами
    path('production_main/', production_main, name='production_main'),  # Основная страница для управления производственными процессами

    # Складские операции
    path('warehouse/', warehouse_view, name='warehouse'),  # Страница для управления складом
    path('finished_goods_warehouse/', finished_goods_warehouse_view, name='finished_goods_warehouse'),  # Страница для управления складом готовой продукции

    # Главная страница сайта
    path('', home, name='home'),

    # Создание и управление линиями
    path('create_line/', create_line, name='create_line'),  # Форма для создания новой линии
    path('add-product/', add_product_to_line, name='add_product_to_line'),  # Форма для добавления продукта к линии

    # Создание и управление партиями
    path('create_batch/', create_batch, name='create_batch'),  # Форма для создания новой партии
    path('view_stock/', view_stock, name='view_stock'),  # Просмотр текущих остатков на складе

    # Получение и списание материалов
    path('receive_materials/', receive_materials, name='receive_materials'),  # Форма для получения новых материалов
    path('write_off_stock/', write_off_stock, name='write_off_stock'),  # Форма для списания остатков

    # Проверка расходов
    path('check_expenses/', check_expenses, name='check_expenses'),  # Страница для проверки расходов

    # Управление готовой продукцией
    path('view_finished_goods_stock/', view_finished_goods_stock, name='view_finished_goods_stock'),  # Просмотр остатков готовой продукции
    path('receive_finished_goods/', receive_finished_goods, name='receive_finished_goods'),  # Форма для получения готовой продукции
    path('ship_finished_goods/', ship_finished_goods, name='ship_finished_goods'),  # Форма для отгрузки готовой продукции

    # Списки и редакторы
    path('lines/', LineListView.as_view(), name='line_list'),  # Список всех линий
    path('product-list/', product_list, name='product_list'),  # Список всех продуктов
    path('batch_list/', batch_list, name='batch_list'),  # Список всех партий
    path('create_material/', create_material, name='create_material'),  # Форма для создания нового материала
    path('material_list/', material_list, name='material_list'),  # Список всех материалов
    path('create_product_material/', create_product_material, name='create_product_material'),  # Форма для создания связи продукта и материала
    path('product_material_list/', product_material_list, name='product_material_list'),  # Список связей продуктов и материалов

    # Управление запасами и отгрузками
    path('release_products/', release_products, name='release_products'),  # Форма для выпуска продукции
    path('add_stock/', add_stock, name='add_stock'),  # Форма для добавления запасов
    path('edit_stock/<int:stock_id>/', edit_stock, name='edit_stock'),  # Форма для редактирования конкретного запаса
    path('view_and_edit_stock/', view_and_edit_stock, name='view_and_edit_stock'),  # Просмотр и редактирование запасов

    # Управление отгрузками
    path('create_shipment/', create_shipment, name='create_shipment'),  # Форма для создания новой отгрузки
    path('view_shipments/', view_shipments, name='view_shipments'),  # Список всех отгрузок

    # Проверка поступлений
    path('check_incoming/', check_incoming, name='check_incoming'),  # Страница для проверки поступлений на склад

    # Управление контрагентами
    path('create_counterparty/', create_counterparty, name='create_counterparty'),  # Форма для создания нового контрагента
    path('counterparty_list/', counterparty_list, name='counterparty_list'),  # Список всех контрагентов

    # Запасы готовой продукции
    path('finished_goods_stock_list/', finished_goods_stock_list, name='finished_goods_stock_list'),  # Список остатков готовой продукции
]