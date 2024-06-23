from django.urls import path
from . import views


urlpatterns = [
    path("", views.chat_home, name="home"),
    path("chat/<username>", views.get_or_create_chat, name="start_chat"),
    path("<chatroom_name>", views.chat_home, name="chatroom"),
    path("chat/create_groupchat/", views.create_groupchat, name="create_groupchat"),
    path("chat/edit/<chatroom_name>", views.edit_groupchat, name="edit_groupchat"),
    path("chat/delete/<chatroom_name>", views.delete_groupchat, name="delete_groupchat"),
    path("chat/leave/<chatroom_name>", views.leave_chat, name="leave_chat"),
    path("chat/upload_file/<chatroom_name>", views.upload_file, name="upload_file")
]
