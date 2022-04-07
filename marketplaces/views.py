from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from marketplaces.models import (
    Marketplaces
)
from marketplaces.serializers import (
    MarketplacesSerializer,
    MarketplaceSerializer
)
from django.http import Http404

class MarketplacesList(APIView):
    """
    List all marketplaces, or create a new marketplace.
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = MarketplacesSerializer

    def get(self, request, format=None):
        marketplaces = Marketplaces.objects.filter(user=request.user, is_archived=False)
        serializer = MarketplacesSerializer(marketplaces, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data
        data['user'] = request.user.id
        serializer = MarketplacesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarketplaceDetailView(APIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = MarketplaceSerializer

    def get_object(self, unique_id):
        try:
            return Marketplaces.objects.get(
                unique_id=unique_id,
                is_archived=False
            )
        except Marketplaces.DoesNotExist:
            raise Http404

    def get(self, request, unique_id, format=None):
        marketplace = self.get_object(unique_id)
        serializer = MarketplaceSerializer(marketplace)
        return Response(serializer.data)

    def put(self, request, unique_id, format=None):
        marketplace = self.get_object(unique_id)
        serializer = MarketplaceSerializer(
            marketplace,
            data=request.data,
            user=request.user
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, unique_id, format=None):
        marketplace = self.get_object(unique_id)
        marketplace.is_archived = True
        marketplace.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
