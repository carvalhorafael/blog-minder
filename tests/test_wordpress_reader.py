import requests
from src.my_crewai_project.tools.wordpress_reader import fetch_wordpress_posts

def test_fetch_wordpress_posts(monkeypatch):
    # Sample response data for testing
    sample_posts = [
        {
            "title": {"rendered": "Post 1"},
            "content": {"rendered": "Content of post 1"}
        },
        {
            "title": {"rendered": "Post 2"},
            "content": {"rendered": "Content of post 2"}
        }
    ]
    
    class MockResponse:
        @staticmethod
        def json():
            return sample_posts
        
        @property
        def status_code(self):
            return 200

    # Mock the requests.get method
    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    # Call the function with a sample URL
    url = "http://example.com"
    result = fetch_wordpress_posts(url)

    # Expected output
    expected_output = "Post 1\nContent of post 1\n\nPost 2\nContent of post 2"

    # Assert the result
    assert result == expected_output
