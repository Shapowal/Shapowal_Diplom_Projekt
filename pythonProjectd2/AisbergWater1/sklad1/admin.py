from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import (
    CustomUser, Line, Product, Batch, MeasurementUnit, Material, Stock, ProductMaterial,
    Counterparty, Shipment, FinishedGoodsStock, ShipmentItem
)

# Админка для CustomUser
class CustomUserAdmin(DefaultUserAdmin):
    model = CustomUser
    list_display = ('username', 'role', 'email', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)

# Админка для Line
class LineAdmin(admin.ModelAdmin):
    list_display = ('name', 'volume', 'number')
    search_fields = ('name', 'number')
    ordering = ('name',)

admin.site.register(Line, LineAdmin)

# Админка для Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'gtin', 'volume', 'line')
    search_fields = ('name', 'gtin')
    list_filter = ('line',)
    ordering = ('name',)

admin.site.register(Product, ProductAdmin)

# Админка для Batch
class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'product', 'line', 'production_date', 'quantity', 'is_used')
    search_fields = ('batch_number', 'product__name', 'line__name')
    list_filter = ('is_used', 'production_date')
    ordering = ('-production_date',)

admin.site.register(Batch, BatchAdmin)

# Админка для MeasurementUnit
class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

admin.site.register(MeasurementUnit, MeasurementUnitAdmin)

# Админка для Material
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name',)
    list_filter = ('unit',)
    ordering = ('name',)

admin.site.register(Material, MaterialAdmin)

# Админка для Stock
class StockAdmin(admin.ModelAdmin):
    list_display = ('material', 'quantity')
    search_fields = ('material__name',)
    ordering = ('material',)

admin.site.register(Stock, StockAdmin)

# Админка для ProductMaterial
class ProductMaterialAdmin(admin.ModelAdmin):
    list_display = ('product', 'material', 'quantity')
    search_fields = ('product__name', 'material__name')
    ordering = ('product', 'material')

admin.site.register(ProductMaterial, ProductMaterialAdmin)

# Админка для Counterparty
class CounterpartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact_number')
    search_fields = ('name', 'address')
    ordering = ('name',)

admin.site.register(Counterparty, CounterpartyAdmin)

# Админка для Shipment
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('product', 'batch', 'quantity', 'shipment_date', 'counterparty')
    search_fields = ('product__name', 'batch__batch_number', 'counterparty__name')
    list_filter = ('shipment_date',)
    ordering = ('-shipment_date',)

admin.site.register(Shipment, ShipmentAdmin)

# Админка для FinishedGoodsStock
class FinishedGoodsStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'batch_number', 'production_date', 'quantity', 'is_used')
    search_fields = ('product__name', 'batch_number')
    list_filter = ('is_used', 'production_date')
    ordering = ('-production_date',)

admin.site.register(FinishedGoodsStock, FinishedGoodsStockAdmin)

# Админка для ShipmentItem
class ShipmentItemAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'product', 'batch', 'quantity')
    search_fields = ('shipment__id', 'product__name', 'batch__batch_number')
    ordering = ('shipment', 'product')

admin.site.register(ShipmentItem, ShipmentItemAdmin)