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