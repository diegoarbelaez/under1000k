import os
from django.conf import settings
from django.http import Http404
from django.views.static import serve

class StaticFilesMiddleware:
    """
    Middleware para servir archivos estáticos en producción
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar si la URL es para archivos estáticos
        if request.path.startswith('/static/'):
            # Remover el prefijo /static/ para obtener la ruta del archivo
            file_path = request.path[8:]  # Remover '/static/'
            
            # Construir la ruta completa al archivo
            static_file_path = os.path.join(settings.STATIC_ROOT, file_path)
            
            # Verificar si el archivo existe
            if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
                return serve(request, file_path, document_root=settings.STATIC_ROOT)
            else:
                raise Http404("Static file not found")
        
        response = self.get_response(request)
        return response 