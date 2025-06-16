import asyncio
import csv
import sys
from pathlib import Path
from typing import Dict, List
import argparse
import logging
from datetime import datetime

from workflow_use.workflow.service import Workflow


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
        result = await workflow.run(
            inputs=row_data,
            close_browser_at_end=True,
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


async def process_csv(csv_path: str, workflow_path: str, batch_size: int = 1) -> List[Dict]:
    """Process CSV file and run workflow for each row"""
    
    # Load the workflow
    workflow = Workflow.load_from_file(workflow_path)
    logger.info(f"Loaded workflow: {workflow.name}")
    
    # Read CSV file
    results = []
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total_rows = len(rows)
        
        logger.info(f"Found {total_rows} rows in CSV file")
        
        # Process rows in batches
        for i in range(0, total_rows, batch_size):
            batch = rows[i:i + batch_size]
            batch_tasks = []
            
            for j, row in enumerate(batch):
                row_index = i + j
                task = run_workflow_for_row(workflow, row, row_index)
                # 5秒待機
                await asyncio.sleep(5)
                batch_tasks.append(task)
            
            # Run batch concurrently
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
            
            # Progress update
            processed = min(i + batch_size, total_rows)
            logger.info(f"Progress: {processed}/{total_rows} rows processed ({processed/total_rows*100:.1f}%)")
    
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
    parser.add_argument('--batch-size', type=int, default=1, help='Number of rows to process concurrently (default: 1)')
    parser.add_argument('--output', default='results', help='Output file prefix for results (default: results)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.csv_file).exists():
        logger.error(f"CSV file not found: {args.csv_file}")
        sys.exit(1)
        
    if not Path(args.workflow_file).exists():
        logger.error(f"Workflow file not found: {args.workflow_file}")
        sys.exit(1)
    
    try:
        # Process the CSV
        results = await process_csv(args.csv_file, args.workflow_file, args.batch_size)
        
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