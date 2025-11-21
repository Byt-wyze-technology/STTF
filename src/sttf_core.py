"""
SAT Transformation Trace Format (STTF) - Core Library
Version: 1.0

Implements the complete STTF standard for SAT CNF transformations.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional


class Expr:
    """Boolean expression evaluator for substitution and model reconstruction."""
    
    def __init__(self, text: str):
        self.text = text.strip()
    
    def eval(self, model: Dict[int, bool]) -> bool:
        """
        Evaluate expression using model {var: bool}.
        
        Args:
            model: Dictionary mapping variable numbers to boolean values
            
        Returns:
            Boolean result of expression evaluation
            
        Raises:
            ValueError: If variable undefined in model or expression invalid
        """
        return self._eval(self.text, model)
    
    def _eval(self, t: str, model: Dict[int, bool]) -> bool:
        t = t.strip()
        
        # Literal: positive or negative integer
        if re.fullmatch(r"-?\d+", t):
            v = int(t)
            val = model.get(abs(v), None)
            if val is None:
                raise ValueError(f"Undefined variable {abs(v)} in model")
            return val if v > 0 else (not val)
        
        # NOT(expr)
        if t.startswith("NOT(") and t.endswith(")"):
            return not self._eval(t[4:-1], model)
        
        # AND(expr, expr)
        if t.startswith("AND(") and t.endswith(")"):
            a, b = self._split_args(t[4:-1])
            return self._eval(a, model) and self._eval(b, model)
        
        # OR(expr, expr)
        if t.startswith("OR(") and t.endswith(")"):
            a, b = self._split_args(t[3:-1])
            return self._eval(a, model) or self._eval(b, model)
        
        # XOR(expr, expr)
        if t.startswith("XOR(") and t.endswith(")"):
            a, b = self._split_args(t[4:-1])
            return self._eval(a, model) ^ self._eval(b, model)
        
        raise ValueError(f"Invalid expression: {t}")
    
    def _split_args(self, s: str) -> Tuple[str, str]:
        """Split comma-separated arguments respecting parenthesis depth."""
        depth = 0
        for i, ch in enumerate(s):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "," and depth == 0:
                return s[:i].strip(), s[i+1:].strip()
        raise ValueError(f"Malformed expression arguments: {s}")
    
    def __repr__(self):
        return f"Expr({self.text})"


class STTFBundle:
    """
    STTF Bundle loader and processor.
    
    Loads and validates a complete STTF bundle containing:
    - original.cnf
    - simplified.cnf
    - transform.log
    - reconstruct.map
    - manifest.json
    """
    
    def __init__(self, bundle_path: str):
        self.path = Path(bundle_path)
        self.original = self.path / "original.cnf"
        self.simplified = self.path / "simplified.cnf"
        self.transform = self.path / "transform.log"
        self.reconstruct = self.path / "reconstruct.map"
        self.manifest_file = self.path / "manifest.json"
        
        self.transform_steps: List[Tuple[int, str, str]] = []
        self.rev_rules: List[Tuple] = []
        self.manifest_data: Dict[str, Any] = {}
        
        self._validate_structure()
        self._load()
    
    def _validate_structure(self):
        """Validate that all required files exist."""
        required = [
            self.original,
            self.simplified,
            self.transform,
            self.reconstruct,
            self.manifest_file
        ]
        
        for file in required:
            if not file.exists():
                raise FileNotFoundError(f"Required STTF file missing: {file}")
    
    def _load(self):
        """Load all bundle components."""
        # Load transform log
        with open(self.transform) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    step, opcode, rest = self._parse_transform_line(line)
                    self.transform_steps.append((step, opcode, rest))
                except Exception as e:
                    raise ValueError(f"Transform log line {line_num}: {e}")
        
        # Load reconstruct map
        with open(self.reconstruct) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    self.rev_rules.append(self._parse_reverse_line(line))
                except Exception as e:
                    raise ValueError(f"Reconstruct map line {line_num}: {e}")
        
        # Load manifest
        with open(self.manifest_file) as f:
            self.manifest_data = json.load(f)
        
        self._validate_manifest()
    
    def _validate_manifest(self):
        """Validate manifest structure and content."""
        required_keys = ["version", "generator", "original", "simplified"]
        for key in required_keys:
            if key not in self.manifest_data:
                raise ValueError(f"Manifest missing required key: {key}")
        
        # Validate metadata
        orig = self.manifest_data["original"]
        simp = self.manifest_data["simplified"]
        
        if not all(k in orig for k in ["variables", "clauses"]):
            raise ValueError("Manifest original metadata incomplete")
        
        if not all(k in simp for k in ["variables", "clauses"]):
            raise ValueError("Manifest simplified metadata incomplete")
        
        if orig["variables"] <= 0 or orig["clauses"] <= 0:
            raise ValueError("Invalid original CNF metadata")
        
        if simp["variables"] <= 0 or simp["clauses"] <= 0:
            raise ValueError("Invalid simplified CNF metadata")
    
    def _parse_transform_line(self, line: str) -> Tuple[int, str, str]:
        """Parse a transformation log line: <step> <opcode> <args>"""
        m = re.match(r"(\d+)\s+(\w+)\s+(.*)", line)
        if not m:
            raise ValueError(f"Invalid transform line format: {line}")
        
        step = int(m.group(1))
        opcode = m.group(2)
        args = m.group(3)
        
        # Validate opcode
        valid_opcodes = {
            "var_rename", "var_elim", "var_subst",
            "clause_remove", "clause_add", "clause_strengthen",
            "unit_derive"
        }
        
        if opcode not in valid_opcodes:
            raise ValueError(f"Invalid opcode: {opcode}")
        
        return step, opcode, args
    
    def _parse_reverse_line(self, line: str) -> Tuple:
        """Parse a reconstruction rule line."""
        # rev_map bvar -> avar
        if line.startswith("rev_map"):
            m = re.match(r"rev_map\s+(\d+)\s*->\s*(\d+)", line)
            if not m:
                raise ValueError(f"Invalid rev_map format: {line}")
            return ("rev_map", int(m.group(1)), int(m.group(2)))
        
        # rev_elim v = value
        if line.startswith("rev_elim "):
            m = re.match(r"rev_elim\s+(\d+)\s*=\s*(true|false)", line)
            if not m:
                raise ValueError(f"Invalid rev_elim format: {line}")
            return ("rev_elim", int(m.group(1)), m.group(2) == "true")
        
        # rev_elim_expr v = expr
        if line.startswith("rev_elim_expr"):
            m = re.match(r"rev_elim_expr\s+(\d+)\s*=\s*(.*)", line)
            if not m:
                raise ValueError(f"Invalid rev_elim_expr format: {line}")
            return ("rev_elim_expr", int(m.group(1)), Expr(m.group(2)))
        
        # rev_clause_add id [literals]
        if line.startswith("rev_clause_add"):
            m = re.match(r"rev_clause_add\s+(\d+)\s+(\[.*\])", line)
            if not m:
                raise ValueError(f"Invalid rev_clause_add format: {line}")
            lits = [int(x) for x in re.findall(r"-?\d+", m.group(2))]
            return ("rev_clause_add", int(m.group(1)), lits)
        
        raise ValueError(f"Invalid reconstruct rule: {line}")
    
    def lift_model(self, model_B: Dict[int, bool]) -> Dict[int, bool]:
        """
        Lift a model from simplified CNF (B) to original CNF (A).
        
        Args:
            model_B: SAT model for simplified.cnf {variable: boolean}
            
        Returns:
            SAT model for original.cnf {variable: boolean}
            
        The reverse mapping rules are applied in order to reconstruct
        eliminated/substituted variables.
        """
        model_A = model_B.copy()
        
        # Apply reverse mappings in order
        for rule in self.rev_rules:
            typ = rule[0]
            
            if typ == "rev_map":
                # Variable renaming: map B variable to A variable
                b, a = rule[1], rule[2]
                if b in model_A:
                    model_A[a] = model_A[b]
            
            elif typ == "rev_elim":
                # Constant elimination: restore fixed value
                v, val = rule[1], rule[2]
                model_A[v] = val
            
            elif typ == "rev_elim_expr":
                # Expression substitution: evaluate to restore value
                v, expr = rule[1], rule[2]
                model_A[v] = expr.eval(model_A)
            
            elif typ == "rev_clause_add":
                # Clause added during transformation (no model impact)
                pass
        
        return model_A
    
    def get_transform_summary(self) -> Dict[str, Any]:
        """Get summary statistics about the transformation."""
        opcodes = {}
        for _, op, _ in self.transform_steps:
            opcodes[op] = opcodes.get(op, 0) + 1
        
        return {
            "total_steps": len(self.transform_steps),
            "opcodes": opcodes,
            "reverse_rules": len(self.rev_rules),
            "original_vars": self.manifest_data["original"]["variables"],
            "original_clauses": self.manifest_data["original"]["clauses"],
            "simplified_vars": self.manifest_data["simplified"]["variables"],
            "simplified_clauses": self.manifest_data["simplified"]["clauses"],
        }
