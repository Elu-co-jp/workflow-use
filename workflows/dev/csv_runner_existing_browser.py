#!/usr/bin/env python3
"""
CSV runner that uses existing browser session
"""
import asyncio
import csv
import sys
from pathlib import Path
from typing import Dict, List
import argparse
import logging
from datetime import datetime
import websockets
import json

from workflow_use.workflow.service import Workflow
from playwright.async_api import async_playwright, connect

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def find_existing_browser():
    """Try to connect to existing browser sessions"""
    try:
        # Try common browser debug ports
        debug_ports = [9222, 9223, 9224]
        
        for port in debug_ports:
            try:
                # Try to connect to Chrome DevTools Protocol
                playwright = await async_playwright().start()
                browser = await playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
                
                contexts = browser.contexts
                if contexts:
                    logger.info(f"Connected to existing browser on port {port}")
                    return browser, contexts[0], playwright
                    
                await browser.close()
                
            except Exception as e:
                logger.debug(f"Port {port} failed: {e}")
                continue
                
        logger.warning("No existing browser found, will create new one")
        return None, None, None
        
    except Exception as e:
        logger.error(f"Error finding existing browser: {e}")
        return None, None, None


async def run_workflow_for_row(workflow: Workflow, row_data: Dict[str, str], row_index: int, context) -> Dict:
    """Run workflow for a single CSV row using existing browser context"""
    try:
        logger.info(f"Processing row {row_index + 1}: {row_data}")
        
        # Create new page in existing context
        page = await context.new_page()
        
        # Execute workflow steps manually using existing browser
        await execute_workflow_steps(workflow, row_data, page)
        
        await page.close()
        
        return {
            'row_index': row_index,
            'status': 'success',
            'data': row_data,
            'result': 'Completed'
        }
        
    except Exception as e:
        logger.error(f"Error processing row {row_index + 1}: {str(e)}")
        return {
            'row_index': row_index,
            'status': 'error',
            'data': row_data,
            'error': str(e)
        }


async def execute_workflow_steps(workflow: Workflow, row_data: Dict[str, str], page):
    """Execute workflow steps on existing page"""
    
    for i, step in enumerate(workflow.steps):
        logger.info(f"--- Running Step {i+1}/{len(workflow.steps)} -- {step.get('description', 'No description')} ---")
        
        step_type = step.get('type')
        
        try:
            if step_type == 'navigation':
                url = step.get('url', '').format(**row_data)
                logger.info(f"Navigating to: {url}")
                await page.goto(url)
                
            elif step_type == 'click':
                selector = step.get('cssSelector', '')
                logger.info(f"Clicking: {selector}")
                await page.click(selector, timeout=10000)
                
            elif step_type == 'input':
                selector = step.get('cssSelector', '')
                value = step.get('value', '').format(**row_data)
                logger.info(f"Inputting '{value}' into: {selector}")
                await page.fill(selector, value)
                
            # Wait between steps
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Step {i+1} failed: {e}")
            # Continue to next step instead of failing completely
            continue


async def process_csv_existing_browser(csv_path: str, workflow_path: str) -> List[Dict]:
    """Process CSV file using existing browser session"""
    
    # Try to find existing browser
    browser, context, playwright = await find_existing_browser()
    
    if not browser:
        logger.error("No existing browser found. Please open a browser first.")
        return []
    
    try:
        # Load workflow
        workflow = Workflow.load_from_file(workflow_path)
        logger.info(f"Loaded workflow: {workflow.name}")
        logger.info("Using existing browser session")
        
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
                
                result = await run_workflow_for_row(workflow, row, i, context)
                results.append(result)
                
                # Add delay between candidates
                if i < total_rows - 1:
                    logger.info("Waiting 3 seconds before next candidate...")
                    await asyncio.sleep(3)
                
                # Progress update
                processed = i + 1
                logger.info(f"Progress: {processed}/{total_rows} candidates processed ({processed/total_rows*100:.1f}%)")
        
        return results
        
    finally:
        # Don't close the browser - keep it for user
        if playwright:
            await playwright.stop()


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
    parser = argparse.ArgumentParser(description='Run workflow using existing browser session')
    parser.add_argument('csv_file', help='Path to the CSV file')
    parser.add_argument('workflow_file', help='Path to the workflow JSON file')
    parser.add_argument('--output', default='results_existing', help='Output file prefix (default: results_existing)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.csv_file).exists():
        logger.error(f"CSV file not found: {args.csv_file}")
        sys.exit(1)
        
    if not Path(args.workflow_file).exists():
        logger.error(f"Workflow file not found: {args.workflow_file}")
        sys.exit(1)
    
    try:
        logger.info("Looking for existing browser session...")
        
        # Process the CSV using existing browser
        results = await process_csv_existing_browser(args.csv_file, args.workflow_file)
        
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