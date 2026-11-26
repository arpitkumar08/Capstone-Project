from rest_framework import serializers


class BidSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    reference = serializers.CharField(max_length=180, trim_whitespace=True)
    title = serializers.CharField(max_length=180, trim_whitespace=True)
    department = serializers.CharField(max_length=180, trim_whitespace=True)
    deadline = serializers.DateField()
    status = serializers.CharField(read_only=True)
    vendors = serializers.IntegerField(read_only=True)
    updated = serializers.CharField(read_only=True)
    progress = serializers.IntegerField(read_only=True)
    documents = serializers.ListField(read_only=True)


class ReviewSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    decision = serializers.ChoiceField(choices=["Compliant", "Non-compliant", "Request clarification"])
    note = serializers.CharField(max_length=4000, trim_whitespace=True, allow_blank=False)
    reviewer = serializers.CharField(read_only=True)
    createdAt = serializers.DateTimeField(read_only=True)


class DocumentSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    size = serializers.IntegerField(min_value=1)
    uploadedAt = serializers.DateTimeField()
