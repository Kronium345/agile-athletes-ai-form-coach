from fastapi import FastAPI, testclient

# Re-export for test discovery
__all__ = ["FastAPI", "testclient"]
