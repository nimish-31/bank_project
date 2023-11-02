from django import forms

class UploadStatementForm(forms.Form):
    statement_file = forms.FileField(label='Statement File', help_text='Upload your statement file')    
