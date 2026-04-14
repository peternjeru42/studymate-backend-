from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import NotificationPreference, StudentProfile, StudyPreference

User = get_user_model()


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = (
            "institution",
            "academic_level",
            "current_semester",
            "target_gpa",
            "weekly_study_target_hours",
            "onboarding_completed",
        )


class StudyPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyPreference
        fields = (
            "preferred_study_time",
            "session_duration",
            "break_duration",
            "study_style",
            "max_sessions_per_day",
        )


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = (
            "deadline_reminders",
            "study_suggestions",
            "assessment_alerts",
            "daily_summary",
        )


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    semester = serializers.CharField(source="student_profile.current_semester", read_only=True)
    target_gpa = serializers.DecimalField(
        source="student_profile.target_gpa", max_digits=3, decimal_places=2, read_only=True
    )
    onboarding_completed = serializers.BooleanField(source="student_profile.onboarding_completed", read_only=True)
    study_preferences = StudyPreferenceSerializer(source="study_preference", read_only=True)
    profile = StudentProfileSerializer(source="student_profile", read_only=True)
    notification_preferences = NotificationPreferenceSerializer(source="notification_preference", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "first_name",
            "last_name",
            "email",
            "semester",
            "target_gpa",
            "onboarding_completed",
            "study_preferences",
            "profile",
            "notification_preferences",
            "created_at",
        )

    def get_name(self, obj):
        return obj.name


class RegisterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password], style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("email", "name", "password")

    def create(self, validated_data):
        name = validated_data.pop("name")
        first_name, _, last_name = name.partition(" ")
        user = User(email=validated_data["email"], first_name=first_name, last_name=last_name)
        user.set_password(validated_data["password"])
        user.save()
        return user


class StudyPreferencesUpdateSerializer(serializers.Serializer):
    study_preferences = StudyPreferenceSerializer(required=False)
    notification_preferences = NotificationPreferenceSerializer(required=False)

    def update(self, instance, validated_data):
        study_data = validated_data.get("study_preferences", {})
        notification_data = validated_data.get("notification_preferences", {})
        for field, value in study_data.items():
            setattr(instance.study_preference, field, value)
        for field, value in notification_data.items():
            setattr(instance.notification_preference, field, value)
        instance.study_preference.save()
        instance.notification_preference.save()
        return instance


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    profile = StudentProfileSerializer(required=False)

    def update(self, instance, validated_data):
        profile_data = validated_data.get("profile", {})
        for field in ("first_name", "last_name"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        for field, value in profile_data.items():
            setattr(instance.student_profile, field, value)
        instance.student_profile.save()
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["name"] = user.name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password], style={"input_type": "password"})

    def validate(self, attrs):
        try:
            user_id = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError("Invalid reset link.")
        if not PasswordResetTokenGenerator().check_token(user, attrs["token"]):
            raise serializers.ValidationError("Invalid or expired reset token.")
        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetPayloadSerializer(serializers.Serializer):
    uid = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    class Meta:
        fields = ("uid", "token")

    def get_uid(self, obj):
        return urlsafe_base64_encode(force_bytes(obj.pk))

    def get_token(self, obj):
        return PasswordResetTokenGenerator().make_token(obj)
