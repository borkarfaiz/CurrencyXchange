from django.http.response import FileResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from .serializers import UserSerializer, ProfilePicSerializer


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def sign_up(request):
	user_serializer = UserSerializer(data=request.data)
	if user_serializer.is_valid():
		user_serializer.save()
		return Response(
			status=HTTP_201_CREATED, data=user_serializer.data,
		)
	else:
		return Response(
			status=HTTP_400_BAD_REQUEST, data=user_serializer.errors
		)


class ProfilePic(APIView):
	parser_classes = (MultiPartParser, FormParser)

	def get(self, request):
		user = request.user
		profile_pic = user.profile_pic
		if not profile_pic:
			return FileResponse(status=HTTP_404_NOT_FOUND)
		profile_pic_file = profile_pic.file

		# send file
		response = FileResponse(profile_pic_file.open(), content_type='image/jpeg')
		response['Content-Length'] = profile_pic_file.size
		response['Content-Disposition'] = 'attachment; filename="%s"' % profile_pic_file.file.name

		return response

	def post(self, request):
		profile_pic_serializer = ProfilePicSerializer(data=request.data, context={'user': request.user})
		if profile_pic_serializer.is_valid():
			profile_pic_serializer.save()
			return Response(
				status=HTTP_201_CREATED, data={"message": "upload successful"}
			)
		else:
			return Response(
				status=HTTP_400_BAD_REQUEST, data=profile_pic_serializer.errors
			)
