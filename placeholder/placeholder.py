from django.http import HttpResponse
from django.conf.urls import url
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django import forms
from django.conf.urls import url
from django.http import HttpResponse, HttpResponseBadRequest
from io import BytesIO
from PIL import Image, ImageDraw
from django.core.cache import cache
from django.views.decorators.http import etag

import hashlib
import sys
import os
 
DEBUG = os.environ.get('DEBUG','on') == 'on'
SECRET_KEY = os.environ.get('SECRET_KEY','%jv-4#hoaqwig2gu!eg#^ozptd*a@88u(aasv7z!7xt^5(*i&k')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS','localhost').split(',')

settings.configure(
	DEBUG=DEBUG,
	SECRET_KEY = SECRET_KEY,
	ROOT_URLCONF =__name__,
	ALLOWED_HOSTS = ALLOWED_HOSTS,
	MIDDLEWARE_CLASSES = (
		'django.middleware.common.CommonMiddleware',
		'django.middleware.csrf.CsrfViewMiddleware',
		'django.middleware.clickjacking.XFrameOptionsMiddleware',
	),
)
class ImageForm(forms.Form):
	"""Formularios para validar o placeholder de imagem solicitado."""
	height = forms.IntegerField(min_value=1, max_value=2000)
	width=forms.IntegerField(min_value=1, max_value=2000)
	
	def generate(self, image_format='PNG'):
		"""gera uma imagem do tipo especificado e a retorna na forma de bytes puros"""
		height = self.cleaned_data['height']
		width = self.cleaned_data['width']
		key = '{}.{}.{}'.format(width, height, image_format)
		content = cache.get(key)
		if content is None:
			image = Image.new('RGB',(width, height))
			draw = ImageDraw.Draw(image)
			text = '{} x {}'.format(width,height)
			textwidth, textheight = draw.textsize(text)
			if textwidth < width and textheight < height:
				texttop = (height - textheight)//2
				textleft = (width - textwidth)//2
				draw.text(textleft, texttop, text, fill=(255,255,255))
			content = ByteIO()
			image.save(content, image_format)
			content.seek(0)
			cache.set(key, content, 60*60)
		return content

def generate_etag(request, width, height):
	content = 'Placeholder: {0} x {1}'.format(width, height)
	return hshlib.sha1(content.encode('utf-8')).hexdigest()


#new view
@etag(generate_etag)
def placeholder(request, width, height):
	form = ImageForm({'height': height, 'width': width})
	if form.is_valid():
		height = form.cleaned_data['height']
		width = form.cleaned_data['width']
		#TODO: Gera imagem do tamanho solicitado
		return HttpResponse("ok")
	else:
		return HttpResponseBadRequest('Invalid Image Request')

#original view
def index(request):
	return HttpResponse('HelloWord')

urlpatterns = (
	url(r'^image/(?P<width>[0-9]+)x(?P<height>[0-9]+)/$', placeholder, name='placeholder'),
	url(r'^$', index, name='homepage'),
)


application = get_wsgi_application()

if __name__=="__main__":
	from django.core.management import execute_from_command_line
	execute_from_command_line(sys.argv)
