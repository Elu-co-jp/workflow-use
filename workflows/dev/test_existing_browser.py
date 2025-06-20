#!/usr/bin/env python3
"""
Test workflow on existing browser session
"""
import asyncio
from workflow_use.workflow.service import Workflow

async def test_workflow_on_existing_browser():
    """Test workflow without creating new browser"""
    try:
        # Load workflow
        workflow = Workflow.load_from_file('workflows/examples/en-ambi-scout-recorded.workflow.json')
        print(f"Loaded workflow: {workflow.name}")
        
        # Test data
        test_data = {
            'memberNumber': '2982599',
            'message': 'はじめまして。弊社のポジションにご興味はございませんでしょうか？貴殿のご経験を拝見し、ぜひ一度お話させていただきたくご連絡いたしました。よろしくお願いいたします。'
        }
        
        print(f"Test data: {test_data}")
        print("Note: This would require connecting to existing browser session")
        print("Current implementation creates new browser instances")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    asyncio.run(test_workflow_on_existing_browser())