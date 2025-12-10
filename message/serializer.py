from rest_framework import serializers
from .models import Conversation, Message

class SenderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField(source='get_full_name')
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_picture:
            return obj.profile.profile_picture.url
        return None

class ReplyToSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    content = serializers.CharField()
    sender = SenderSerializer()

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender = SenderSerializer(read_only=True)
    reply_to = ReplyToSerializer(read_only=True)
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender_username', 'sender', 'content', 'timestamp', 'reply_to', 'attachment', 'attachment_type']

    def get_attachment(self, obj):
        if obj.attachment:
            return {
                'url': obj.attachment.url,
                'name': obj.get_attachment_filename(),
                'type': obj.attachment_type
            }
        return None
        
class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.StringRelatedField(many=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'is_team', 'participants', 'last_message', 'updated_at']
        
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None
    
class ConversationDetailSerializer(serializers.ModelSerializer):
    participants = serializers.StringRelatedField(many=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'is_team', 'participants', 'messages', 'updated_at']