import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["WAKATIME_API_TOKEN"] = "fake-token"
os.environ["API_KEY_READONLY"] = "test-api-key"
os.environ["ENABLE_EMAIL_INSIGHTS"] = "false"
