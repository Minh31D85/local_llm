from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services.llm import OllamaService
from .promp_builder import build_prompts
from .models import LLMRequest

serv = OllamaService()

@api_view(["POST"])
def generate_code(request):
    prompt = request.data.get("prompt")
    mode = request.data.get("mode")

    if not prompt or not prompt.strip():
        return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(prompt) > 5000:
        return Response({"error": "Prompt too long"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        system_prompt, user_prompt = build_prompts(mode, prompt)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    result = serv.generate(system_prompt, user_prompt)

    if not isinstance(result,str):
        return Response({"error": "Invalid LLM response"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if result.startswith("LLM "):
        return Response({"error": result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    db_entry = LLMRequest.objects.create(
        mode=mode,
        language="auto",
        prompt=prompt,
        response = result
    )

    return Response({
        "id": db_entry.id,
        "code": result
        })


@api_view(["GET"])
def history(request):
    entries = LLMRequest.objects.order_by("-created_at")[:20]

    data = [
        {
            "id": e.id,
            "mode": e.mode,
            "language": e.language,
            "prompt": e.prompt,
            "response": e.response,
            "created_at": e.created_at
        }
        for e in entries
    ]
    return Response(data)


@api_view(["DELETE"])
def del_history_entry(request, entry_id):
    try:
        entry = LLMRequest.objects.get(id=entry_id)
        entry.delete()
        return Response({"success": True})
    except LLMRequest.DoesNotExist:
        return Response({"error": "Entry not found"}, status=status.HTTP_404_NOT_FOUND)


def index(request):
    return render(request, "index.html")