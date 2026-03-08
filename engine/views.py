from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import StreamingHttpResponse

from .llm.router import LLMRouter
from .prompt_builder import build_prompts
from .models import LLMRequest
from .utils.output_cleaner import clean_output

import json

router = LLMRouter()


@api_view(["POST"])
def generate_code(request):
    body = json.loads(request.body)
    prompt = body.get("prompt")

    if not prompt or not prompt.strip():
        return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(prompt) > 5000:
        return Response({"error": "Prompt too long"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        system_prompt, user_prompt = build_prompts(prompt)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
    
    model, stream = router.stream(system_prompt, user_prompt)

    wrapped_stream = stream_and_store(prompt, model, stream)

    response = StreamingHttpResponse(
        wrapped_stream, 
        content_type="text/plain"
    )

    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"

    return response




@api_view(["GET"])
def history(request):
    entries = LLMRequest.objects.order_by("-created_at")[:20]

    data = [
        {
            "id": e.id,
            "prompt": e.prompt,
            "model": e.model, 
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


def stream_and_store(prompt, model, stream):
    full_response = []
    try:
        for chunk in stream:
            full_response.append(chunk)
            yield chunk
    finally:
        final_text = "".join(full_response).strip()
        final_text = clean_output(final_text)

        if not final_text:
            return
        
        if final_text.startswith("LLM "):
            return

        LLMRequest.objects.create(
            prompt=prompt,
            model=model,
            response=final_text
        )

