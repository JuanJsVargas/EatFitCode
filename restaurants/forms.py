from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        widget=forms.RadioSelect(attrs={'class': 'star-rating'}),
        label=''
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Share your experience...',
            'class': 'form-control'
        }),
        required=False,
        label='Your Review'
    )

    class Meta:
        model = Rating
        fields = ['rating', 'comment'] 