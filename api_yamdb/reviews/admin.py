from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'description', 'category')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'role',
        'first_name',
        'last_name',
        'email',
        'bio',
    )
    list_editable = ('role',)
    list_filter = ('role',)
    search_fields = ('username',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'score', 'pub_date')
    ordering = ('-score',)
    list_per_page = 10


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'text', 'author', 'pub_date')
    ordering = ('-pub_date', )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
