import sys
from typing import Any

class PayloadValidator:
    """
    Utility class for payload validation.
    """
    
    @staticmethod
    def validate_payload_size(payload: Any, max_size_mb: float = 1.0) -> bool:
        """
        Validate that payload size doesn't exceed the specified limit.
        
        Args:
            payload (Any): Payload to validate
            max_size_mb (float): Maximum size in megabytes
            
        Returns:
            bool: True if payload is within size limit
            
        Raises:
            ValueError: If payload exceeds size limit
        """
        payload_size = sys.getsizeof(payload)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if payload_size > max_size_bytes:
            raise ValueError(f"Payload size ({payload_size} bytes) exceeds maximum allowed size ({max_size_bytes} bytes)")
        
        return True