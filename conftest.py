import pytest
from app import app

@pytest.fixture
def app():
    app = app()
    return app

