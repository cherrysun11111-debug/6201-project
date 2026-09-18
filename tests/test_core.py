import unittest

from ecrisk.baseline import predict_complaint_type, predict_risk
from ecrisk.data import generate_rows
from ecrisk.model import NaiveBayesRiskModel


class CoreTests(unittest.TestCase):
    def test_data_generation_is_reproducible(self):
        first = generate_rows(5, 123)
        second = generate_rows(5, 123)
        self.assertEqual(first, second)

    def test_baseline_flags_refund_as_high(self):
        self.assertEqual(predict_risk("The seller refused my refund and I may file a chargeback"), "high")

    def test_complaint_type_detection(self):
        complaint_type, terms = predict_complaint_type("Tracking is late and the courier marked it delivered")
        self.assertEqual(complaint_type, "delivery_delay")
        self.assertIn("tracking", terms)

    def test_model_can_fit_and_predict(self):
        rows = generate_rows(60, 6201)
        model = NaiveBayesRiskModel()
        model.fit([r["review_text"] for r in rows], [r["risk"] for r in rows])
        label, confidence, abstain = model.predict("The battery sparked and this may be unsafe")
        self.assertIn(label, {"low", "medium", "high"})
        self.assertGreaterEqual(confidence, 0.0)
        self.assertIsInstance(abstain, bool)


if __name__ == "__main__":
    unittest.main()
