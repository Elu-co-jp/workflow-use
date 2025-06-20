#!/usr/bin/env python3
"""
Simple workflow runner that doesn't create/close browsers
"""
import asyncio
import csv
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List
import argparse
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def execute_workflow_step(step: Dict, row_data: Dict[str, str]) -> bool:
    """Execute a single workflow step using browser-use Controller"""
    try:
        from workflow_use.controller.service import WorkflowController
        
        controller = WorkflowController()
        step_type = step.get('type')
        
        logger.info(f"Executing step: {step.get('description', 'No description')}")
        logger.info(f"Step type: {step_type}")
        
        if step_type == 'navigation':
            url = step.get('url', '').format(**row_data)
            logger.info(f"Navigating to: {url}")
            await controller.navigate(url)
            
        elif step_type == 'click':
            selector = step.get('cssSelector', '')
            logger.info(f"Clicking: {selector}")
            
            # Try to click the element
            try:
                await controller.click(selector)
            except Exception as e:
                logger.warning(f"Primary selector failed: {e}")
                # Try XPath as fallback
                xpath = step.get('xpath', '')
                if xpath:
                    logger.info(f"Trying XPath fallback: {xpath}")
                    await controller.click(xpath)
                else:
                    raise e
                    
        elif step_type == 'input':
            selector = step.get('cssSelector', '')
            value = step.get('value', '').format(**row_data)
            logger.info(f"Inputting '{value}' into: {selector}")
            await controller.input_text(selector, value)
            
        # Small delay between steps
        await asyncio.sleep(1)
        return True
        
    except Exception as e:
        logger.error(f"Step execution failed: {e}")
        return False


async def run_workflow_for_row(workflow: Dict, row_data: Dict[str, str], row_index: int) -> Dict:
    """Run workflow for a single CSV row"""
    try:
        logger.info(f"Processing row {row_index + 1}: {row_data}")
        
        # Execute each workflow step
        for i, step in enumerate(workflow['steps']):
            logger.info(f"--- Running Step {i+1}/{len(workflow['steps'])} ---")
            
            success = await execute_workflow_step(step, row_data)
            if not success:
                logger.warning(f"Step {i+1} failed, continuing...")
                # Continue with next step instead of failing completely
                continue
        
        return {
            'row_index': row_index,
            'status': 'success',
            'data': row_data,
            'result': 'Workflow completed'
        }
        
    except Exception as e:
        logger.error(f"Error processing row {row_index + 1}: {str(e)}")
        return {
            'row_index': row_index,
            'status': 'error',
            'data': row_data,
            'error': str(e)
        }


async def process_csv_simple(csv_path: str, workflow_path: str) -> List[Dict]:
    """Process CSV file with simple workflow execution"""
    
    # Load workflow
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    logger.info(f"Loaded workflow: {workflow.get('name', 'Unknown')}")
    logger.info("Using simple execution mode (no browser management)")
    
    # Read CSV file
    results = []
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total_rows = len(rows)
        
        logger.info(f"Found {total_rows} rows in CSV file")
        
        # Process rows sequentially
        for i, row in enumerate(rows):
            logger.info(f"Processing candidate {i + 1}/{total_rows}")
            
            result = await run_workflow_for_row(workflow, row, i)
            results.append(result)
            
            # Add delay between candidates
            if i < total_rows - 1:
                logger.info("Waiting 3 seconds before next candidate...")
                await asyncio.sleep(3)
            
            # Progress update
            processed = i + 1
            logger.info(f"Progress: {processed}/{total_rows} candidates processed ({processed/total_rows*100:.1f}%)")
    
    return results


def save_results(results: List[Dict], output_path: str):
    """Save processing results to a file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{output_path}_{timestamp}.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        if not results:
            return
            
        # Create fieldnames from the first result
        fieldnames = ['row_index', 'status']
        if 'data' in results[0] and results[0]['data']:
            fieldnames.extend([f'input_{k}' for k in results[0]['data'].keys()])
        fieldnames.extend(['error', 'result'])
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            row = {
                'row_index': result['row_index'],
                'status': result['status']
            }
            
            # Add input data with prefix
            if 'data' in result:
                for k, v in result['data'].items():
                    row[f'input_{k}'] = v
            
            # Add error or result
            if 'error' in result:
                row['error'] = result['error']
            if 'result' in result:
                row['result'] = str(result['result'])
                
            writer.writerow(row)
    
    logger.info(f"Results saved to: {output_file}")
    return output_file


async def main():
    parser = argparse.ArgumentParser(description='Simple workflow runner (no browser management)')
    parser.add_argument('csv_file', help='Path to the CSV file')
    parser.add_argument('workflow_file', help='Path to the workflow JSON file')
    parser.add_argument('--output', default='results_simple', help='Output file prefix (default: results_simple)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.csv_file).exists():
        logger.error(f"CSV file not found: {args.csv_file}")
        sys.exit(1)
        
    if not Path(args.workflow_file).exists():
        logger.error(f"Workflow file not found: {args.workflow_file}")
        sys.exit(1)
    
    try:
        logger.info("Starting simple workflow execution...")
        logger.info("Note: This assumes a browser is already open and logged in")
        
        # Process the CSV
        results = await process_csv_simple(args.csv_file, args.workflow_file)
        
        # Save results
        output_file = save_results(results, args.output)
        
        # Summary
        success_count = sum(1 for r in results if r['status'] == 'success')
        error_count = sum(1 for r in results if r['status'] == 'error')
        
        logger.info(f"\nProcessing complete!")
        logger.info(f"Total rows: {len(results)}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Errors: {error_count}")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())