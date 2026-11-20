import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ChatMessage
from .chat_engine import generate_assistant_response, is_hindi

@login_required
def chat_page(request):
    messages_history = ChatMessage.objects.filter(user=request.user).order_by('created_at')[:40]
    return render(request, 'assistant/chat.html', {'chat_history': messages_history})

@login_required
@require_POST
def api_send_message(request):
    try:
        data = json.loads(request.body)
        user_text = data.get('message', '').strip()
    except Exception:
        user_text = request.POST.get('message', '').strip()

    if not user_text:
        return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

    lang = 'hi' if is_hindi(user_text) else 'en'

    # Save user message
    user_msg = ChatMessage.objects.create(
        user=request.user,
        role='user',
        content=user_text,
        language=lang
    )

    # Generate assistant answer
    reply_text = generate_assistant_response(request.user, user_text)

    # Save assistant response
    assistant_msg = ChatMessage.objects.create(
        user=request.user,
        role='assistant',
        content=reply_text,
        language=lang
    )

    return JsonResponse({
        'status': 'success',
        'reply': reply_text,
        'timestamp': assistant_msg.created_at.strftime('%H:%M'),
        'language': lang
    })

@login_required
@require_POST
def api_clear_chat(request):
    ChatMessage.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'cleared'})
