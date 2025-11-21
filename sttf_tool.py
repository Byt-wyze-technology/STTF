import sys
import argparse
sys.path.insert(0, 'src')

from sttf_generate import STTFBundleGenerator
from sttf_core import STTFBundle

def create_bundle_from_cnf(cnf_file, output_dir):
    """Read a CNF file and create STTF bundle"""
    print(f"Reading {cnf_file}...")
    
    clauses = []
    num_vars = 0
    
    with open(cnf_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('p cnf'):
                parts = line.split()
                num_vars = int(parts[2])
            elif line and not line.startswith('c') and not line.startswith('p'):
                lits = [int(x) for x in line.split() if x != '0']
                if lits:
                    clauses.append(lits)
    
    print(f"✓ {num_vars} variables, {len(clauses)} clauses")
    
    # Create bundle
    gen = STTFBundleGenerator(output_dir)
    gen.set_original_cnf(num_vars, clauses)
    gen.write_bundle("CNF-Tool", "1.0")
    
    print(f"\n✓ STTF bundle created: {output_dir}/")

def main():
    parser = argparse.ArgumentParser(description='STTF Command Line Tool')
    parser.add_argument('cnf_file', help='CNF file to process')
    parser.add_argument('-o', '--output', default='output_bundle', help='Output directory')
    
    args = parser.parse_args()
    create_bundle_from_cnf(args.cnf_file, args.output)

if __name__ == '__main__':
    main()