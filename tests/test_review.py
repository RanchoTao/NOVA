import unittest
from nova.engine import NovaEngine, artifact
from nova.review import challenge, handoff, select_card


class TestReview(unittest.TestCase):
    def test_challenge_is_never_verified(self):
        card = NovaEngine().roll(count=1, seed=7)[0]
        critique = challenge(card)
        self.assertEqual(critique.scientific_verdict, "UNKNOWN")
        self.assertEqual(critique.status, "PRELIMINARY_CRITIQUE")
        self.assertIn("文献", critique.nearest_neighbor_check)

    def test_handoff_is_inert(self):
        card = NovaEngine().roll(count=1, seed=5)[0]
        proposal = handoff(card)
        self.assertTrue(proposal["review_required"])
        self.assertFalse(proposal["execution_authorized"])
        self.assertFalse(proposal["gpu_authorized"])
        self.assertFalse(proposal["publication_authorized"])
        self.assertEqual(proposal["scientific_verdict"], "UNKNOWN")
        self.assertEqual(proposal["candidate_id"], card.id)

    def test_select_card_requires_explicit_id_for_batch(self):
        cards = NovaEngine().roll(count=3, seed=5)
        data = artifact(cards)
        with self.assertRaisesRegex(ValueError, "--idea-id"):
            select_card(data)
        self.assertEqual(select_card(data, cards[1].id).id, cards[1].id)


if __name__ == "__main__":
    unittest.main()
