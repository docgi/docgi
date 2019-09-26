from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from . import models


class CheckWorkspaceView(APIView):
    permission_classes = [
        AllowAny
    ]

    def post(self, request, *args, **kwargs):
        """
        Check workspace exists or not with `name`
        """
        workspace_name = request.data.get("name", None)
        if workspace_name is None:
            return Response(
                data=dict(error="Invalid payload."),
                status=status.HTTP_400_BAD_REQUEST
            )

        is_exists = models.Workspace.objects.filter(
            name__iexact=workspace_name
        ).exists()
        return Response(
            data=dict(exists=is_exists),
            status=status.HTTP_200_OK
        )
