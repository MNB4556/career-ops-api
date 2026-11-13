"""AWS Lambda entry point.

Lambda calls ``handler(event, context)``. Mangum translates the API Gateway
payload into an ASGI request, so the same FastAPI app runs unchanged in both
places.
"""

from __future__ import annotations

from mangum import Mangum

from career_ops_api.main import app

handler = Mangum(app, lifespan="auto")
