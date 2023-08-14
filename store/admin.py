from django.contrib import admin
from .models import Address, Subscription, Category, Product, Cart, Order, ProductReview, ContactMessage, BlogPost
# Register your models here.
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'locality', 'city', 'state')
    list_filter = ('city', 'state')
    list_per_page = 10
    search_fields = ('locality', 'city', 'state')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category_image', 'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'is_active', 'is_featured')
    list_filter = ('is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'description')
    prepopulated_fields = {"slug": ("title", )}


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'get_sku', 'category', 'product_image', 'is_active', 'is_featured', 'updated_at')
    list_editable = ('slug', 'category', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    list_per_page = 10
    search_fields = ('title', 'category', 'short_description')
    prepopulated_fields = {"slug": ("title", )}

    def get_sku(self, obj):
        return obj.sku if obj.sku else 'Not Set'

    get_sku.short_description = 'SKU'

    def save_model(self, request, obj, form, change):
        if not obj.sku:  # Only generate SKU if it's not already set (i.e., it's a new product)
            last_product = Product.objects.order_by('-sku').first()
            if last_product:
                obj.sku = str(int(last_product.sku) + 1)
            else:
                obj.sku = '1'
        super().save_model(request, obj, form, change)
        
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_editable = ('quantity',)
    list_filter = ('created_at',)
    list_per_page = 20
    search_fields = ('user', 'product')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'status', 'ordered_date')
    list_editable = ('quantity', 'status')
    list_filter = ('status', 'ordered_date')
    list_per_page = 20
    search_fields = ('user', 'product')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'comment', 'date_posted')
    list_filter = ('rating', 'date_posted')
    search_fields = ('user__username', 'product__title')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish_date', 'display_image')
    list_filter = ('publish_date',)
    search_fields = ('title', 'content')

    def display_image(self, obj):
        if obj.image:
            return '<img src="{}" width="50" height="50" />'.format(obj.image.url)
        return None
    display_image.allow_tags = True
    display_image.short_description = 'Image'

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    list_filter = ('subscribed_at',)
    search_fields = ('email',)

admin.site.register(Address, AddressAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ProductReview, ReviewAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)