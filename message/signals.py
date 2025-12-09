from django.db.models.signals import post_save
from django.dispatch import receiver

from dashboard.orbit import generate_orbit_reply
from message.models import Message


# TODO SEND MESSAGE BEFORE PROCESSING REQUEST
@receiver(post_save, sender=Message)
def handle_orbit_message(sender, instance, created, **kwargs):
    if not created:
        return

    conversation = instance.conversation

    if not conversation.is_orbit_chat:
        return
    if not instance.sender or instance.sender is None:
        return
    if instance.message_type != "regular":
        return

    # Generate Orbit reply
    prompt = instance.content or ""
    if not prompt.strip():
        return

    reply_text = generate_orbit_reply(prompt)

    Message.objects.create(
        conversation=conversation,
        sender=None,
        content=reply_text,
        message_type="system"
    )
