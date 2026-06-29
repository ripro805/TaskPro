from django.db.models.signals import post_save, pre_save,post_delete,m2m_changed
from django.dispatch import receiver 
from django.core.mail import send_mail
from tasks.models import Task
#signals

@receiver(m2m_changed, sender=Task.assigned_to.through)
def notify_employees_on_tasks_creation(sender, instance, action, **kwargs):
    if action == 'post_add':
        users = instance.assigned_to.all()
        for user in users:
            # Get user's full name or username
            user_name = user.get_full_name() if user.get_full_name() else user.username
            print(f"Notification: Task '{instance.title}' has been assigned to {user_name} ({user.email})")

        # Send email only if users have email addresses
        recipient_emails = [user.email for user in users if user.email]

        if recipient_emails:
            send_mail(
                subject=f"New Task Assigned: {instance.title}",
                message=f"You have been assigned a new task: {instance.title}\nDescription: {instance.description}\nDue Date: {instance.due_date}",
                from_email="rifatrizviofficial001@gmail.com",
                recipient_list=recipient_emails,
                fail_silently=True,
            )
        
        
@receiver(post_delete, sender=Task)
def notify_task_deletion(sender, instance, **kwargs):
    detail = getattr(instance, 'detail', None)
    if detail:
        print(f"TaskDetail for '{instance.title}' also deleted.")
    print(f"Task Deleted: {instance.title}")
