# Built-in imports
from typing import Any, List, Dict
from datetime import datetime

# local imports
from app.utils.logger import get_logger

logger = get_logger(__name__)

class Transformer:
    """
    Transforms and cleans data.
    """
    def __init__(self):
        pass
    
    def transform(self, data: Any) -> List[Dict[str, Any]]:
        if not data:
            logger.warning("Warning: No data to transform.")
            return []
        clean_data = []
        for item in data:
            try:
                cleaned = {
                    "time_stamp": self.parse_datetime(item.get("timestamp")),
                    "cpu_percent": item.get("cpu_percent"),
                    "memory": item.get("memory"),
                    "disk": item.get("disk"),
                    "net_io": item.get("net_io")
                }
                
                if self.is_valid(cleaned):
                    clean_data.append(cleaned)
                else:
                    logger.warning("Warning: Item is not valid")
            except Exception as e:
                logger.exception(f"Error: transforming item: {item}, Error: {e}")
        return clean_data
    
    def parse_datetime(self, value: str) -> str:
        try:
            dt = datetime.fromisoformat(value)
            return dt.isoformat()
        except Exception as e:
            logger.warning(f"Warning: Failed to parse datetime from value: {value}")
        return datetime.utcnow().isoformat()
        
    def is_valid(self, item: Dict[str, Any]) -> bool:
        return bool(item['time_stamp'] and item['cpu_percent'] and item['memory'] and item['disk'] and item['net_io'])