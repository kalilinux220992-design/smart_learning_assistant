import json
import os
import tempfile

from django.test import SimpleTestCase, override_settings
from django.urls import reverse


class WatchStatsTests(SimpleTestCase):
    def test_converter_page_is_available(self):
        response = self.client.get(reverse('converter_home'))
        self.assertEqual(response.status_code, 200)

    def test_placement_predictor_page_is_available(self):
        response = self.client.get(reverse('predictor:home'))
        self.assertEqual(response.status_code, 200)

    def test_post_and_get_watch_stats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, 'watch_stats.json')

            with override_settings(WATCH_STATS_FILE=stats_file):
                payload = {
                    'total_seconds': 7200,
                    'categories': {
                        'news': 1800,
                        'lectures': 3600,
                        'entertainment': 1800,
                    },
                }

                response = self.client.post(
                    reverse('watch_stats_api'),
                    data=json.dumps(payload),
                    content_type='application/json',
                )

                self.assertEqual(response.status_code, 200)
                self.assertTrue(os.path.exists(stats_file))

                with open(stats_file, 'r', encoding='utf-8') as handle:
                    saved = json.load(handle)

                today_key = self.client.get(reverse('watch_stats_page')).context['date']
                self.assertEqual(saved[today_key]['categories']['lectures'], 3600)

                page_response = self.client.get(reverse('watch_stats_page'))
                self.assertContains(page_response, 'Lectures')
                self.assertContains(page_response, 'Minutes')
                self.assertContains(page_response, '500')

    def test_options_request_returns_cors_headers(self):
        response = self.client.options(
            reverse('watch_stats_api'),
            content_type='application/json',
            HTTP_ORIGIN='chrome-extension://abc123',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS='content-type',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Origin'], 'chrome-extension://abc123')
        self.assertIn('POST', response['Access-Control-Allow-Methods'])

    def test_clear_today_watch_stats_preserves_other_days(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stats_file = os.path.join(tmpdir, 'watch_stats.json')
            today_key = self.client.get(reverse('watch_stats_page')).context['date']
            with open(stats_file, 'w', encoding='utf-8') as handle:
                json.dump({
                    today_key: {'total_seconds': 120, 'categories': {'coding': 120}},
                    '2000-01-01': {'total_seconds': 60, 'categories': {'news': 60}},
                }, handle)

            with override_settings(WATCH_STATS_FILE=stats_file):
                response = self.client.post(reverse('clear_today_watch_stats'))

            self.assertRedirects(response, reverse('watch_stats_page'))
            with open(stats_file, 'r', encoding='utf-8') as handle:
                saved = json.load(handle)
            self.assertNotIn(today_key, saved)
            self.assertIn('2000-01-01', saved)
