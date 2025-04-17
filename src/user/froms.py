from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from user.models import User

class UserForm(UserChangeForm):
   class Meta:
      model = User
      fields = "__all__"


class UserCustomCreationForm(UserCreationForm):
   class Meta:
      model = User
      fields = "__all__"