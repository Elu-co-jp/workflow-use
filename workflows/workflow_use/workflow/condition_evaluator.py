"""
Condition evaluation engine for workflow conditional steps.
"""

import asyncio
import logging
from typing import Any, Dict

from browser_use import Browser

logger = logging.getLogger(__name__)


class WorkflowConditionError(Exception):
    """Exception raised when condition evaluation fails."""
    pass


class ConditionEvaluator:
    """Evaluates JavaScript conditions in browser context."""
    
    def __init__(self, browser: Browser):
        self.browser = browser
    
    async def evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any] | None = None,
        negate: bool = False
    ) -> bool:
        """
        Evaluate a JavaScript condition in the browser context.
        
        Args:
            condition: JavaScript expression to evaluate
            context: Optional context variables to substitute in condition
            negate: If True, returns the opposite of the condition result
            
        Returns:
            Boolean result of the condition evaluation
            
        Raises:
            WorkflowConditionError: If condition evaluation fails
        """
        try:
            # Substitute context variables if provided
            if context:
                # Simple string formatting for context variables
                try:
                    formatted_condition = condition.format(**context)
                except KeyError as e:
                    logger.warning(f"Context variable not found in condition: {e}")
                    formatted_condition = condition
            else:
                formatted_condition = condition
            
            logger.info(f"Evaluating condition: {formatted_condition}")
            
            # Get current page
            page = await self.browser.get_current_page()
            if not page:
                raise WorkflowConditionError("No active page available for condition evaluation")
            
            # Evaluate JavaScript condition
            result = await page.evaluate(formatted_condition)
            
            # Ensure result is boolean
            if not isinstance(result, bool):
                # Try to convert to boolean
                result = bool(result)
                logger.warning(f"Condition result was not boolean, converted: {result}")
            
            # Apply negation if requested
            final_result = not result if negate else result
            
            logger.info(f"Condition evaluation result: {final_result} (original: {result}, negated: {negate})")
            return final_result
            
        except Exception as e:
            error_msg = f"Failed to evaluate condition '{condition}': {str(e)}"
            logger.error(error_msg)
            raise WorkflowConditionError(error_msg) from e
    
    async def evaluate_dom_condition(
        self,
        selector: str,
        check_type: str = "exists",
        expected_text: str | None = None,
        context: Dict[str, Any] | None = None
    ) -> bool:
        """
        Evaluate DOM-based conditions using common patterns.
        
        Args:
            selector: CSS selector for the element
            check_type: Type of check ('exists', 'not_exists', 'contains_text', 'visible')
            expected_text: Expected text content (for contains_text check)
            context: Optional context variables
            
        Returns:
            Boolean result of the DOM condition
        """
        try:
            # Substitute context variables in selector if provided
            if context:
                try:
                    formatted_selector = selector.format(**context)
                except KeyError:
                    formatted_selector = selector
            else:
                formatted_selector = selector
            
            if check_type == "exists":
                condition = f"document.querySelector('{formatted_selector}') !== null"
            elif check_type == "not_exists":
                condition = f"document.querySelector('{formatted_selector}') === null"
            elif check_type == "visible":
                condition = f"""
                (() => {{
                    const el = document.querySelector('{formatted_selector}');
                    return el !== null && el.offsetParent !== null;
                }})()
                """
            elif check_type == "contains_text":
                if not expected_text:
                    raise WorkflowConditionError("expected_text is required for contains_text check")
                # Format expected_text with context if available
                if context:
                    try:
                        formatted_text = expected_text.format(**context)
                    except KeyError:
                        formatted_text = expected_text
                else:
                    formatted_text = expected_text
                
                condition = f"""
                (() => {{
                    const el = document.querySelector('{formatted_selector}');
                    return el !== null && el.textContent.includes('{formatted_text}');
                }})()
                """
            else:
                raise WorkflowConditionError(f"Unsupported check_type: {check_type}")
            
            return await self.evaluate_condition(condition)
            
        except WorkflowConditionError:
            raise
        except Exception as e:
            error_msg = f"Failed to evaluate DOM condition: {str(e)}"
            logger.error(error_msg)
            raise WorkflowConditionError(error_msg) from e