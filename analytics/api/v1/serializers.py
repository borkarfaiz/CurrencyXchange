from rest_framework import serializers

from wallet.models import Order


class DateSerializer(serializers.ModelSerializer):
	start_date = serializers.DateField()

	class Meta:
		model = Order
		fields = ["start_date"]
