"""
Memory Provider ABC — Hermes-inspired pluggable memory
"""
from abc import ABC, abstractmethod

class MemoryProvider(ABC):
    """هر حافظه‌بک‌اند باید اینو پیاده کنه"""
    @abstractmethod
    def sync_turn(self, session_id: str, role: str, content: str): ...
    
    @abstractmethod
    def prefetch(self, query: str, limit: int = 5) -> str: ...
    
    @abstractmethod
    def get_durable(self) -> dict: ... # {"memory": str, "user": str, "soul": str}
    
    def shutdown(self): pass
