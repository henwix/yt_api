from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class EmailClient:
    def build_smtp_email(
        self,
        to: list[str],
        context: dict,
        subject: str,
        template: str,
    ) -> EmailMultiAlternatives:
        html_content = render_to_string(
            template_name=template,
            context=context,
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            to=to,
        )
        msg.attach_alternative(html_content, 'text/html')

        return msg

    def send_email(self, msg: EmailMultiAlternatives) -> None:
        msg.send()
