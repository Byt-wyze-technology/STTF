"""
STTF Bundle Generator
Utility for creating example STTF bundles for testing and demonstration.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any


class STTFBundleGenerator:
    """Generate valid STTF bundles with transformations."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.original_vars = 0
        self.original_clauses = []
        self.transform_steps = []
        self.rev_rules = []
        self.step_counter = 1
    
    def set_original_cnf(self, num_vars: int, clauses: List[List[int]]):
        """Set the original CNF formula."""
        self.original_vars = num_vars
        self.original_clauses = clauses
    
    def add_var_rename(self, old: int, new: int):
        """Add variable renaming transformation."""
        self.transform_steps.append(
            f"{self.step_counter} var_rename {old} {new}"
        )
        self.rev_rules.append(f"rev_map {new} -> {old}")
        self.step_counter += 1
    
    def add_var_elim(self, var: int, reason: str = "pure_literal"):
        """Add variable elimination transformation."""
        self.transform_steps.append(
            f"{self.step_counter} var_elim {var} {reason}"
        )
        # Eliminated variable needs reconstruction rule
        # For simplicity, set to false (would be determined by actual elimination)
        self.rev_rules.append(f"rev_elim {var} = false")
        self.step_counter += 1
    
    def add_var_subst(self, var: int, expr: str):
        """Add variable substitution transformation."""
        self.transform_steps.append(
            f"{self.step_counter} var_subst {var} = {expr}"
        )
        self.rev_rules.append(f"rev_elim_expr {var} = {expr}")
        self.step_counter += 1
    
    def add_clause_remove(self, clause_id: int, reason: str = "subsumed"):
        """Add clause removal transformation."""
        self.transform_steps.append(
            f"{self.step_counter} clause_remove {clause_id} {reason}"
        )
        self.step_counter += 1
    
    def add_clause_add(self, literals: List[int], source: str = "resolution"):
        """Add clause addition transformation."""
        lit_str = " ".join(map(str, literals))
        self.transform_steps.append(
            f"{self.step_counter} clause_add [{lit_str}] {source}"
        )
        self.step_counter += 1
    
    def add_clause_strengthen(self, clause_id: int, new_literals: List[int]):
        """Add clause strengthening transformation."""
        lit_str = " ".join(map(str, new_literals))
        self.transform_steps.append(
            f"{self.step_counter} clause_strengthen {clause_id} [{lit_str}]"
        )
        self.step_counter += 1
    
    def add_unit_derive(self, literal: int, source_clause: int):
        """Add unit derivation transformation."""
        self.transform_steps.append(
            f"{self.step_counter} unit_derive {literal} {source_clause}"
        )
        self.step_counter += 1
    
    def compute_simplified_cnf(self) -> Tuple[int, List[List[int]]]:
        """
        Compute simplified CNF by applying transformations.
        Returns: (num_vars, clauses)
        """
        # This is a simplified version - just tracks basic operations
        clauses = [c.copy() for c in self.original_clauses]
        clause_map = {i+1: c for i, c in enumerate(clauses)}
        eliminated = set()
        renamed = {}
        
        for step in self.transform_steps:
            parts = step.split(maxsplit=2)
            opcode = parts[1]
            args = parts[2] if len(parts) > 2 else ""
            
            if opcode == "var_rename":
                old, new = map(int, args.split())
                renamed[old] = new
                
            elif opcode == "var_elim":
                var = int(args.split()[0])
                eliminated.add(var)
                
            elif opcode == "var_subst":
                var = int(args.split("=")[0].strip())
                eliminated.add(var)
                
            elif opcode == "clause_remove":
                cid = int(args.split()[0])
                if cid in clause_map:
                    del clause_map[cid]
        
        # Apply renames and filter
        simplified = []
        for clause in clause_map.values():
            new_clause = []
            skip = False
            for lit in clause:
                var = abs(lit)
                if var in eliminated:
                    skip = True
                    break
                # Apply renames
                while var in renamed:
                    var = renamed[var]
                new_lit = var if lit > 0 else -var
                new_clause.append(new_lit)
            if not skip and new_clause:
                simplified.append(new_clause)
        
        # Count active variables
        active_vars = set()
        for clause in simplified:
            for lit in clause:
                active_vars.add(abs(lit))
        
        num_vars = max(active_vars) if active_vars else 0
        
        return num_vars, simplified
    
    def write_bundle(self, generator_name: str = "sttf_generator", 
                    generator_version: str = "1.0"):
        """Write complete STTF bundle to disk."""
        
        # Compute simplified CNF
        simp_vars, simp_clauses = self.compute_simplified_cnf()
        
        # Write original.cnf
        with open(self.output_dir / "original.cnf", "w") as f:
            f.write(f"p cnf {self.original_vars} {len(self.original_clauses)}\n")
            for clause in self.original_clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")
        
        # Write simplified.cnf
        with open(self.output_dir / "simplified.cnf", "w") as f:
            f.write(f"p cnf {simp_vars} {len(simp_clauses)}\n")
            for clause in simp_clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")
        
        # Write transform.log
        with open(self.output_dir / "transform.log", "w") as f:
            for step in self.transform_steps:
                f.write(step + "\n")
        
        # Write reconstruct.map
        with open(self.output_dir / "reconstruct.map", "w") as f:
            for rule in self.rev_rules:
                f.write(rule + "\n")
        
        # Write manifest.json
        manifest = {
            "version": "1.0",
            "generator": {
                "tool": generator_name,
                "version": generator_version
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "original": {
                "variables": self.original_vars,
                "clauses": len(self.original_clauses)
            },
            "simplified": {
                "variables": simp_vars,
                "clauses": len(simp_clauses)
            },
            "transformation_steps": len(self.transform_steps)
        }
        
        with open(self.output_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✓ STTF bundle written to {self.output_dir}")
        print(f"  Original: {self.original_vars} vars, {len(self.original_clauses)} clauses")
        print(f"  Simplified: {simp_vars} vars, {len(simp_clauses)} clauses")
        print(f"  Transform steps: {len(self.transform_steps)}")
        print(f"  Reverse rules: {len(self.rev_rules)}")


def generate_simple_example(output_dir: str):
    """
    Generate a simple example STTF bundle.
    
    Demonstrates basic transformations:
    - Variable elimination
    - Clause removal
    - Variable renaming
    """
    gen = STTFBundleGenerator(output_dir)
    
    # Original formula: (1 ∨ 2) ∧ (¬1 ∨ 3) ∧ (¬2 ∨ ¬3) ∧ (4)
    gen.set_original_cnf(
        num_vars=4,
        clauses=[
            [1, 2],      # clause 1
            [-1, 3],     # clause 2
            [-2, -3],    # clause 3
            [4]          # clause 4
        ]
    )
    
    # Transformation: eliminate variable 4 (pure literal)
    gen.add_var_elim(4, "pure_literal")
    
    # Transformation: remove clause 4
    gen.add_clause_remove(4, "pure_literal_clause")
    
    # Transformation: rename variable 3 to 5
    gen.add_var_rename(3, 5)
    
    gen.write_bundle("simple_example", "1.0")


def generate_complex_example(output_dir: str):
    """
    Generate a more complex example with substitutions.
    
    Demonstrates:
    - Variable substitution with expressions
    - Clause strengthening
    - Multiple eliminations
    """
    gen = STTFBundleGenerator(output_dir)
    
    # Larger formula
    gen.set_original_cnf(
        num_vars=8,
        clauses=[
            [1, 2, 3],
            [-1, 4],
            [-2, 5],
            [-3, 6],
            [7, 8],
            [-4, -5, 6],
            [-6, 7],
            [-7, -8]
        ]
    )
    
    # Substitute variable 8 with NOT(7)
    gen.add_var_subst(8, "NOT(7)")
    gen.add_clause_remove(5, "substitution")
    gen.add_clause_remove(8, "substitution")
    
    # Eliminate pure literal 4
    gen.add_var_elim(4, "pure_literal")
    gen.add_clause_remove(2, "pure_literal_clause")
    
    # Strengthen clause 6
    gen.add_clause_strengthen(6, [-5, 6])
    
    gen.write_bundle("complex_example", "1.0")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        output = sys.argv[1]
    else:
        output = "/tmp/sttf_example"
    
    print("Generating simple STTF bundle...")
    generate_simple_example(output + "_simple")
    
    print("\nGenerating complex STTF bundle...")
    generate_complex_example(output + "_complex")
