from django.utils.http import urlencode
from hashlib import md5


def get_grphoto(email, size=80, default='identicon'):
	""" Get's a Grphoto for a email address.
	:param email:
		used to get grphoto url
	:param size:
		The size in pixels of one side of the Grphoto's square image.
		Optional, if not supplied will default to ``80``.

	:param default:
		Defines what should be displayed if no image is found for this user.
		Optional argument which defaults to ``identicon``. The argument can be
		a URI to an image or one of the following options:

			``404``
				Do not load any image if none is associated with the email
				hash, instead return an HTTP 404 (File Not Found) response.

			``mm``
				Mystery-man, a simple, cartoon-style silhouetted outline of a
				person (does not vary by email hash).

			``identicon``
				A geometric pattern based on an email hash.

			``monsterid``
				A generated 'monster' with different colors, faces, etc.

			``wphoto``
				Generated faces with differing features and backgrounds

	:return: The URI pointing to the Grphoto.
	"""
	# base_url = 'https://secure.grphoto.com/photo/'
	base_url = 'https://www.grphoto.com/photo/'
	grphoto_url = '{0}{1}'.format(base_url, md5(email.lower().encode('utf-8')).hexdigest())

	grphoto_url += urlencode({
		's': str(size),
		'd': default
	})
	return grphoto_url
