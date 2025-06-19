#!/usr/bin/env python3
"""
Test script for the conditional step functionality.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the workflow_use package to the path
sys.path.append(str(Path(__file__).parent))

from workflow_use.workflow.service import Workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def test_conditional_workflow():
    """Test the conditional step functionality."""
    print("Testing conditional workflow...")
    
    try:
        # Load the conditional test workflow
        workflow = Workflow.load_from_file(
            "examples/conditional-test.workflow.json"
        )
        
        print(f"Loaded workflow: {workflow.name}")
        print(f"Number of steps: {len(workflow.steps)}")
        
        # Run the workflow
        result = await workflow.run()
        
        print("Workflow completed successfully!")
        print(f"Number of step results: {len(result.step_results)}")
        
        return True
        
    except Exception as e:
        print(f"Workflow failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_detection():
    """Test the error detection workflow."""
    print("\nTesting error detection workflow...")
    
    try:
        # Load the error detection workflow
        workflow = Workflow.load_from_file(
            "examples/error-detection.workflow.json"  
        )
        
        print(f"Loaded workflow: {workflow.name}")
        print(f"Number of steps: {len(workflow.steps)}")
        
        # Run the workflow - should stop at 404 detection
        result = await workflow.run()
        
        print("Error detection workflow completed!")
        print(f"Number of step results: {len(result.step_results)}")
        print("Note: This should have stopped early due to condition detection")
        
        return True
        
    except Exception as e:
        print(f"Error detection workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("Starting conditional step tests...")
    
    # Test basic conditional functionality
    success1 = await test_conditional_workflow()
    
    # Test error detection
    success2 = await test_error_detection()
    
    if success1 and success2:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)