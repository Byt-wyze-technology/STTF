"""
STTF Test Suite
Comprehensive tests for the STTF implementation.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sttf_core import Expr, STTFBundle
from sttf_replay import STTFReplayEngine, CNFFormula
from sttf_generate import STTFBundleGenerator


class TestExpr(unittest.TestCase):
    """Test boolean expression evaluator."""
    
    def test_literal_positive(self):
        expr = Expr("5")
        model = {5: True}
        self.assertTrue(expr.eval(model))
        
        model = {5: False}
        self.assertFalse(expr.eval(model))
    
    def test_literal_negative(self):
        expr = Expr("-5")
        model = {5: True}
        self.assertFalse(expr.eval(model))
        
        model = {5: False}
        self.assertTrue(expr.eval(model))
    
    def test_not_operator(self):
        expr = Expr("NOT(3)")
        model = {3: True}
        self.assertFalse(expr.eval(model))
        
        model = {3: False}
        self.assertTrue(expr.eval(model))
    
    def test_and_operator(self):
        expr = Expr("AND(1, 2)")
        self.assertTrue(expr.eval({1: True, 2: True}))
        self.assertFalse(expr.eval({1: True, 2: False}))
        self.assertFalse(expr.eval({1: False, 2: True}))
        self.assertFalse(expr.eval({1: False, 2: False}))
    
    def test_or_operator(self):
        expr = Expr("OR(1, 2)")
        self.assertTrue(expr.eval({1: True, 2: True}))
        self.assertTrue(expr.eval({1: True, 2: False}))
        self.assertTrue(expr.eval({1: False, 2: True}))
        self.assertFalse(expr.eval({1: False, 2: False}))
    
    def test_xor_operator(self):
        expr = Expr("XOR(1, 2)")
        self.assertFalse(expr.eval({1: True, 2: True}))
        self.assertTrue(expr.eval({1: True, 2: False}))
        self.assertTrue(expr.eval({1: False, 2: True}))
        self.assertFalse(expr.eval({1: False, 2: False}))
    
    def test_nested_expression(self):
        expr = Expr("AND(OR(1, 2), NOT(3))")
        self.assertTrue(expr.eval({1: True, 2: False, 3: False}))
        self.assertFalse(expr.eval({1: False, 2: False, 3: False}))
        self.assertFalse(expr.eval({1: True, 2: True, 3: True}))
    
    def test_complex_expression(self):
        expr = Expr("OR(AND(1, 2), AND(NOT(3), 4))")
        self.assertTrue(expr.eval({1: True, 2: True, 3: False, 4: False}))
        self.assertTrue(expr.eval({1: False, 2: False, 3: False, 4: True}))
        self.assertFalse(expr.eval({1: False, 2: True, 3: True, 4: False}))


class TestCNFFormula(unittest.TestCase):
    """Test CNF formula operations."""
    
    def test_add_clause(self):
        cnf = CNFFormula()
        cid = cnf.add_clause([1, 2, 3])
        self.assertEqual(len(cnf.clauses), 1)
        self.assertIn(cid, cnf.clause_ids)
    
    def test_remove_clause(self):
        cnf = CNFFormula()
        cid = cnf.add_clause([1, 2, 3])
        cnf.remove_clause(cid)
        self.assertEqual(len(cnf.clauses), 0)
        self.assertNotIn(cid, cnf.clause_ids)
    
    def test_rename_var(self):
        cnf = CNFFormula()
        cnf.add_clause([1, -2, 3])
        cnf.add_clause([-1, 2])
        cnf.rename_var(1, 10)
        
        # Check all clauses updated
        self.assertIn([10, -2, 3], cnf.clauses)
        self.assertIn([-10, 2], cnf.clauses)
    
    def test_eliminate_var(self):
        cnf = CNFFormula()
        cnf.eliminate_var(5)
        self.assertIn(5, cnf.eliminated_vars)
    
    def test_get_active_vars(self):
        cnf = CNFFormula()
        cnf.add_clause([1, 2, 3])
        cnf.add_clause([-2, 4])
        active = cnf.get_active_vars()
        self.assertEqual(active, {1, 2, 3, 4})
    
    def test_to_dimacs(self):
        cnf = CNFFormula()
        cnf.add_clause([1, 2])
        cnf.add_clause([-1, 3])
        dimacs = cnf.to_dimacs()
        
        self.assertIn("p cnf", dimacs)
        self.assertIn("1 2 0", dimacs)
        self.assertIn("-1 3 0", dimacs)


class TestSTTFBundleGeneration(unittest.TestCase):
    """Test STTF bundle generation."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_simple_bundle(self):
        gen = STTFBundleGenerator(self.temp_dir)
        gen.set_original_cnf(3, [[1, 2], [-1, 3], [-2, -3]])
        gen.add_var_rename(1, 10)
        gen.write_bundle()
        
        # Check all files exist
        bundle_path = Path(self.temp_dir)
        self.assertTrue((bundle_path / "original.cnf").exists())
        self.assertTrue((bundle_path / "simplified.cnf").exists())
        self.assertTrue((bundle_path / "transform.log").exists())
        self.assertTrue((bundle_path / "reconstruct.map").exists())
        self.assertTrue((bundle_path / "manifest.json").exists())
    
    def test_bundle_loads(self):
        gen = STTFBundleGenerator(self.temp_dir)
        gen.set_original_cnf(3, [[1, 2], [-1, 3]])
        gen.add_var_elim(3, "test")
        gen.write_bundle()
        
        # Load bundle
        bundle = STTFBundle(self.temp_dir)
        self.assertIsNotNone(bundle.manifest_data)
        self.assertGreater(len(bundle.transform_steps), 0)


