#!/usr/bin/env python3
"""
Simple manual workflow test using current browser tab
"""
import asyncio
import json
from pathlib import Path

def load_workflow(workflow_path: str):
    """Load workflow from JSON file"""
    with open(workflow_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_test_data(csv_path: str):
    """Load test data from CSV"""
    import csv
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

async def main():
    # Load workflow and test data
    workflow = load_workflow('workflows/examples/en-ambi-scout-recorded.workflow.json')
    test_data = load_test_data('workflows/examples/en-ambi-test.csv')[0]  # First row
    
    print("=== Manual Workflow Test ===")
    print(f"Workflow: {workflow['name']}")
    print(f"Test data: {test_data}")
    print("\nSteps to execute manually in your browser:")
    print("(Open VNC viewer: http://localhost:6080/vnc.html)")
    print()
    
    for i, step in enumerate(workflow['steps'], 1):
        step_type = step.get('type')
        description = step.get('description', 'No description')
        
        print(f"Step {i}: {description}")
        print(f"  Type: {step_type}")
        
        if step_type == 'navigation':
            url = step.get('url', '').format(**test_data)
            print(f"  → Navigate to: {url}")
            
        elif step_type == 'click':
            selector = step.get('cssSelector', '')
            xpath = step.get('xpath', '')
            print(f"  → Click element:")
            print(f"    CSS: {selector}")
            if xpath:
                print(f"    XPath: {xpath}")
                
        elif step_type == 'input':
            selector = step.get('cssSelector', '')
            value = step.get('value', '').format(**test_data)
            print(f"  → Input into element:")
            print(f"    CSS: {selector}")
            print(f"    Value: {value}")
        
        print()
        
        # Wait for user to complete step
        input(f"Press Enter after completing Step {i}...")
    
    print("✅ Manual workflow test completed!")
    print("If all steps worked, the workflow should be ready for automation.")

if __name__ == '__main__':
    asyncio.run(main())