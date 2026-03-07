from django.db import models

class LLMRequest(models.Model):
    prompt = models.TextField()
    model = models.CharField(max_length=50, blank=True)
    response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
