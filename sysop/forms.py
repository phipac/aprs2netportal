from django import forms
from django.contrib.auth.models import User

from models import Server


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        # fields = '__all__'  # needed in future version of Django


class SysopServerForm(ServerForm):
    """Allows sysops to edit their server details. Some fields are readonly."""
    def __init__(self, *args, **kwargs):
        super(SysopServerForm, self).__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['server_id'].widget.attrs['disabled'] = 'disabled'
            self.fields['server_id'].required = False
            self.fields['hostname'].widget.attrs['disabled'] = 'disabled'
            self.fields['hostname'].required = False
            self.fields['domain'].widget.attrs['disabled'] = 'disabled'
            self.fields['domain'].required = False

        self.fields['authorized_sysops'].widget.attrs['size'] = "10"
        user_qs = User.objects.order_by('username')
        self.fields['authorized_sysops'].queryset = user_qs
        self.fields['owner'].queryset = user_qs

    def clean_server_id(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.server_id
        else:
            return self.cleaned_data['server_id']

    def clean_hostname(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.hostname
        else:
            return self.cleaned_data['hostname']

    def clean_domain(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.domain
        else:
            return self.cleaned_data['domain']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
