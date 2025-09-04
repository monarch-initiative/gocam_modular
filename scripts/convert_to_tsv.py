"""Convert JSONL files to properly formatted TSV files."""

import json
import csv
from pathlib import Path


def jsonl_to_tsv_fixed(jsonl_file, tsv_file, column_order=None):
    """Convert JSONL file to TSV format with proper handling of lists/arrays."""
    with open(jsonl_file, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        print(f'Warning: {jsonl_file} is empty')
        return
    
    # Collect all possible headers
    all_headers = set()
    objects = []
    for line in lines:
        obj = json.loads(line)
        all_headers.update(obj.keys())
        objects.append(obj)
    
    # Use specified column order if provided, otherwise sort alphabetically
    if column_order:
        # Start with specified order, then add any remaining columns
        headers = [col for col in column_order if col in all_headers]
        remaining = sorted([col for col in all_headers if col not in column_order])
        headers.extend(remaining)
    else:
        headers = sorted(list(all_headers))
    
    with open(tsv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter='\t')
        writer.writeheader()
        
        for obj in objects:
            row = {}
            for header in headers:
                value = obj.get(header, '')
                if isinstance(value, list):
                    # Handle lists properly - join with pipe separator for better readability
                    if len(value) == 1:
                        row[header] = value[0]  # Single item, no array notation
                    else:
                        row[header] = '|'.join(str(v) for v in value)  # Multiple items with pipe separator
                elif isinstance(value, dict):
                    row[header] = json.dumps(value)  # Keep dicts as JSON
                else:
                    row[header] = value
            writer.writerow(row)


def main():
    """Convert JSONL files in output directory to TSV format."""
    output_dir = Path('output')
    
    # Convert nodes file with proper column order
    nodes_jsonl = output_dir / 'go_cam_gene_to_gene_nodes.jsonl'
    if nodes_jsonl.exists():
        print('Converting nodes JSONL to TSV with correct column order...')
        nodes_column_order = ['id', 'name', 'category', 'in_taxon']
        jsonl_to_tsv_fixed(nodes_jsonl, output_dir / 'gocam_nodes.tsv', nodes_column_order)
    
    # Convert edges file  
    edges_jsonl = output_dir / 'go_cam_gene_to_gene_edges.jsonl'
    if edges_jsonl.exists():
        print('Converting edges JSONL to TSV with proper list handling...')
        jsonl_to_tsv_fixed(edges_jsonl, output_dir / 'gocam_edges.tsv')
    
    print('TSV conversion completed!')


if __name__ == '__main__':
    main()