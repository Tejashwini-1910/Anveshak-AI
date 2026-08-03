import unittest
from unittest.mock import patch
from anveshak.agents import Paper
from anveshak.pipeline import ResearchPipeline

class PipelineTest(unittest.TestCase):
    @patch("anveshak.agents.LiteratureRetrievalAgent.search")
    def test_pipeline_returns_explainable_report(self, search):
        search.return_value = ([Paper("Smart infrastructure innovation", "A. Researcher", 2025, "Journal", "Innovation infrastructure evaluation", 10, "https://example.org", "Test")], ["Test"])
        report = ResearchPipeline().run("How can AI improve resilient infrastructure?")
        self.assertEqual(len(report["progress"]), 10)
        self.assertIn("overall_confidence", report["verification"])

if __name__ == "__main__": unittest.main()
