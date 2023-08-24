from django import forms

class MonthYearForm(forms.Form):
    month_year = forms.DateField(input_formats=['%Y-%m'])
