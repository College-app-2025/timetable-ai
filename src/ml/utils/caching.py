"""
Caching utilities for the SIH Timetable Optimization System.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os
from pathlib import Path

from src.utils.logger_config import get_logger

logger = get_logger("ml_caching")


class CacheManager:
    """Manages caching for optimization results and intermediate data."""
    
    def __init__(self, cache_dir: str = "cache/ml"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
        
        # Cache configuration
        self.max_cache_size = 100  # Maximum number of cached items
        self.cache_ttl = timedelta(hours=24)  # Time to live for cache items
        
        self.logger.info(f"Cache manager initialized with directory: {self.cache_dir}")
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate a unique cache key for the given data."""
        try:
            # Create a deterministic string representation of the data
            data_str = json.dumps(data, sort_keys=True, default=str)
            
            # Generate MD5 hash
            hash_object = hashlib.md5(data_str.encode())
            cache_key = hash_object.hexdigest()
            
            return cache_key
            
        except Exception as e:
            self.logger.error(f"Error generating cache key: {str(e)}")
            return f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.json"
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache file is valid (exists and not expired)."""
        if not cache_file.exists():
            return False
        
        # Check if file is within TTL
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        return datetime.now() - file_time < self.cache_ttl
    
    def get(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached result for the given data."""
        try:
            cache_key = self._generate_cache_key(data)
            cache_file = self._get_cache_file_path(cache_key)
            
            if not self._is_cache_valid(cache_file):
                self.logger.debug(f"Cache miss or expired for key: {cache_key}")
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            self.logger.debug(f"Cache hit for key: {cache_key}")
            return cached_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving from cache: {str(e)}")
            return None
    
    def set(self, data: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Cache the result for the given data."""
        try:
            cache_key = self._generate_cache_key(data)
            cache_file = self._get_cache_file_path(cache_key)
            
            # Add metadata to cached result
            cached_result = {
                'cached_at': datetime.now().isoformat(),
                'cache_key': cache_key,
                'result': result
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached_result, f, indent=2, default=str)
            
            self.logger.debug(f"Result cached with key: {cache_key}")
            
            # Clean up old cache files if needed
            self._cleanup_cache()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error caching result: {str(e)}")
            return False
    
    def _cleanup_cache(self):
        """Clean up old cache files to maintain cache size limit."""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            
            if len(cache_files) <= self.max_cache_size:
                return
            
            # Sort by modification time (oldest first)
            cache_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Remove oldest files
            files_to_remove = cache_files[:-self.max_cache_size]
            for cache_file in files_to_remove:
                cache_file.unlink()
                self.logger.debug(f"Removed old cache file: {cache_file.name}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {str(e)}")
    
    def clear(self) -> bool:
        """Clear all cache files."""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            
            for cache_file in cache_files:
                cache_file.unlink()
            
            self.logger.info(f"Cleared {len(cache_files)} cache files")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            
            total_files = len(cache_files)
            valid_files = sum(1 for f in cache_files if self._is_cache_valid(f))
            expired_files = total_files - valid_files
            
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                'total_files': total_files,
                'valid_files': valid_files,
                'expired_files': expired_files,
                'total_size_bytes': total_size,
                'cache_directory': str(self.cache_dir),
                'max_cache_size': self.max_cache_size,
                'cache_ttl_hours': self.cache_ttl.total_seconds() / 3600
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {str(e)}")
            return {'error': str(e)}
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache files matching a pattern."""
        try:
            cache_files = list(self.cache_dir.glob(f"*{pattern}*.json"))
            
            invalidated_count = 0
            for cache_file in cache_files:
                cache_file.unlink()
                invalidated_count += 1
            
            self.logger.info(f"Invalidated {invalidated_count} cache files matching pattern: {pattern}")
            return invalidated_count
            
        except Exception as e:
            self.logger.error(f"Error invalidating cache pattern: {str(e)}")
            return 0


class OptimizationCache:
    """Specialized cache for optimization operations."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.logger = logger
    
    def get_optimization_result(self, 
                              students: List[Any], 
                              courses: List[Any], 
                              faculty: List[Any], 
                              rooms: List[Any],
                              config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached optimization result."""
        try:
            # Create cache key from input data
            cache_data = {
                'students_count': len(students),
                'courses_count': len(courses),
                'faculty_count': len(faculty),
                'rooms_count': len(rooms),
                'config': config,
                'data_hash': self._get_data_hash(students, courses, faculty, rooms)
            }
            
            return self.cache_manager.get(cache_data)
            
        except Exception as e:
            self.logger.error(f"Error getting optimization result from cache: {str(e)}")
            return None
    
    def set_optimization_result(self, 
                              students: List[Any], 
                              courses: List[Any], 
                              faculty: List[Any], 
                              rooms: List[Any],
                              config: Dict[str, Any],
                              result: Dict[str, Any]) -> bool:
        """Cache optimization result."""
        try:
            # Create cache key from input data
            cache_data = {
                'students_count': len(students),
                'courses_count': len(courses),
                'faculty_count': len(faculty),
                'rooms_count': len(rooms),
                'config': config,
                'data_hash': self._get_data_hash(students, courses, faculty, rooms)
            }
            
            return self.cache_manager.set(cache_data, result)
            
        except Exception as e:
            self.logger.error(f"Error caching optimization result: {str(e)}")
            return False
    
    def _get_data_hash(self, 
                      students: List[Any], 
                      courses: List[Any], 
                      faculty: List[Any], 
                      rooms: List[Any]) -> str:
        """Generate hash for data to detect changes."""
        try:
            # Create a simple hash from data IDs and counts
            data_str = f"{len(students)}_{len(courses)}_{len(faculty)}_{len(rooms)}"
            
            # Add some data identifiers if available
            if students:
                data_str += f"_{students[0].id if hasattr(students[0], 'id') else 'unknown'}"
            if courses:
                data_str += f"_{courses[0].id if hasattr(courses[0], 'id') else 'unknown'}"
            
            return hashlib.md5(data_str.encode()).hexdigest()[:8]
            
        except Exception as e:
            self.logger.error(f"Error generating data hash: {str(e)}")
            return "unknown"

