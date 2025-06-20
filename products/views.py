from django.shortcuts import render, get_object_or_404
from django.db.models import F
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Product
from .serializers import ProductSerializer


class ProductListCreateView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductComparsionListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        if self.kwargs:
            tipo = self.kwargs['type']
            return Product.objects.filter(type=tipo)
        else:
            return Product.objects.all()


class ProductRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'type'

    def get_queryset(self):
        tipo = self.kwargs['type']
        produto = get_object_or_404(Product, type=tipo)
        return Product.objects.filter(id=produto.id)


class ProductRequestHUBView(APIView):
    """
    - Requisição que o HUB faz para o CD
    - CD retorna a quantidade requisitada apenas se pre-requisitos forem verdadeiros
    """
    def patch(self, request, type, qtd):
        quantity = self.kwargs.get('qtd')

        if not quantity:
            return Response({
                "error": "Quantity not specified!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)

            if quantity <= 0:
                return Response({
                    "error": "Quantity can not be 0 or lower!"
                }, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({"error": "Invalid quantity format!"}, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, type=type)

        if product.quantity < quantity:
            return Response({"error": f"Not enough {product.type}!"}, status=status.HTTP_412_PRECONDITION_FAILED)
        else:
            Product.objects.filter(type=product.type).update(
            quantity=F('quantity') - quantity
            )
            
            product.refresh_from_db()

            return Response({
                "status": "success",
                "message": f"{quantity} {product.type}(s) has been sent to the HUB!",
                "info": f"{product.type} current quantity: {product.quantity}"
            }, status=status.HTTP_200_OK)


class ProductDestroyAPIView(DestroyAPIView):
    serializer_class = ProductSerializer
    
    def get_object(self):
        product_type = self.kwargs['type']
        return get_object_or_404(Product, type=product_type)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        product_type = instance.type
        
        self.perform_destroy(instance)

        return Response({
            "status": "success",
            "message": f"{product_type} has been deleted!"
        }, status=status.HTTP_200_OK)


class ProductPatchIncrement(APIView):
    """
    - Endpoint que adiciona produtos de forma segura no objeto.
    - Operações feitas no nível do banco de dados.
    """
    def patch(self, request, type, qtd):
        quantity = self.kwargs.get('qtd')

        if not quantity:
            return Response({"error": "Quantity not specified!"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response({"error": "Quantity is not valid!"}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({"error": "Invalid quantity format!"}, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, type=type)
        
        Product.objects.filter(pk=product.id).update(
            quantity=F('quantity') + quantity
        )

        product.refresh_from_db()

        return Response({
            "status": "success",
            "message": f"{product.type} quantity increased by {quantity}",
            "new quantity": product.quantity,
        }, status=status.HTTP_200_OK)