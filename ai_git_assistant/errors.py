class AIGitAssistantError(Exception):
    """Base exception for expected user-facing failures."""


class GitContextError(AIGitAssistantError):
    """Raised when Git context cannot be collected."""


class ProviderError(AIGitAssistantError):
    """Raised when the AI API request or response fails."""


class ValidationError(AIGitAssistantError):
    """Raised when generated text does not satisfy the output contract."""
