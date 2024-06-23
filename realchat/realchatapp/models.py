import os
import shortuuid
from PIL import Image
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ChatGroup(models.Model):
    group_name = models.CharField(max_length=130, unique=True, default=shortuuid.uuid)
    groupchat_name = models.CharField(max_length=130, null=True, blank=True)
    admin = models.ForeignKey(User, related_name='groupchats', blank=True, null=True, on_delete=models.SET_NULL)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(User, related_name='chat_group', blank=True)
    is_private= models.BooleanField(default=False)

    def __str__(self):
        return self.group_name
    
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=500, blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None

    def  __str__(self):
        if self.body:
            return f"{self.author.username} : {self.body}"
        elif self.file:
            return f"{self.author.username} : {self.filename}"

    
    class Meta:
        ordering = ["-created_at"]

    # @property
    # def is_image(self):
    #     if self.filename.lower().endwith(('.jpg', '.jpeg', '.gif', '.png', '.svg', 'webp')):
    #         return True
    #     else:
    #         return False
        

    @property
    def is_image(self):
        try:
            image = Image.open(self.file)
            image.verify()
            return True
        except:
            return False