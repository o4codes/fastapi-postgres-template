"""Async mail sender using SMTP."""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.configs.settings import get_settings

settings = get_settings()


class AsyncEmailSender:
    """Async email sender using SMTP with template support."""

    def __init__(self):
        """Initialize email sender with settings."""
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name
        self.use_tls = settings.smtp_tls
        self.use_ssl = settings.smtp_ssl

        # Set up Jinja2 environment for email templates
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    @asynccontextmanager
    async def _create_smtp_connection(self):
        """
        Create async SMTP connection with proper encryption.

        Returns:
            SMTP connection
        """
        smtp = aiosmtplib.SMTP(
            hostname=self.host,
            port=self.port,
            use_tls=self.use_ssl,
        )

        try:
            await smtp.connect()
            if self.use_tls and not self.use_ssl:
                await smtp.starttls()
            await smtp.login(self.username, self.password)
            yield smtp
        finally:
            await smtp.quit()

    def _create_message(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        html_content: str,
        cc_emails: Optional[Union[str, List[str]]] = None,
        bcc_emails: Optional[Union[str, List[str]]] = None,
        reply_to: Optional[str] = None,
    ) -> MIMEMultipart:
        """
        Create email message with proper headers.

        Args:
            to_emails: Recipient email(s)
            subject: Email subject
            html_content: HTML content of the email
            cc_emails: CC recipient(s)
            bcc_emails: BCC recipient(s)
            reply_to: Reply-to email address

        Returns:
            Email message
        """
        if isinstance(to_emails, str):
            to_emails = [to_emails]
        if isinstance(cc_emails, str):
            cc_emails = [cc_emails]
        if isinstance(bcc_emails, str):
            bcc_emails = [bcc_emails]

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = ", ".join(to_emails)

        if cc_emails:
            message["Cc"] = ", ".join(cc_emails)
        if reply_to:
            message["Reply-To"] = reply_to

        # Create HTML part
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        return message

    def _get_all_recipients(
        self,
        to_emails: Union[str, List[str]],
        cc_emails: Optional[Union[str, List[str]]] = None,
        bcc_emails: Optional[Union[str, List[str]]] = None,
    ) -> List[str]:
        """Get all recipients including CC and BCC."""
        all_recipients = []
        if isinstance(to_emails, str):
            all_recipients.append(to_emails)
        else:
            all_recipients.extend(to_emails)
        if cc_emails:
            if isinstance(cc_emails, str):
                all_recipients.append(cc_emails)
            else:
                all_recipients.extend(cc_emails)
        if bcc_emails:
            if isinstance(bcc_emails, str):
                all_recipients.append(bcc_emails)
            else:
                all_recipients.extend(bcc_emails)
        return all_recipients

    async def send_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        template_name: str,
        template_data: Dict[str, Any],
        cc_emails: Optional[Union[str, List[str]]] = None,
        bcc_emails: Optional[Union[str, List[str]]] = None,
        reply_to: Optional[str] = None,
    ) -> None:
        """
        Send an email using a template asynchronously.

        Args:
            to_emails: Recipient email(s)
            subject: Email subject
            template_name: Name of the template file (e.g. 'welcome.html')
            template_data: Data to pass to the template
            cc_emails: CC recipient(s)
            bcc_emails: BCC recipient(s)
            reply_to: Reply-to email address

        Raises:
            FileNotFoundError: If template file doesn't exist
            jinja2.exceptions.TemplateError: If template rendering fails
            aiosmtplib.errors.SMTPException: If email sending fails
        """
        # Render template
        template = self.env.get_template(template_name)
        html_content = template.render(**template_data)

        # Create message
        message = self._create_message(
            to_emails=to_emails,
            subject=subject,
            html_content=html_content,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
            reply_to=reply_to,
        )

        # Get all recipients
        # all_recipients = self._get_all_recipients(to_emails, cc_emails, bcc_emails)

        # Send email
        async with self._create_smtp_connection() as smtp:
            await smtp.send_message(message)

    async def send_raw_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        html_content: str,
        cc_emails: Optional[Union[str, List[str]]] = None,
        bcc_emails: Optional[Union[str, List[str]]] = None,
        reply_to: Optional[str] = None,
    ) -> None:
        """
        Send a raw HTML email without using a template asynchronously.

        Args:
            to_emails: Recipient email(s)
            subject: Email subject
            html_content: HTML content of the email
            cc_emails: CC recipient(s)
            bcc_emails: BCC recipient(s)
            reply_to: Reply-to email address

        Raises:
            aiosmtplib.errors.SMTPException: If email sending fails
        """
        # Create message
        message = self._create_message(
            to_emails=to_emails,
            subject=subject,
            html_content=html_content,
            cc_emails=cc_emails,
            bcc_emails=bcc_emails,
            reply_to=reply_to,
        )

        # Get all recipients
        # all_recipients = self._get_all_recipients(to_emails, cc_emails, bcc_emails)

        # Send email
        async with self._create_smtp_connection() as smtp:
            await smtp.send_message(message)
