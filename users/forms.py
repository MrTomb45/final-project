import re
from django import forms
from django.contrib.auth import authenticate
from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Неверный email или пароль")
        return cleaned_data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        widgets = {
            "avatar": forms.FileInput(
                attrs={
                    "class": "form-control-file",
                    "id": "id_avatar",
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return phone

        if not re.match(r"^(8|\+7)\d{10}$", phone):
            raise forms.ValidationError(
                "Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
            )

        if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Этот номер телефона уже используется.")

        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and not url.startswith("https://github.com/"):
            raise forms.ValidationError(
                "Ссылка должна вести на GitHub (https://github.com/...)"
            )
        return url
