import unittest
from evaluation import evaluate_rows, score_transcript


class EvaluationTests(unittest.TestCase):
    def test_exact_korean_match(self):
        self.assertEqual(score_transcript('오늘 기분이 좋아요', '오늘 기분이 좋아요'), {'WER': 0, 'CER': 0})

    def test_empty_transcription_is_complete_deletion(self):
        self.assertEqual(score_transcript('오늘 기분이 좋아요', ''), {'WER': 1, 'CER': 1})

    def test_failed_transcription_is_not_dropped_from_average(self):
        result = evaluate_rows([{'gt_text': '안녕', 'pred_text': '안녕'},
                                {'gt_text': '안녕', 'pred_text': ''}])
        self.assertEqual(result['WER'], 0.5)
        self.assertEqual(result['evaluated'], 2)
        self.assertEqual(result['empty_hypothesis'], 1)

    def test_missing_reference_is_counted_separately(self):
        result = evaluate_rows([{'gt_text': '', 'pred_text': '안녕'},
                                {'gt_text': '안녕', 'pred_text': '안녕'}])
        self.assertEqual(result['excluded_empty_reference'], 1)
        self.assertEqual(result['rows'], 2)
        self.assertEqual(result['evaluated'], 1)

    def test_no_valid_reference_is_not_a_zero_error_success(self):
        with self.assertRaises(ValueError):
            evaluate_rows([{'gt_text': '  ', 'pred_text': '안녕'}])

    def test_insertions_can_exceed_one(self):
        self.assertEqual(score_transcript('a', 'a b c')['WER'], 2)

    def test_whitespace_policy(self):
        self.assertEqual(score_transcript('오늘  기분', '오늘\n기분')['CER'], 0)

    def test_truncated_record_fails(self):
        with self.assertRaises(ValueError):
            evaluate_rows([{'gt_text': '안녕', 'pred_text': None}])


if __name__ == '__main__':
    unittest.main()
