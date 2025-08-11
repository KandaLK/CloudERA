"""
Circuit Breaker Pattern Implementation

Provides circuit breaker functionality for external services to prevent
cascading failures and improve system resilience under high load.
"""

import time
import threading
from typing import Dict, Any, Optional, Callable
from enum import Enum
from collections import defaultdict

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Circuit is open, rejecting calls
    HALF_OPEN = "half_open" # Testing if service is back

class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(self, 
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.timeout = timeout
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.lock = threading.Lock()
        
        # Statistics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.rejected_calls = 0
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        with self.lock:
            self.total_calls += 1
            
            # Check if circuit should be half-open
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    print(f"[CircuitBreaker:{self.name}] Entering HALF_OPEN state")
                else:
                    self.rejected_calls += 1
                    raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
            
            # Execute the function
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Check for timeout
                if execution_time > self.timeout:
                    raise TimeoutError(f"Function execution exceeded {self.timeout}s")
                
                # Success - reset failure count
                self._on_success()
                return result
                
            except Exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.successful_calls += 1
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            print(f"[CircuitBreaker:{self.name}] Recovered - returning to CLOSED state")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failed_calls += 1
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"[CircuitBreaker:{self.name}] OPENED - {self.failure_count} failures exceeded threshold")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        with self.lock:
            success_rate = (self.successful_calls / max(self.total_calls, 1)) * 100
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "failure_threshold": self.failure_threshold,
                "total_calls": self.total_calls,
                "successful_calls": self.successful_calls,
                "failed_calls": self.failed_calls,
                "rejected_calls": self.rejected_calls,
                "success_rate": round(success_rate, 2),
                "last_failure_time": self.last_failure_time,
                "recovery_timeout": self.recovery_timeout
            }
    
    def reset(self):
        """Manually reset the circuit breaker"""
        with self.lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED
            self.last_failure_time = None
            print(f"[CircuitBreaker:{self.name}] Manually reset to CLOSED state")

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

class CircuitBreakerManager:
    """Manages multiple circuit breakers"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.lock = threading.Lock()
    
    def get_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        with self.lock:
            if name not in self.breakers:
                self.breakers[name] = CircuitBreaker(name, **kwargs)
                print(f"[CircuitBreakerManager] Created circuit breaker: {name}")
            return self.breakers[name]
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers"""
        with self.lock:
            return {name: breaker.get_stats() for name, breaker in self.breakers.items()}
    
    def reset_all(self):
        """Reset all circuit breakers"""
        with self.lock:
            for breaker in self.breakers.values():
                breaker.reset()

# Global circuit breaker manager
circuit_manager = CircuitBreakerManager()

# Decorator for easy circuit breaker usage
def circuit_breaker(name: str, **breaker_kwargs):
    """Decorator to apply circuit breaker to a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            breaker = circuit_manager.get_breaker(name, **breaker_kwargs)
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator