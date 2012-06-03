from django import forms

from .models import Pin


class PinForm(forms.ModelForm):
    url = forms.CharField(label='URL', required=False)
    file  = forms.FileField(label='File', required=False)

    def __init__(self, *args, **kw):
        super(forms.ModelForm, self).__init__(*args, **kw)
        
        # Specify the display order
        self.fields.keyOrder = [
            'url',
            'file',
            'description']

    def clean(self):
        cleaned_data = self.cleaned_data
        url_data = cleaned_data.get('url')
        file_data = cleaned_data.get('file')

        # Check URL or file was submitted, and clean or upload
        if url_data is not None and len(url_data) > 0:
            cleaned_data['url'] = self.scrub_url(url_data)
        elif file_data is not None:
            cleaned_data['url'] = self.upload_file(file_data)
        else:
            raise forms.ValidationError("You need to supply either a URL or File") 

        return cleaned_data

    def upload_file(self, file_data):
        file_name = '/tmp/pinry-test.jpg'
        destination = open(file_name, 'wb+')
        for chunk in file_data.chunks():
            destination.write(chunk)
        destination.close()

        return 'file://' + file_name


    def scrub_url(self, data):

        # Test file type
        image_file_types = ['png', 'gif', 'jpeg', 'jpg']
        file_type = data.split('.')[-1]
        if file_type.lower() not in image_file_types:
            raise forms.ValidationError("Requested URL is not an image file. "
                                        "Only images are currently supported.")

        # Check if pin already exists
        try:
            Pin.objects.get(url=data)
            raise forms.ValidationError("URL has already been pinned!")
        except Pin.DoesNotExist:
            protocol = data.split(':')[0]
            if protocol == 'http':
                opp_data = data.replace('http://', 'https://')
            elif protocol == 'https':
                opp_data = data.replace('https://', 'http://')
            else:
                raise forms.ValidationError("Currently only support HTTP and "
                                            "HTTPS protocols, please be sure "
                                            "you include this in the URL.")

            try:
                Pin.objects.get(url=opp_data)
                raise forms.ValidationError("URL has already been pinned!")
            except Pin.DoesNotExist:
                return data

    class Meta:
        model = Pin
        exclude = ['image']
