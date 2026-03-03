from django.db import models

class LLMRequest(models.Model):
    MODE_CHOICES = [
        ("generate", "Generate"),
        ("analyze", "Analyze"),
    ]

    LANGUAGE_CHOICES = [
        ("python", "Python"),
        ("javascript", "JavaScript"),
        ("typescript", "TypeScript"),
        ("csharp", "C#"),
        ("microsoftsql", "Microsoft SQL"),
    ]

    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    prompt = models.TextField()
    response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
