from unittest.mock import AsyncMock, Mock

import pytest

from dotenv import load_dotenv
from fastapi import HTTPException

from src.github.schemas import (
    GithubTreeResponse,
    GithubRepositoryResponse,
    GithubTreeElement,
)
from src.schemas import TextFile

load_dotenv()
from src.service import CodeReviewAIService  # noqa E402


@pytest.fixture
def mock_github_client():
    """Fixture to mock the GitHub client used in the CodeReviewAIService."""
    mock_client = AsyncMock()

    mock_client.get_tree = AsyncMock()
    mock_client.get_content = AsyncMock()
    mock_client.get_repository = AsyncMock()

    return mock_client


@pytest.fixture
def mock_ai_client():
    mock_client = AsyncMock()
    mock_client.review_repository = AsyncMock()
    return mock_client


@pytest.fixture
def mock_element():
    """Fixture to provide a mock GithubTreeElement."""
    return GithubTreeElement(
        sha='abc123',
        path='example/path/to/file.txt',
        type='blob',
        size=1234,
    )


@pytest.fixture
def service(mock_github_client, mock_ai_client):
    """Fixture to provide an instance of CodeReviewAIService."""
    code_review_service = CodeReviewAIService(github=mock_github_client)
    code_review_service.ai = mock_ai_client
    return code_review_service


@pytest.mark.asyncio
async def test_get_tree_success(service, mock_github_client):
    """Test that get_tree behaves as expected when the API call is successful."""
    # ARRANGE
    owner = 'test_owner'
    repo = 'test_repo'
    default_branch = 'main'
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.content = b'{"sha": "9fb037999f264ba9a7fc6274d15fa3ae2ab98312", "url": "https://api.github.com/repos/octocat/Hello-World", "truncated": false, "tree":[]}'  # Simulating a JSON response from GitHub
    mock_github_client.get_tree = AsyncMock(return_value=mock_response)

    # ACT
    result = await service.get_tree(owner, repo, default_branch)

    # ASSERT
    mock_github_client.get_tree.assert_awaited_once_with(owner, repo, default_branch)
    assert isinstance(result, GithubTreeResponse)
    assert result.tree == []


@pytest.mark.asyncio
async def test_get_tree_failure(service, mock_github_client):
    """Test that get_tree raises an HTTPException when the API call fails."""
    # ARRANGE
    owner = 'test_owner'
    repo = 'test_repo'
    default_branch = 'main'
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.text = 'Internal Server Error'
    mock_github_client.get_tree = AsyncMock(return_value=mock_response)

    # ACT & ASSERT
    with pytest.raises(HTTPException) as exc_info:
        await service.get_tree(owner, repo, default_branch)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Internal Server Error'


@pytest.mark.asyncio
async def test_get_repository_success(service, mock_github_client):
    """Test that get_repository behaves as expected when the API call is successful."""
    # ARRANGE
    owner = 'test_owner'
    repo = 'test_repo'
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.content = b'{"id": 1, "name": "test_repo", "full_name": "octocat/Hello-World", "private": false, "size": 1, "language": "test", "topics": [], "default_branch": "main"}'  # Example response

    # Mock the behavior of the GitHub client's get_repository method
    mock_github_client.get_repository = AsyncMock(return_value=mock_response)

    # ACT
    result = await service.get_repository(owner, repo)

    # ASSERT
    mock_github_client.get_repository.assert_awaited_once_with(owner, repo)
    assert isinstance(result, GithubRepositoryResponse)
    assert result.id == 1  # Based on the mocked response
    assert result.name == 'test_repo'
    assert result.full_name == 'octocat/Hello-World'


@pytest.mark.asyncio
async def test_get_repository_failure(service, mock_github_client):
    """Test that get_repository raises an HTTPException when the API call fails."""
    # ARRANGE
    owner = 'test_owner'
    repo = 'test_repo'
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.text = 'Internal Server Error'
    mock_github_client.get_repository = AsyncMock(return_value=mock_response)

    # ACT & ASSERT
    with pytest.raises(HTTPException) as exc_info:
        await service.get_repository(owner, repo)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Internal Server Error'


@pytest.mark.asyncio
async def test_get_file_content_success(service, mock_github_client, mock_element):
    """Test that get_file_content behaves as expected when the API call is successful."""
    # ARRANGE
    owner = 'test_owner'
    repo = 'test_repo'

    # Mock response for get_content
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.content = b'{"content": "aGVsbG8gd29ybGQ="}'
    mock_response.json = Mock(return_value={'content': 'aGVsbG8gd29ybGQ='})
    mock_github_client.get_content = AsyncMock(return_value=mock_response)

    # ACT
    result = await service.get_file_content(owner, repo, mock_element)

    # ASSERT
    mock_github_client.get_content.assert_awaited_once_with(
        owner, repo, mock_element.sha
    )
    assert isinstance(result, TextFile)
    assert result.path == mock_element.path
    assert result.content == 'hello world'  # Decoded content from the base64 string


@pytest.mark.asyncio
async def test_get_file_content_failure(service, mock_github_client, mock_element):
    """Test that get_file_content raises an HTTPException when the API call fails."""
    # ARRANGE
    owner = 'test_owner'
    repo = 'test_repo'

    # Mock response for get_content
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.text = 'Internal Server Error'

    mock_github_client.get_content = AsyncMock(return_value=mock_response)

    # ACT & ASSERT
    with pytest.raises(HTTPException) as exc_info:
        await service.get_file_content(owner, repo, mock_element)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Internal Server Error'