class TestSTTFReplay(unittest.TestCase):
    """Test replay engine."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_replay_var_rename(self):
        # Create test bundle
        gen = STTFBundleGenerator(self.temp_dir)
        gen.set_original_cnf(3, [[1, 2], [-1, 3]])
        gen.add_var_rename(1, 10)
        gen.write_bundle()
        
        # Replay
        engine = STTFReplayEngine(
            str(Path(self.temp_dir) / "original.cnf"),
            str(Path(self.temp_dir) / "transform.log")
        )
        formula = engine.replay_transformation()
        
        # Check rename applied
        active = formula.get_active_vars()
        self.assertIn(10, active)
        self.assertNotIn(1, active)
    
    def test_replay_var_elim(self):
        gen = STTFBundleGenerator(self.temp_dir)
        gen.set_original_cnf(3, [[1, 2], [-1, 3], [3]])
        gen.add_var_elim(3, "pure")
        gen.add_clause_remove(2, "contains_3")
        gen.add_clause_remove(3, "contains_3")
        gen.write_bundle()
        
        # Replay
        engine = STTFReplayEngine(
            str(Path(self.temp_dir) / "original.cnf"),
            str(Path(self.temp_dir) / "transform.log")
        )
        formula = engine.replay_transformation()
        
        # Variable 3 should be eliminated
        self.assertIn(3, formula.eliminated_vars)


class TestModelLifting(unittest.TestCase):
    """Test model lifting from simplified to original CNF."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_lift_with_rename(self):
        gen = STTFBundleGenerator(self.temp_dir)
        gen.set_original_cnf(3, [[1, 2], [-1, 3]])
        gen.add_var_rename(1, 10)
        gen.write_bundle()
        
        bundle = STTFBundle(self.temp_dir)
        
        # Model for simplified (after rename: vars 10, 2, 3)
        model_B = {10: True, 2: False, 3: True}
        
        # Lift to original
        model_A = bundle.lift_model(model_B)
        
        # Should have mapping 10 -> 1
        self.assertIn(1, model_A)
        self.assertEqual(model_A[1], True)
    
    def test_lift_with_elimination(self):
        gen = STTFBundleGenerator(self.temp_dir)
        gen.set_original_cnf(4, [[1, 2], [-1, 3], [4]])
        gen.add_var_elim(4, "pure")
        gen.write_bundle()
        
        bundle = STTFBundle(self.temp_dir)
        
        # Model for simplified (vars 1, 2, 3)
        model_B = {1: True, 2: False, 3: True}
        
        # Lift to original
        model_A = bundle.lift_model(model_B)
        
        # Should restore variable 4
        self.assertIn(4, model_A)
        self.assertEqual(model_A[4], False)  # Set by elimination rule
    
    def test_lift_with_substitution(self):
        gen = STTFBundleGenerator(self.temp_dir)
        gen.set_original_cnf(4, [[1, 2], [-1, 3], [4]])
        gen.add_var_subst(4, "OR(1, 2)")
        gen.write_bundle()
        
        bundle = STTFBundle(self.temp_dir)
        
        # Model for simplified (vars 1, 2, 3)
        model_B = {1: True, 2: False, 3: False}
        
        # Lift to original
        model_A = bundle.lift_model(model_B)
        
        # Variable 4 should be computed from OR(1, 2)
        self.assertIn(4, model_A)
        self.assertTrue(model_A[4])  # OR(True, False) = True


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_full_pipeline(self):
        """Test: generate -> validate -> replay -> lift"""
        
        # 1. Generate bundle
        gen = STTFBundleGenerator(self.temp_dir)
        gen.set_original_cnf(
            num_vars=5,
            clauses=[
                [1, 2, 3],
                [-1, 4],
                [-2, 5],
                [-3, -4],
                [5]
            ]
        )
        gen.add_var_elim(5, "pure_literal")
        gen.add_clause_remove(3, "contains_5")
        gen.add_clause_remove(5, "unit_5")
        gen.add_var_rename(1, 10)
        gen.write_bundle()
        
        # 2. Load and validate
        bundle = STTFBundle(self.temp_dir)
        self.assertIsNotNone(bundle)
        self.assertEqual(bundle.manifest_data["version"], "1.0")
        
        # 3. Replay transformation
        engine = STTFReplayEngine(
            str(Path(self.temp_dir) / "original.cnf"),
            str(Path(self.temp_dir) / "transform.log")
        )
        formula = engine.replay_transformation()
        self.assertIsNotNone(formula)
        
        # 4. Create and lift a model
        # Simplified has vars: 10, 2, 3, 4 (after elimination and rename)
        model_B = {10: True, 2: False, 3: True, 4: False}
        model_A = bundle.lift_model(model_B)
        
        # Check original variables restored
        self.assertIn(1, model_A)  # Renamed from 10
        self.assertIn(5, model_A)  # Eliminated variable
        
        print(f"✓ Full pipeline test passed")
        print(f"  Model B: {model_B}")
        print(f"  Model A: {model_A}")


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestExpr))
    suite.addTests(loader.loadTestsFromTestCase(TestCNFFormula))
    suite.addTests(loader.loadTestsFromTestCase(TestSTTFBundleGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestSTTFReplay))
    suite.addTests(loader.loadTestsFromTestCase(TestModelLifting))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

