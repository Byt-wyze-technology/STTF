"""
STTF Replay Engine
Deterministically replays transformations to reconstruct simplified CNF from original CNF.
"""

from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
import re


class CNFFormula:
    """In-memory representation of a CNF formula."""
    
    def __init__(self):
        self.num_vars: int = 0
        self.clauses: List[List[int]] = []
        self.clause_ids: Dict[int, List[int]] = {}  # clause_id -> clause
        self.next_clause_id: int = 1
        self.var_mapping: Dict[int, int] = {}  # old -> new for renames
        self.eliminated_vars: Set[int] = set()
        self.substitutions: Dict[int, str] = {}  # var -> expression
    
    def add_clause(self, literals: List[int], clause_id: Optional[int] = None) -> int:
        """Add a clause and return its ID."""
        if clause_id is None:
            clause_id = self.next_clause_id
            self.next_clause_id += 1
        
        self.clauses.append(literals)
        self.clause_ids[clause_id] = literals
        return clause_id
    
    def remove_clause(self, clause_id: int):
        """Remove a clause by ID."""
        if clause_id in self.clause_ids:
            clause = self.clause_ids[clause_id]
            if clause in self.clauses:
                self.clauses.remove(clause)
            del self.clause_ids[clause_id]
    
    def rename_var(self, old: int, new: int):
        """Rename variable throughout formula."""
        self.var_mapping[old] = new
        
        # Update all clauses - preserve sign of literal
        for i, clause in enumerate(self.clauses):
            self.clauses[i] = [
                (new if lit > 0 else -new) if abs(lit) == old else lit 
                for lit in clause
            ]
        
        # Update clause_ids mapping
        for cid, clause in self.clause_ids.items():
            self.clause_ids[cid] = [
                (new if lit > 0 else -new) if abs(lit) == old else lit 
                for lit in clause
            ]
    
    def eliminate_var(self, var: int):
        """Mark variable as eliminated."""
        self.eliminated_vars.add(var)
    
    def substitute_var(self, var: int, expr: str):
        """Record variable substitution."""
        self.substitutions[var] = expr
        self.eliminated_vars.add(var)
    
    def strengthen_clause(self, clause_id: int, new_literals: List[int]):
        """Replace clause with strengthened version."""
        if clause_id in self.clause_ids:
            old_clause = self.clause_ids[clause_id]
            if old_clause in self.clauses:
                idx = self.clauses.index(old_clause)
                self.clauses[idx] = new_literals
            self.clause_ids[clause_id] = new_literals
    
    def add_unit(self, literal: int):
        """Add unit clause."""
        self.add_clause([literal])
    
    def get_active_vars(self) -> Set[int]:
        """Get set of variables appearing in current clauses."""
        active = set()
        for clause in self.clauses:
            for lit in clause:
                active.add(abs(lit))
        return active
    
    def to_dimacs(self) -> str:
        """Export to DIMACS CNF format."""
        active_vars = self.get_active_vars()
        num_vars = max(active_vars) if active_vars else 0
        num_clauses = len(self.clauses)
        
        lines = [f"p cnf {num_vars} {num_clauses}"]
        for clause in self.clauses:
            lines.append(" ".join(map(str, clause)) + " 0")
        
        return "\n".join(lines) + "\n"


