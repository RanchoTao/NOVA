import unittest
from nova.catalog import OPERATORS, load_seeds
from nova.engine import NovaEngine, artifact
from nova.models import IdeaCard


class TestEngine(unittest.TestCase):
    def test_catalog_is_complete(self):
        self.assertGreaterEqual(len(load_seeds()), 6)
        self.assertEqual(len(OPERATORS), 6)

    def test_repeatable_offline_roll_and_diversity(self):
        a = NovaEngine().roll(count=6, seed=123)
        b = NovaEngine().roll(count=6, seed=123)
        self.assertEqual([c.to_dict() for c in a], [c.to_dict() for c in b])
        self.assertEqual(len({c.operator_id for c in a}), 6)
        self.assertEqual(len({c.seed_id for c in a}), 6)
        self.assertEqual(len({c.id for c in a}), 6)

    def test_science_fields_locked(self):
        idea = NovaEngine().roll(seed=3)[0]
        self.assertEqual(idea.novelty_status, "UNCHECKED")
        self.assertEqual(idea.status, "IDEA")
        self.assertEqual(idea.evidence, [])
        self.assertEqual(idea.origin, "template-demo")
        self.assertFalse(artifact([idea])["scientific_evidence"])
        self.assertEqual(idea.to_dict(), IdeaCard.from_dict(idea.to_dict()).to_dict())
        with self.assertRaises(ValueError):
            IdeaCard.from_dict({**idea.to_dict(), "novelty_status": "VERIFIED"})
        with self.assertRaises(ValueError):
            IdeaCard.from_dict({**idea.to_dict(), "status": "SCIENTIFICALLY_VERIFIED"})

    def test_constraints(self):
        engine = NovaEngine()
        for kw in ({"count": 0}, {"count": 21}, {"count": 2, "domain": "nonexistent"},
                   {"count": 1, "operator": "nonexistent"}):
            with self.assertRaises(ValueError):
                engine.roll(**kw)
        result = engine.roll(count=1, domain="computer-vision", operator="causal_inverter", seed=2)
        self.assertEqual(result[0].domain, "computer-vision")
        self.assertEqual(result[0].operator_id, "causal_inverter")

    def test_model_adapter_and_result_validation(self):
        class FakeModel:
            def complete_json(self, system, user):
                self.prompt = user
                return dict(title="候选", question="为何不这样做？", mechanism="因果机制",
                            why_surprising="违背预期", minimal_experiment="执行对照",
                            baseline="相同预算基线", falsifier="反例", confounders=["泄漏", "偏差"])
        model = FakeModel()
        card = NovaEngine(model).roll(count=1, seed=5)[0]
        self.assertEqual(card.origin, "model-unverified")
        self.assertEqual(card.novelty_status, "UNCHECKED")
        self.assertIn("Selected operator", model.prompt)

        class BadModel:
            def complete_json(self, system, user):
                return {"title": "神奇突破"}
        with self.assertRaises(ValueError):
            NovaEngine(BadModel()).roll(count=1, seed=1)


if __name__ == "__main__":
    unittest.main()
