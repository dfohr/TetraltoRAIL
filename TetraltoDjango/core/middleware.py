class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Don't cache admin or health check URLs
        if request.path.startswith('/admin/') or request.path == '/health/':
            return response

        # Add Cache-Control headers
        if request.method == 'GET':
            # Static files (CSS, JS, images)
            if any(request.path.endswith(ext) for ext in ['.css', '.js', '.avif', '.png', '.jpg', '.jpeg', '.ico']):
                response['Cache-Control'] = 'public, max-age=31536000, immutable'  # 1 year
            # HTML pages
            else:
                response['Cache-Control'] = 'public, max-age=3600'  # 1 hour

        return response

class SitemapMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Handle sitemap.xml specifically
        if request.path == '/sitemap.xml':
            # Remove any x-robots-tag header that might have been set
            if 'X-Robots-Tag' in response:
                del response['X-Robots-Tag']
            
            # Ensure proper caching for sitemap
            response['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
            
            # Add content type if not already set
            if 'Content-Type' not in response:
                response['Content-Type'] = 'application/xml'

        return response 