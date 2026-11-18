import sys
import unittest
from pathlib import Path

# let the tests use the modules in src/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from matcher import match_jobs
from resume_reader import clean_text


class UnitTests(unittest.TestCase):

    def test_unit1_clean_text_removes_personal_info(self):
        """Unit test 1: clean_text removes name, email, phone and link, and keeps the skills."""
        raw = "Jane Doe | jane@mail.com | (618) 555-1234 | linkedin.com/in/jane\nSkills: C++, Python"
        text = clean_text(raw)

        # personal info is gone
        self.assertNotIn("jane", text)
        self.assertNotIn("@", text)
        self.assertNotIn("555", text)
        self.assertNotIn("linkedin", text)

        # skills are kept, lowercase, symbols removed (c++ stays)
        self.assertEqual(text, "skills c++ python")

    def test_unit2_best_match_ranks_first(self):
        """Unit test 2: match_jobs ranks the job closest to the resume first."""
        resume = "python sql developer"
        jobs = [
            {"title": "Sales Associate", "description": "retail sales, customer service and cash register"},
            {"title": "Python Developer", "description": "we need a python developer who knows sql"},
        ]
        ranked = match_jobs(resume, jobs)

        # best match first, with a higher score
        self.assertEqual(ranked[0]["title"], "Python Developer")
        self.assertGreater(ranked[0]["score"], ranked[1]["score"])

        # skills found in both texts
        self.assertEqual(ranked[0]["skills"], ["python", "sql"])


# run: python -m unittest discover tests -v
if __name__ == "__main__":
    unittest.main(verbosity=2)
