from rest_framework import serializers
from urlexpander.models import URL

class URLSerializer(serializers.ModelSerializer):
	class Meta:
		model = URL
		fields = "__all__"