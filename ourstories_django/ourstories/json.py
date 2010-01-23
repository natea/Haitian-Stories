""" json.py
Mechanisms to easily format any django response in JavaScript Object Notation; inspired
by TurboGears's JSON capabilities
""" 

import sys
from django.utils.simplejson import dumps

from django.http import HttpResponse

class JsonResponse(HttpResponse):
    """ HttpReponse wrapper that formats the response as a JSON response
    """
    def __init__(self, content='', mimetype=None, status=None, content_type=None):
        HttpResponse.__init__(self, dumps(content), mimetype, status, content_type)
