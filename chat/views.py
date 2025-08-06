from rest_framework.views import APIView
from rest_framework.response import Response

class ConversationListView(APIView):
    def get(self, request):
        return Response({"message": "Conversation list placeholder"})

class ConversationDetailView(APIView):
    def get(self, request, pk):
        return Response({"message": f"Conversation detail placeholder for {pk}"})
class MessageListView(APIView):
    def get(self, request, conversation_id):
        return Response({"message": f"Message list placeholder for conversation {conversation_id}"})

class MessageDetailView(APIView):
    def get(self, request, pk):
        return Response({"message": f"Message detail placeholder for {pk}"})
from rest_framework.decorators import api_view
from rest_framework.response import Response


class QuickReplyListView(APIView):
    def get(self, request):
        return Response({"message": "Quick reply list placeholder"})
from rest_framework.views import APIView
from rest_framework.response import Response

class AnalysisSessionListView(APIView):
    def get(self, request):
        return Response({"message": "Analysis session list placeholder"})
@api_view(['POST'])
def send_message(request):
    return Response({"message": "Send message placeholder"})