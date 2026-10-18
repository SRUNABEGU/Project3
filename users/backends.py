from django.contrib.auth.backends import ModelBackend


class NotBlockedBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and not user.is_blocked
