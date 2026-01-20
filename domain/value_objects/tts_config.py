"""TTS configuration value object."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TtsConfig:
    
    voice: str = "alena"
    language: str = "ru-RU"
    speed: float = 1.0
    emotion: Optional[str] = None
    
    def __post_init__(self):
        """Validate TTS config."""
        if not isinstance(self.speed, (int, float)) or self.speed <= 0:
            raise ValueError("Speed must be a positive number")
        
        if self.speed > 3.0:
            raise ValueError("Speed cannot exceed 3.0")
        
        if self.speed < 0.1:
            raise ValueError("Speed cannot be less than 0.1")
