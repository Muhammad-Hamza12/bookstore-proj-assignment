from rest_framework import serializers
from .models import Book, Author, Category
from django.contrib.auth.models import User

#Author Serialiser to manage author json serialization
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

#Category Serialiser to manage category json serialization
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

#Book Serialiser to manage book json serialization
class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    category = CategorySerializer()
    class Meta:
        model = Book
        fields = '__all__'
    
    def update(self, instance, validated_data):
        # Handle nested author update
        author_data = validated_data.pop('author')
        author, created = Author.objects.get_or_create(name=author_data['name'])
        instance.author = author

        # Handle nested category update
        category_data = validated_data.pop('category')
        category, created = Category.objects.get_or_create(name=category_data['name'])
        instance.category = category

        # Update the rest of the fields
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        
        return instance
    
    def create(self, validated_data):
        author_data = validated_data.pop('author')
        category_data = validated_data.pop('category')

        author_instance, created = Author.objects.get_or_create(**author_data)
        category_instance, created = Category.objects.get_or_create(**category_data)

        book_instance = Book.objects.create(
            author=author_instance,
            category=category_instance,
            **validated_data
        )

        return book_instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user