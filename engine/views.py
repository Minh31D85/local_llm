from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from services.llm import OllamaService

serv = OllamaService()

@api_view(["POST"])
def generate_code(request):
    prompt = request.data.get("prompt")
    language = request.data.get("language")

    if not prompt:
        return Response(
            {"error": "Prompt is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not language:
        return Response(
            {"error": "Language is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(prompt) > 5000:
        return Response(
            {"error": "Prompt too long"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = serv.generate(prompt, language)
    return Response({"code": result})