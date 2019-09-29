from rest_framework import serializers


class GetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CheckCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
