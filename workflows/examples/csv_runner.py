import asyncio
import csv
import sys
from pathlib import Path
from typing import Dict, List
import argparse
import logging
from datetime import datetime

from workflow_use.workflow.service import Workflow
from browser_use import Browser


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_workflow_for_row(workflow: Workflow, row_data: Dict[str, str], row_index: int) -> Dict:
    """Run workflow for a single CSV row"""
    try:
        logger.info(f"Processing row {row_index + 1}: {row_data}")
        
        # Run the workflow with the row data as inputs
        # Keep browser open for batch processing (only close on last row)
        is_last_row = row_index == (getattr(workflow, '_total_rows', 0) - 1)
        result = await workflow.run(
            inputs=row_data,
            close_browser_at_end=is_last_row,
        )

        return {
            'row_index': row_index,
            'status': 'success',
            'data': row_data,
            'result': result
        }
    except Exception as e:
        logger.error(f"Error processing row {row_index + 1}: {str(e)}")
        return {
            'row_index': row_index,
            'status': 'error',
            'data': row_data,
            'error': str(e)
        }


async def process_csv(csv_path: str, workflow_path: str, headless: bool = False) -> List[Dict]:
    """Process CSV file and run workflow for each row"""
    
    # Create browser with headless mode setting
    browser = Browser(headless=headless)
    
    # Load the workflow with the browser
    workflow = Workflow.load_from_file(workflow_path, browser=browser)
    logger.info(f"Loaded workflow: {workflow.name}")
    logger.info(f"Browser mode: {'Headless' if headless else 'Visual (check http://localhost:6080/vnc.html)'}")
    
    # Read CSV file
    results = []
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total_rows = len(rows)
        
        logger.info(f"Found {total_rows} rows in CSV file")
        
        # Store total rows in workflow for browser management
        workflow._total_rows = total_rows
        
        # Process rows sequentially to maintain browser state
        for i, row in enumerate(rows):
            logger.info(f"Processing candidate {i + 1}/{total_rows}")
            
            # Process each row sequentially (not concurrently)
            result = await run_workflow_for_row(workflow, row, i)
            results.append(result)
            
            # Add delay between candidates (except for the last one)
            if i < total_rows - 1:
                logger.info("Waiting 5 seconds before next candidate...")
                await asyncio.sleep(5)
            
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
    parser = argparse.ArgumentParser(description='Run workflow for each row in a CSV file')
    parser.add_argument('csv_file', help='Path to the CSV file')
    parser.add_argument('workflow_file', help='Path to the workflow JSON file')
    parser.add_argument('--output', default='results', help='Output file prefix for results (default: results)')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode (default: visual mode)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.csv_file).exists():
        logger.error(f"CSV file not found: {args.csv_file}")
        sys.exit(1)
        
    if not Path(args.workflow_file).exists():
        logger.error(f"Workflow file not found: {args.workflow_file}")
        sys.exit(1)
    
    try:
        # Show VNC info if in visual mode
        if not args.headless:
            logger.info("\n" + "="*60)
            logger.info("🖥️  Visual Mode Enabled!")
            logger.info("🌐 Open http://localhost:6080/vnc.html in your browser")
            logger.info("   to see the browser automation in action!")
            logger.info("="*60 + "\n")
            await asyncio.sleep(3)  # Give user time to open VNC viewer
        
        # Process the CSV
        results = await process_csv(args.csv_file, args.workflow_file, args.headless)
        
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