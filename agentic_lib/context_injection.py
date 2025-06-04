"""
Context Injection Decorator for Tools

Provides automatic dependency injection of context fields into tool functions.
"""

from typing import List, Callable, Set
import inspect
from functools import wraps


def context_inject(*field_names: str):
    """
    Decorator que valida e inyecta campos del contexto automáticamente.
    
    Usage:
        @context_inject("message_history", "index_name")
        async def search(self, message_history: List[Dict], index_name: str, args: SearchProductsArgs):
            # message_history e index_name se inyectan automáticamente del Context
            pass
    
    Args:
        *field_names: Names of Context fields to inject into the function
        
    Raises:
        ValueError: If requested fields don't exist in Context or signature mismatch
    """
    def decorator(func: Callable) -> Callable:
        # ✅ Updated import for standalone operation
        from spartacus_services.context import Context
        
        # Check if requested fields exist in Context
        context_fields = set(Context.__annotations__.keys())
        missing_fields = [f for f in field_names if f not in context_fields]
        
        if missing_fields:
            available_fields = sorted(context_fields)
            raise ValueError(
                f"Function {func.__name__} requests context fields {missing_fields} "
                f"that don't exist in Context.\n"
                f"Available fields: {available_fields}"
            )
        
        # ✅ Validation de function signature
        sig = inspect.signature(func)
        func_params = set(sig.parameters.keys()) - {'self', 'args'}
        expected_params = set(field_names)
        
        if func_params != expected_params:
            raise ValueError(
                f"Function {func.__name__} signature mismatch.\n"
                f"Decorator specifies: {sorted(field_names)}\n"
                f"Function parameters: {sorted(func_params)}\n"
                f"(excluding 'self' and 'args')"
            )
        
        # ✅ Store metadata en la función
        func._context_fields = field_names
        func._needs_context_injection = True
        
        print(f"✅ Context injection configured for {func.__name__}: {list(field_names)}")
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        # Copy metadata al wrapper
        wrapper._context_fields = field_names
        wrapper._needs_context_injection = True
        
        return wrapper
    
    return decorator


def get_context_fields(func: Callable) -> List[str]:
    """
    Helper function to get context fields required by a function.
    
    Returns:
        List of field names required from Context, or empty list if no injection needed
    """
    if hasattr(func, '_context_fields'):
        return list(func._context_fields)
    return []


def needs_context_injection(func: Callable) -> bool:
    """
    Check if a function needs context injection.
    
    Returns:
        True if function is decorated with @context_inject
    """
    return getattr(func, '_needs_context_injection', False) 