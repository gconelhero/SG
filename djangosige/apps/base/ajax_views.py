from django.views.generic import View
from django.http import HttpResponse
from django.core import serializers

import json

from django.core.cache import cache

class setCache(View):
    def get(self, request, *args, **kwargs):
        cache_get = [{'menu_open_close': cache.get('menu_open_close')}]
        return HttpResponse(json.dumps(cache_get))

    def post(self, request, *args, **kwargs):
        try:
            set_cache = request.POST['menu_open_close']
            cache.set('menu_open_close', set_cache, 30)
        except Exception as erro:
            set_cache = False
            print("CACHE MENU NÃO SETADO > ", erro)

        
        return HttpResponse()
