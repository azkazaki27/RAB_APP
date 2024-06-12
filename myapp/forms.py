from django import forms
from .models import Pekerjaan, SubPekerjaan, RAB
from django.contrib.auth.models import User

class SubPekerjaanForm(forms.ModelForm):
    class Meta:
        model = SubPekerjaan
        fields = ['nama', 'kuantiti', 'satuan', 'harga_satuan', 'referensi_harga']

class PekerjaanForm(forms.ModelForm):
    class Meta:
        model = Pekerjaan
        fields = ['nama_pekerjaan', 'tipe_pekerjaan']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RABForm(forms.ModelForm):
    class Meta:
        model = RAB
        fields = ['nama_rab', 'tanggal']
        widgets = {
            'tanggal': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }