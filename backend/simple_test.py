#!/usr/bin/env python3
"""
Minimal test to see if Python functions work on Vercel
"""

def handler(request):
    """Minimal Vercel function handler"""
    return {
        'statusCode': 200,
        'body': '{"status": "ok", "message": "Python is working on Vercel"}'
    }

# Also export as 'app' for compatibility
class SimpleApp:
    def __call__(self, scope, receive, send):
        import json
        
        response_body = json.dumps({
            "status": "ok", 
            "message": "Simple Python app is working",
            "scope_type": scope.get("type", "unknown")
        }).encode()
        
        async def asgi():
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'application/json'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': response_body,
            })
        
        return asgi()

app = SimpleApp()