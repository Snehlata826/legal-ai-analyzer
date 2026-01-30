#!/usr/bin/env python3
try:
    import app.main
    print("Import successful: app.main")
except ImportError as e:
    print(f"Import failed: {e}")

try:
    from app.routers import upload
    print("Import successful: app.routers.upload")
except ImportError as e:
    print(f"Import failed: {e}")

try:
    from app.core import extract_text
    print("Import successful: app.core.extract_text")
except ImportError as e:
    print(f"Import failed: {e}")

try:
    from app.embeddings import embedder
    print("Import successful: app.embeddings.embedder")
except ImportError as e:
    print(f"Import failed: {e}")

try:
    from app.services import simplifier
    print("Import successful: app.services.simplifier")
except ImportError as e:
    print(f"Import failed: {e}")
