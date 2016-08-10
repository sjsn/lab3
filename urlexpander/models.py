from django.db import models
from django.utils import timezone

class URL(models.Model):
	url = models.URLField(max_length = 250)
	date = models.DateTimeField(default = timezone.now)
	status = models.CharField(max_length = 100, default = '200')
	final_url = models.CharField(max_length = 250, null = url)
	title = models.CharField(max_length = 250, null = True)
	wayback = models.CharField(max_length = 250, null = url)
	wayback_date = models.CharField(max_length = 30, null = True)

	def __str__(self):
		return self.url
