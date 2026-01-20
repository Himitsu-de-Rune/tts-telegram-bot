"""TextMessage value object with validation."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TextMessage:
    
    MAX_LENGTH = 2000
    MIN_LENGTH = 1
    
    content: str
    
    def __post_init__(self):
        """Validate text message."""
        if not isinstance(self.content, str):
            raise ValueError("Content must be a string")
        
        if len(self.content.strip()) < self.MIN_LENGTH:
            raise ValueError("Text cannot be empty")
        
        if len(self.content) > self.MAX_LENGTH:
            raise ValueError(
                f"Text exceeds maximum length of {self.MAX_LENGTH} characters. "
                f"Current length: {len(self.content)}"
            )
    
    @property
    def length(self) -> int:
        return len(self.content)
    
    @property
    def is_empty(self) -> bool:
        return len(self.content.strip()) == 0
