import json
from fastapi import Request, Response


# Сначала сделал декоратор и это работало.
# Но смущало добавление request в каждое представление и
# синтаксического сахара.

# def log_if_debug(func):
#     @wraps(func)
#     async def wrapper(*args, **kwargs):
#         request: Request = kwargs.get("request")
#         debug: bool = get_debug()
#         result = await func(*args, **kwargs)
#         if debug:
#             print(f"Request data:\n Method: {request.method}\n URL: {request.url}")
#             body = await request.body()
#             print(f"Request body: {body.decode('utf-8') if body else 'No body'}")
#             print("Response will be logged after route processing")
#             status = 200 if result else 503
#             print(f"Response status: {status}")
#             print(f"Response body: {result if result else 'No Content'}")
#             result = None
#         return result
#     return wrapper


async def debug_logging_middleware(request: Request, call_next) -> Response:
    debug = getattr(request.app.state, 'cli_args', None) and request.app.state.cli_args.debug
    if not debug:
        return await call_next(request)
    
    print("\n" + "="*50)
    print(f"{request.method} {request.url}")
    print("\nHeaders:")
    for k, v in request.headers.items():
        print(f"{k}: {v}")

    body = await request.body()
    print("\nRequest body:")
    print(json.dumps(json.loads(body), indent=2) if body else 'No body')
    response = await call_next(request)
    print("\n" + "="*50)
    print(f"Status: {response.status_code}")
    print("\nResponse headers:")
    for k, v in response.headers.items():
        print(f"{k}: {v}")

    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)
    response_body = b''.join(chunks)

    print(f"\nResponse body: {response_body.decode('utf-8', errors='replace')[:500]}")

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )
