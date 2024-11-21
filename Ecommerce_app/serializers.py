from rest_framework.serializers import IntegerField,SerializerMethodField,ModelSerializer,ValidationError,CharField,DateTimeField,DecimalField
from django.contrib.auth import get_user_model
from .models import Category, Order, OrderItem, Product, Cart, CartItem

User = get_user_model()

class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username','email','password','address','phone_number','user_type']

    def create(self,validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            address=validated_data.get('address'),
            phone_number=validated_data.get('phone_number'),
            user_type=validated_data.get('user_type','customer')
            )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def update(self,instance,validated_data):
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.username = validated_data.get('username')
        instance.phone_number = validated_data.get('email')
        instance.email = validated_data.get('email')
        instance.address = validated_data.get('address')
        instance.save()
        return instance
    
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','description']

class ProductSerializer(ModelSerializer):
    # category = CategorySerializer()
    category_name = CharField(source='category.name',read_only=True)
    created_at = DateTimeField(format='%d-%m-%Y,%H:%M',read_only=True)
    updated_at = DateTimeField(format='%d-%m-%Y,%H:%M',read_only=True)
    product_name = CharField(source='name')
    # product_id = IntegerField(source='id',read_only=True)
    class Meta:
        model = Product
        fields = ['id','product_name','description','price','stock','category','category_name','created_at','updated_at']

    def to_representation(self,instance):
        representation = super().to_representation(instance)
        return {key:value for key,value in representation.items() if value not in [None,'']}

class CartItemSerializer(ModelSerializer):
    product_name = CharField(source='product.name',read_only=True)
    product_price = DecimalField(source='product.price',max_digits=10,decimal_places=2,read_only=True)

    class Meta:
        model = CartItem
        fields = ['id','product','product_name','product_price','quantity','added_at']

    def validate(self,data):
        product = data.get('product')
        quantity = data.get('quantity')

        if quantity > product.stock:
            raise ValidationError(f"Requested quantity ({quantity}) exceeds available stock ({product.stock})")
        
        return data

class CartSerializer(ModelSerializer):
    items = CartItemSerializer(many=True,read_only=True)
    total_price = SerializerMethodField(read_only=True)
    created_at = DateTimeField(format='%d-%m-%Y,%H:%M',read_only=True)
    updated_at = DateTimeField(format='%d-%m-%Y,%H:%M',read_only=True)

    class Meta:
        model = Cart
        fields = ['id','user','items','total_price','created_at','updated_at']

    def get_total_price(self,obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())
    
class OrderItemSerialzer(ModelSerializer):
    product_name = CharField(source='product.name',read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id','product','product_name','quantity','price']

class OrderSerializer(ModelSerializer):
    items = OrderItemSerialzer(many=True,read_only=True)
    status = CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['id','user','total_price','status','items','created_at','updated_at']