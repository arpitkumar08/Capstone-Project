from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    details = response.data
    if isinstance(details, dict):
        messages = []
        for field, errors in details.items():
            parts = errors if isinstance(errors, list) else [errors]
            messages.extend(f"{field}: {message}" if field != "non_field_errors" else str(message) for message in parts)
        message = "; ".join(str(item) for item in messages) or "Request validation failed."
    else:
        message = str(details)
    response.data = {"error": message, "details": details}
    return response
