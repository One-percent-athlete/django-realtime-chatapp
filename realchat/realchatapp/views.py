from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatGroup, GroupMessage
from .forms import CreateChatMessageFrom

@login_required
def chat_home(request):
    chat_group = get_object_or_404(ChatGroup, group_name="public")

    chat_messages = chat_group.chat_messages.all()[:30]
    form = CreateChatMessageFrom()

    if request.htmx:
        form = CreateChatMessageFrom(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                'message':message,
                'user': request.user
            }
        return render(request, 'chatapp/chat_message_p.html', context)

    return render(request, 'chatapp/chat.html', {"chat_messages": chat_messages, 'form': form})