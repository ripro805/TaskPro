from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


@receiver(post_save, sender=User)
def activation_email(sender, instance, created, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{uid}/{token}/"
        
        subject = "Activate Your TaskPro Account"
        html_content = render_to_string('accounts/activation_email.html', {
            'activation_link': activation_url,
            'year': 2026,
        })
        text_content = strip_tags(html_content)
        
        recipient_list = [instance.email]
        
        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=recipient_list,
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
        except Exception as e:
            print(f"Failed to send activation email to {instance.email}: {e}")
            
            

@receiver(post_save, sender=User)
def assign_role(sender, instance, created, **kwargs):
    if created:
        user_group, created = Group.objects.get_or_create(name='User') 
        instance.groups.add(user_group)
        instance.save() 

# UserProfile model removed; profile fields are on the custom user model itself.