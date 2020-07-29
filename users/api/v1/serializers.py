from django.contrib.auth import get_user_model

from rest_framework import serializers

from wallet.models import Wallet, Balance

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, min_length=8)

	def create(self, validated_data):
		password = validated_data.pop("password")
		user = UserModel.objects.create(
			**validated_data
		)
		user.set_password(password)
		user.save()
		wallet = Wallet.objects.create(user=user)
		Balance.objects.create(
			wallet=wallet, currency=wallet.preferred_currency
		)
		return user

	class Meta:
		model = UserModel
		fields = ("id", "username", "password", "email", "first_name", "last_name")


class ProfilePicSerializer(serializers.ModelSerializer):
	profile_pic = serializers.ImageField(required=True)

	def create(self, validated_data):
		user = self.context.get('user')
		file = self.validated_data.get('profile_pic')
		if user.profile_pic:
			user.profile_pic.delete()
		file_extension = file.name.split(".")[-1]
		file.name = "{}.{}".format(user.username, file_extension)
		user.profile_pic = file
		user.save()
		return file

	class Meta:
		model = get_user_model()
		fields = ("profile_pic",)