class STTFReplayEngine:
    """
    Replays transformation log to reconstruct simplified CNF.
    """
    
    def __init__(self, original_cnf_path: str, transform_log_path: str):
        self.original_path = Path(original_cnf_path)
        self.transform_path = Path(transform_log_path)
        self.formula = CNFFormula()
        
    def load_original(self):
        """Load original CNF from DIMACS file."""
        with open(self.original_path) as f:
            clause_id = 1
            for line in f:
                line = line.strip()
                if not line or line.startswith("c"):
                    continue
                
                if line.startswith("p"):
                    # Parse header: p cnf <vars> <clauses>
                    parts = line.split()
                    self.formula.num_vars = int(parts[2])
                    continue
                
                # Parse clause
                literals = [int(x) for x in line.split() if x != "0"]
                if literals:
                    self.formula.add_clause(literals, clause_id)
                    clause_id += 1
    
    def replay_transformation(self) -> CNFFormula:
        """
        Apply all transformation steps to reconstruct simplified formula.
        
        Returns:
            CNFFormula representing the simplified CNF
        """
        self.load_original()
        
        with open(self.transform_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                try:
                    self._apply_transform_step(line)
                except Exception as e:
                    raise ValueError(f"Transform line {line_num}: {e}")
        
        return self.formula
    
    def _apply_transform_step(self, line: str):
        """Apply a single transformation step."""
        # Parse: <step> <opcode> <args>
        m = re.match(r"(\d+)\s+(\w+)\s+(.*)", line)
        if not m:
            raise ValueError(f"Invalid transform line: {line}")
        
        step = int(m.group(1))
        opcode = m.group(2)
        args = m.group(3)
        
        # Dispatch to handler
        if opcode == "var_rename":
            self._handle_var_rename(args)
        elif opcode == "var_elim":
            self._handle_var_elim(args)
        elif opcode == "var_subst":
            self._handle_var_subst(args)
        elif opcode == "clause_remove":
            self._handle_clause_remove(args)
        elif opcode == "clause_add":
            self._handle_clause_add(args)
        elif opcode == "clause_strengthen":
            self._handle_clause_strengthen(args)
        elif opcode == "unit_derive":
            self._handle_unit_derive(args)
        else:
            raise ValueError(f"Unknown opcode: {opcode}")
    
    def _handle_var_rename(self, args: str):
        """Handle var_rename old new"""
        parts = args.split()
        old, new = int(parts[0]), int(parts[1])
        self.formula.rename_var(old, new)
    
    def _handle_var_elim(self, args: str):
        """Handle var_elim v reason"""
        parts = args.split(maxsplit=1)
        var = int(parts[0])
        reason = parts[1] if len(parts) > 1 else ""
        self.formula.eliminate_var(var)
        
        # Remove clauses containing this variable
        to_remove = []
        for cid, clause in self.formula.clause_ids.items():
            if any(abs(lit) == var for lit in clause):
                to_remove.append(cid)
        
        for cid in to_remove:
            self.formula.remove_clause(cid)
    
    def _handle_var_subst(self, args: str):
        """Handle var_subst v = expr"""
        m = re.match(r"(\d+)\s*=\s*(.*)", args)
        if not m:
            raise ValueError(f"Invalid var_subst args: {args}")
        
        var = int(m.group(1))
        expr = m.group(2)
        self.formula.substitute_var(var, expr)
        
        # Remove clauses containing this variable
        to_remove = []
        for cid, clause in self.formula.clause_ids.items():
            if any(abs(lit) == var for lit in clause):
                to_remove.append(cid)
        
        for cid in to_remove:
            self.formula.remove_clause(cid)
    
    def _handle_clause_remove(self, args: str):
        """Handle clause_remove id reason"""
        parts = args.split(maxsplit=1)
        clause_id = int(parts[0])
        reason = parts[1] if len(parts) > 1 else ""
        self.formula.remove_clause(clause_id)
    
    def _handle_clause_add(self, args: str):
        """Handle clause_add [l1 l2 ... lk] source"""
        # Parse clause: [l1 l2 ... lk]
        m = re.search(r"\[([^\]]*)\]", args)
        if not m:
            raise ValueError(f"Invalid clause_add args: {args}")
        
        literals = [int(x) for x in m.group(1).split()]
        self.formula.add_clause(literals)
    
    def _handle_clause_strengthen(self, args: str):
        """Handle clause_strengthen old_id [new_clause]"""
        parts = args.split(maxsplit=1)
        clause_id = int(parts[0])
        
        # Parse new clause
        m = re.search(r"\[([^\]]*)\]", parts[1])
        if not m:
            raise ValueError(f"Invalid clause_strengthen args: {args}")
        
        literals = [int(x) for x in m.group(1).split()]
        self.formula.strengthen_clause(clause_id, literals)
    
    def _handle_unit_derive(self, args: str):
        """Handle unit_derive lit source_clause"""
        parts = args.split()
        literal = int(parts[0])
        source = int(parts[1]) if len(parts) > 1 else 0
        self.formula.add_unit(literal)
    
    def write_simplified(self, output_path: str):
        """Write simplified formula to DIMACS file."""
        dimacs = self.formula.to_dimacs()
        with open(output_path, "w") as f:
            f.write(dimacs)


def replay_bundle(bundle_path: str, output_path: Optional[str] = None) -> CNFFormula:
    """
    Convenience function to replay a complete STTF bundle.
    
    Args:
        bundle_path: Path to STTF bundle directory
        output_path: Optional path to write simplified.cnf
        
    Returns:
        CNFFormula representing simplified CNF
    """
    from pathlib import Path
    
    bundle = Path(bundle_path)
    original = bundle / "original.cnf"
    transform = bundle / "transform.log"
    
    engine = STTFReplayEngine(str(original), str(transform))
    formula = engine.replay_transformation()
    
    if output_path:
        engine.write_simplified(output_path)
    
    return formula
