from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from predictor.models import Student


class HomePageTests(TestCase):
    def test_root_url_renders_homepage(self):
        response = self.client.get(reverse("predictor:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Placement Predictor")

    def test_legacy_home_url_still_works(self):
        response = self.client.get("/predictor/home/")

        self.assertEqual(response.status_code, 200)


class StudentsPageTests(TestCase):
    def test_students_page_renders_database_records(self):
        Student.objects.create(
            name="Arjun Sharma",
            branch="CSE",
            year=4,
            company_name="TCS",
            package_lpa="7.50",
            status=Student.STATUS_PLACED,
        )

        response = self.client.get(reverse("predictor:students"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Arjun Sharma")
        self.assertContains(response, "4")
        self.assertContains(response, "TCS")
        self.assertContains(response, "CSE")
        self.assertContains(response, "7.50")
        self.assertContains(response, "Placed")

    def test_students_page_shows_empty_state_when_no_records_exist(self):
        response = self.client.get(reverse("predictor:students"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No student records found.")

    def test_students_page_loads_records_from_excel_when_db_is_empty(self):
        response = self.client.get(reverse("predictor:students"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Anuranjan")
        self.assertContains(response, "CSE")


class PredictPageTests(TestCase):
    def test_predict_page_renders_form(self):
        response = self.client.get(reverse("predictor:predict"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Decision Tree Algorithm")
        self.assertContains(response, "Random Forest Classifier Algorithm")

    @patch("predictor.views.result_dt")
    def test_predict_post_dispatches_to_decision_tree(self, mock_result_dt):
        mock_result_dt.return_value = self.client.get(reverse("predictor:predict"))

        response = self.client.post(
            reverse("predictor:predict"),
            {"algorithm": "decision_tree"},
        )

        self.assertEqual(response.status_code, 200)
        mock_result_dt.assert_called_once()

    @patch("predictor.views.result_rfc")
    def test_predict_post_dispatches_to_random_forest(self, mock_result_rfc):
        mock_result_rfc.return_value = self.client.get(reverse("predictor:predict"))

        response = self.client.post(
            reverse("predictor:predict"),
            {"algorithm": "random_forest"},
        )

        self.assertEqual(response.status_code, 200)
        mock_result_rfc.assert_called_once()
