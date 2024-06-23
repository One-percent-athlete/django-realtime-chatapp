from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib import messages
from .models import ChatGroup, GroupMessage
from .forms import CreateChatMessageFrom, CreateGroupchatForm, EditGroupchatForm

@login_required
def chat_home(request, chatroom_name='public'):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    chat_messages = chat_group.chat_messages.all()[:30]
    form = CreateChatMessageFrom()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            if request.user.emailaddress_set.filter(verified=True).exists():
                chat_group.members.add(request.user)
            else:
                messages.warning(request, 'You Need To Verify Your Email To Join The Chat.')
                return redirect('profile_settings')

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
    
    context = {
        "chat_messages": chat_messages, 
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
        'chat_group': chat_group,
    }

    return render(request, 'chatapp/chat.html', context)

@login_required
def get_or_create_chat(request, username):
    if request.user.username == username:
        return redirect('home')
    
    other_user = User.objects.get(username=username)
    my_private_chatrooms = request.user.chat_group.filter(is_private=True)

    if my_private_chatrooms.exists():
        for chatroom in my_private_chatrooms:
            if other_user in chatroom.members.all():
                return redirect('chatroom', chatroom.group_name)
                
            else:
                chatroom = ChatGroup.objects.create(is_private=True)
                chatroom.members.add(other_user, request.user)

    chatroom = ChatGroup.objects.create(is_private=True)
    chatroom.members.add(other_user, request.user)

    return redirect('chatroom', chatroom.group_name)

@login_required
def create_groupchat(request):
    form = CreateGroupchatForm()

    if request.method == "POST":
        form = CreateGroupchatForm(request.POST)
        if form.is_valid():
            groupchat = form.save(commit=False)
            groupchat.admin = request.user
            groupchat.save()
            groupchat.members.add(request.user)
            return redirect('chatroom', groupchat.group_name)

    return render(request, 'chatapp/create_groupchat.html', {"form": form})

@login_required
def edit_groupchat(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    form = EditGroupchatForm(instance=chat_group)
    if request.method == 'POST':
        form = EditGroupchatForm(request.POST, instance=chat_group)
        if form.is_valid():
            form.save()

            remove_members = request.POST.getlist("remove_members")
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                chat_group.members.remove(member)
            return redirect('chatroom', chatroom_name)

    return render(request, 'chatapp/edit_groupchat.html', {"form":form, 'chat_group':chat_group})

@login_required
def delete_groupchat(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    if request.method =='POST':
        chat_group.delete()
        messages.success(request, "Chatgroup Deleted..")
        return redirect('home')
    
    return render(request, 'chatapp/delete_groupchat.html', {"chat_group":chat_group} )

@login_required
def leave_chat(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()
    
    if request.method =='POST':
        chat_group.members.remove(request.user)
        messages.success(request, "You Left The Chat")
        return redirect('home')
    
    return render(request, 'chatapp/leave_chat.html', {"chat_group":chat_group} )

@login_required
def upload_file(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    if request.htmx and request.FILES:
        file = request.FILES['file']
        message = GroupMessage.objects.create(
            file = file,
            author = request.user,
            group = chat_group
        )
        channel_layer = get_channel_layer()
        event = {
            'type':'message_handler',
            'message_id': message.id
        }

        async_to_sync(channel_layer.group_send)(
            chatroom_name, event
        )
    return HttpResponse()