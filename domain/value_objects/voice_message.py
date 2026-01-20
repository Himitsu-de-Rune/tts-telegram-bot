"""VoiceMessage value object representing audio metadata."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VoiceMessage:
    
    audio_data: bytes
    format: str = "ogg"
    duration: Optional[int] = None  # Duration in seconds
    size: Optional[int] = None  # Size in bytes
    
    def __post_init__(self):
        """Validate voice message."""
        if not isinstance(self.audio_data, bytes):
            raise ValueError("Audio data must be bytes")
        
        if len(self.audio_data) == 0:
            raise ValueError("Audio data cannot be empty")
        
        if self.size is None:
            object.__setattr__(self, 'size', len(self.audio_data))
        
        if self.format.lower() not in ['ogg', 'opus', 'mp3', 'wav']:
            raise ValueError(f"Unsupported audio format: {self.format}")
