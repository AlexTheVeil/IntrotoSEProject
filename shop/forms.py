from django import forms

class PayoutRequestForm(forms.Form):
    period_start = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    period_end = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned = super().clean()
        s, e = cleaned.get("period_start"), cleaned.get("period_end")
        if s and e and s > e:
            raise forms.ValidationError("Start date must be before end date.")
        return cleaned