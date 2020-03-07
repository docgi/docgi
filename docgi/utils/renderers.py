from rest_framework.renderers import JSONRenderer
from rest_framework import status

NOT_OKE_STATUS = [
    status.HTTP_400_BAD_REQUEST,
    status.HTTP_401_UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN,
    status.HTTP_500_INTERNAL_SERVER_ERROR
]


class DocgiJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response")
        status_code = response.status_code
        oke = True

        if status_code in NOT_OKE_STATUS:
            oke = False

        custom_data = dict(
            oke=oke,
            status=status_code,
            data=data
        )
        return super().render(data=custom_data,
                              accepted_media_type=accepted_media_type,
                              renderer_context=renderer_context)
