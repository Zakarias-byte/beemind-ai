# BeeMind CORS Configuration
# Strategic CORS setup to avoid common issues with api.beemind.dev

from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app):
    """
    Strategic CORS configuration for BeeMind API
    Handles common CORS issues proactively
    """
    
    # Production domains
    production_origins = [
        "https://beemind.dev",
        "https://www.beemind.dev",
        "http://beemind.dev",  # Fallback for redirects
        "http://www.beemind.dev",  # Fallback for redirects
    ]
    
    # Development domains
    development_origins = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # Determine environment
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        allowed_origins = production_origins
    else:
        allowed_origins = production_origins + development_origins
    
    # Add CORS middleware with strategic configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=[
            "GET", 
            "POST", 
            "PUT", 
            "DELETE", 
            "OPTIONS", 
            "HEAD", 
            "PATCH"
        ],
        allow_headers=[
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRFToken",
            "X-API-Key",
            "Cache-Control",
            "Pragma",
            "Expires",
            "Last-Modified",
            "If-Modified-Since",
            "If-None-Match",
            "ETag",
            "User-Agent",
            "Referer",
            "Origin",
        ],
        expose_headers=[
            "Content-Length",
            "Content-Type", 
            "Cache-Control",
            "Expires",
            "Last-Modified",
            "ETag",
            "X-Total-Count",
            "X-Page-Count",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
        ],
        max_age=86400,  # 24 hours preflight cache
    )
    
    # Add custom CORS headers middleware for extra compatibility
    @app.middleware("http")
    async def add_cors_headers(request, call_next):
        response = await call_next(request)
        
        # Get origin from request
        origin = request.headers.get("origin")
        
        # Check if origin is allowed
        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        # Always add these for compatibility
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
        response.headers["Access-Control-Max-Age"] = "86400"
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response.headers["Access-Control-Allow-Headers"] = ", ".join([
                "Accept", "Accept-Language", "Content-Language", "Content-Type",
                "Authorization", "X-Requested-With", "X-CSRFToken", "X-API-Key",
                "Cache-Control", "Pragma", "Expires", "Last-Modified",
                "If-Modified-Since", "If-None-Match", "ETag", "User-Agent",
                "Referer", "Origin"
            ])
        
        return response
    
    return app

# Additional CORS debugging function
def log_cors_info(request):
    """Log CORS information for debugging"""
    origin = request.headers.get("origin", "No Origin")
    method = request.method
    headers = dict(request.headers)
    
    print(f"CORS Debug - Origin: {origin}, Method: {method}")
    print(f"Request Headers: {headers}")
    
    return {
        "origin": origin,
        "method": method, 
        "headers": headers
    }
