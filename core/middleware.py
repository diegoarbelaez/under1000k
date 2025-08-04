import os
import logging
from django.conf import settings
from django.http import Http404
from django.views.static import serve

# Configurar logger
logger = logging.getLogger(__name__)

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


class AuthLoggingMiddleware:
    """
    Middleware para logging detallado de autenticación
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log de la request
        logger.info(f"🔍 REQUEST: {request.method} {request.path}")
        logger.info(f"   User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        logger.info(f"   Content-Type: {request.META.get('CONTENT_TYPE', 'N/A')}")
        
        # Log de datos POST si es login
        if request.path == '/admin/login/' and request.method == 'POST':
            logger.info("🔐 LOGIN ATTEMPT:")
            logger.info(f"   Username: {request.POST.get('username', 'N/A')}")
            logger.info(f"   Password length: {len(request.POST.get('password', ''))}")
            logger.info(f"   CSRF Token: {request.POST.get('csrfmiddlewaretoken', 'N/A')[:20]}...")
        
        response = self.get_response(request)
        
        # Log de la response
        logger.info(f"📤 RESPONSE: {response.status_code}")
        if hasattr(response, 'content'):
            logger.info(f"   Content length: {len(response.content)}")
        
        # Log específico para login
        if request.path == '/admin/login/' and request.method == 'POST':
            if response.status_code == 302:
                logger.info("✅ LOGIN SUCCESS - Redirecting")
            elif response.status_code == 200:
                logger.info("❌ LOGIN FAILED - Still on login page")
                # Intentar extraer mensaje de error
                if hasattr(response, 'content'):
                    content = response.content.decode('utf-8')
                    if 'error' in content.lower():
                        logger.error("   Error message found in response")
        
        return response 