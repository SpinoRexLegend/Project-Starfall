import json
import unittest
from unittest.mock import patch

import RiskAssessor


class RiskAssessorTest(unittest.TestCase):

    def test_kinetic_energy_uses_spherical_mass_and_half_mv_squared(self):
        with patch.dict("os.environ", {}, clear=True):
            result = RiskAssessor.perform_assessment(
                "AST-1",
                0.01,
                20.0,
                "Iron",
                1.0,
                10_000.0
            )

        self.assertAlmostEqual(0.195223, result["kineticEnergyMT"], places=6)
        self.assertAlmostEqual(8.1681409e14, result["kineticEnergyJoules"], delta=1e7)
        self.assertAlmostEqual(4_084_070.45, result["estimatedMassKg"], places=2)
        self.assertEqual(7_800.0, result["materialDensityKgM3"])
        self.assertEqual("E = 0.5 * m * v^2", result["kineticEnergyFormula"])

        raw_response = json.loads(result["rawResponse"])
        self.assertEqual(7_800.0, raw_response["material_density_kg_m3"])

    def test_density_assumptions_are_runtime_configurable(self):
        with patch.dict("os.environ", {
            "ASTEROID_DENSITY_METALLIC_KG_M3": "8000"
        }, clear=True):
            self.assertEqual(8_000.0, RiskAssessor.material_density_kg_m3("metallic"))


if __name__ == "__main__":
    unittest.main()
