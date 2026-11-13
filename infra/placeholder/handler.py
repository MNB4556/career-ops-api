"""Answers 503 until the first CI deploy replaces this package."""


def handler(event, context):
    return {
        "statusCode": 503,
        "headers": {"content-type": "application/json"},
        "body": '{"detail":"not deployed yet"}',
    }
