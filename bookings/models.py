from datetime import datetime, timedelta
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from hashlib import md5

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from nptime import nptime

from config import base_dir
from pods.models import Pod
from utils import time_str, date_str

EXPIRE_MINUTES = 30
DOMAIN = "http://ala.hipisi.org.pl:8551"


class Booking(models.Model):
    pod = models.ForeignKey(Pod, on_delete=models.CASCADE)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    email = models.EmailField()
    token = models.TextField()
    expired = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.token = self.token or self.get_token()
            self.expired = self.expired or self.date_start + timedelta(minutes=EXPIRE_MINUTES)
            self._send_email_verification()
        super().save(*args, **kwargs)

    def get_token(self):
        __hash_data = [
            settings.SECRET_KEY,
            self.email,
            self.pod,
            self.date_start,
            self.date_end
        ]
        __hash_str = ":".join(map(str, __hash_data))
        return md5(__hash_str.encode('utf-8')).hexdigest()

    @classmethod
    def get_slot(cls, calendar_date, time: nptime, duration, pod, email):
        calendar_date = datetime(day=calendar_date.day, month=calendar_date.month, year=calendar_date.year)
        date_start = calendar_date + time.to_timedelta()
        date_end = date_start + duration
        return cls(pod=pod, date_start=date_start, date_end=date_end, email=email)

    @classmethod
    def get_qs(cls, qs=None):
        qs = qs or cls.objects
        return qs.filter(expired__gt=datetime.now())

    @classmethod
    def bookings(cls, pod, date_start, date_end):
        return cls.get_qs() \
            .filter(pod=pod) \
            .filter(
            Q(date_start__lt=date_end, date_start__gte=date_start) |
            Q(date_end__lte=date_start, date_end__gt=date_end)
        )

    @property
    def conflicts(self):
        return self.bookings(self.pod, self.date_start, self.date_end)

    @property
    def count(self):
        return self.pod.amount - self.conflicts.count()

    @property
    def date_str(self):
        return date_str(self.date_start)

    @property
    def time_start_str(self):
        return time_str(self.date_start)

    @property
    def time_end_str(self):
        return time_str(self.date_end)

    @property
    def term_str(self):
        return f"{self.date_str} {self.time_start_str}-{self.time_end_str}"

    def __str__(self):
        return f"{self.pod}: {self.term_str}"

    def _send_email_verification(self):
        domain = DOMAIN
        subject = 'Welcome in Green Cloud Technology!'

        image_path = base_dir("static", "email", "welcome_email.png")

        img_cid = make_msgid()

        context = {
            'domain': domain,
            'booking': self,
            'img_cid': img_cid
        }
        body_html = render_to_string(
            'email_verification.html',
            context
        )
        body_text = render_to_string(
            'email_verification.txt',
            context
        )

        email = EmailMessage(subject, None, "info@marysia.app", [self.email])
        # email.content_subtype = "html"

        # https://stackoverflow.com/questions/1633109/creating-a-mime-email-template-with-images-to-send-with-python-django

        # Create a "related" message container that will hold the HTML
        # message and the image. These are "related" (not "alternative")
        # because they are different, unique parts of the HTML message,
        # not alternative (html vs. plain text) views of the same content.
        html_part = MIMEMultipart(_subtype='related')

        # Create the body with HTML. Note that the image, since it is inline, is
        # referenced with the URL cid:myimage... you should take care to make
        # "myimage" unique
        body = MIMEText(body_html, _subtype='html')
        html_part.attach(body)

        # Configure and send an EmailMessage
        # Note we are passing None for the body (the 2nd parameter). You could pass plain text
        # to create an alternative part for this message
        email.attach(html_part)  # Attach the raw MIMEBase descendant. This is a public method on EmailMessage

        with open(image_path, 'rb') as image:
            # Now create the MIME container for the image
            mime_image = MIMEImage(image.read())
            mime_image.add_header('Content-ID', f"<{img_cid}>")
            mime_image.add_header("Content-Disposition", "inline", filename="welcome_email.png")
            email.attach(mime_image)
            # html_part.attach(mime_image)
        email.send()
