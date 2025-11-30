from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Send a test email to the specified address using current email settings'

    def add_arguments(self, parser):
        parser.add_argument('to', help='Recipient email address')

    def handle(self, *args, **options):
        to = options['to']
        subject = 'Test email from IntrotoSEProject'
        message = 'This is a test email sent by the management command send_test_email.'
        from_email = None  # uses DEFAULT_FROM_EMAIL if set
        try:
            send_mail(subject, message, from_email, [to], fail_silently=False)
            self.stdout.write(self.style.SUCCESS(f'Successfully sent test email to {to}'))
        except Exception as e:
            raise CommandError(f'Failed to send email: {e}')
