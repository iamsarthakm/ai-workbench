from fastapi import Request


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # AWS ALB (append): client IP is rightmost. GCP GLB uses [-2] if you move there.
        return forwarded_for.split(",")[-1].strip()
    if request.client:
        return request.client.host
    return "unknown"
