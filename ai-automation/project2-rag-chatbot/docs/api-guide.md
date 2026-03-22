# API Integration Guide

Our REST API uses standard HTTP methods. All requests must include an API key in the Authorization header: Authorization: Bearer YOUR_API_KEY.

Rate limits are 100 requests per minute for free plans and 1000 requests per minute for paid plans. Exceeding the rate limit returns a 429 status code. Implement exponential backoff when you receive 429 responses.

File uploads are limited to 25MB per request. For larger files, use our multipart upload endpoint at /api/v2/uploads/multipart. Files over 100MB are not supported.

Common error codes: 400 Bad Request means invalid parameters. 401 Unauthorized means invalid or expired API key. 403 Forbidden means your plan does not include this feature. 500 Internal Server Error means something went wrong on our end, please retry.
