from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK,HTTP_204_NO_CONTENT,HTTP_201_CREATED,HTTP_400_BAD_REQUEST,HTTP_404_NOT_FOUND
from rest_framework.response import Response
from .serializers import OrderSerializer, UserSerializer,CategorySerializer,CartSerializer,ProductSerializer,CartItemSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .models import Category, OrderItem,Product,Cart,CartItem,Order
from rest_framework.generics import RetrieveUpdateDestroyAPIView,ListCreateAPIView
from .permissions import IsAdmin

User = get_user_model()

class RegisterView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'Message:User Registered Successfully'},status=HTTP_201_CREATED)
        return Response({'Message':'hello'},status=HTTP_200_OK)
    
class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username and password:
            return Response({'Message':'username and password must be provided'},status=HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User,username=username)
        if user.check_password:
            token,created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(instance=user)
            return Response({'token':token.key,'serializer':serializer.data},status=HTTP_200_OK)
        return Response({'Error':'Invalid Credentials'},status=HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    def post(self,request):
        user=request.user
        try:
            user.auth_token.delete()
            return Response({'Message':'Logged Out Successfully'},status=HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'Error':'Token not found'},status=HTTP_400_BAD_REQUEST)
        
class HelloView(APIView):
    def get(self,request):
        return Response({'message':'hello'},status=HTTP_200_OK)

class CategoryView(APIView):
    permission_classes = [IsAdmin]
    def post(self,request):
        data = request.data
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=HTTP_201_CREATED)
        return Response(serializer.errors,status=HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories,many=True)
        return Response(serializer.data,status=HTTP_200_OK)

class AdminProductView(ListCreateAPIView):
    permission_classes = [IsAdmin]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class AdminProductDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class UserProductView(APIView):
    def get(self,request):
        products = Product.objects.all()
        serializer = ProductSerializer(products,many=True)
        return Response(serializer.data,status=HTTP_200_OK)
    
class UserProductDetailView(APIView):
    def get(self,request,pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'Error':'Item not found'},status=HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response(serializer.data,status=HTTP_200_OK)
    
class UserProfileView(APIView):
    def get(self,request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data,status=HTTP_200_OK)
    
    def put(self,request):
        data = request.data
        user = request.user
        serializer = UserSerializer(user,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'Message':'User updated Successfully'},status=HTTP_201_CREATED)
        return Response(serializer.errors,status=HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        user = request.user
        try:
            User.objects.get(username=user.username).delete()
            return Response({'user deleted Succfully'},status=HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'user noot found'},status=HTTP_404_NOT_FOUND)


class CartView(APIView):
    def get(self,request):
        cart,_ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
class AddCartItemView(APIView):
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        data = request.data
        product = Product.objects.get(id=data['product_id'])
        
        if int(data['quantity']) > product.stock:
            return Response({"error": "Requested quantity exceeds available stock."},status=HTTP_400_BAD_REQUEST)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = data['quantity']
        cart_item.save()
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=HTTP_201_CREATED)

class RemoveCartItemView(APIView):
    def delete(self, request):
        cart = Cart.objects.get(user=request.user)
        product_id = request.data.get('product_id')
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response({"message": "Product removed from cart."})
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Product not found in cart."},
                status=HTTP_404_NOT_FOUND,
            )

class ClearCartView(APIView):
    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        return Response({"message": "Cart cleared successfully."})

class PlaceOrderView(APIView):
    def post(self,request):
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            return Response({"error":"Your cart is empty."},status=HTTP_400_BAD_REQUEST)
        
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())
        order = Order.objects.create(user=user,total_price=total_price)

        for cart_item in cart.items.all():
            if cart_item.quantity > cart_item.product.stock:
                return Response({"error": f"Not enough stock for {cart_item.product.name}."},status=HTTP_400_BAD_REQUEST)
            
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        cart.items.all().delete()

        return Response({"message":"Order Placed Successsfully", "oder_id":order.id},status=HTTP_200_OK)

class ListOrdersView(APIView):
    def get(self,request):
        user = request.user
        orders = Order.objects.filter(user=user).order_by('-created_at')
        serializer = OrderSerializer(orders,many=True)
        return Response(serializer.data)
    
class OrderDetailView(APIView):
    def get(self,request,order_id):
        user = request.user
        try:
            order = Order.objects.get(id=order_id,user=user)
        except Order.DoesNotExist:
            return Response({"error":"Order not found."},status=HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(order)
        return Response(serializer.data,status=HTTP_200_OK)