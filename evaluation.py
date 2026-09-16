"""Offline STT scoring. No audio, credentials, model downloads, or API calls."""
import argparse
import csv
import json


def edit_distance(reference, hypothesis):
    previous = list(range(len(hypothesis) + 1))
    for i, expected in enumerate(reference, 1):
        current = [i]
        for j, actual in enumerate(hypothesis, 1):
            current.append(min(current[-1] + 1, previous[j] + 1,
                               previous[j - 1] + (expected != actual)))
        previous = current
    return previous[-1]


def score_transcript(reference, hypothesis):
    """Return WER/CER; blank references cannot define an error-rate denominator.

    Collapse whitespace, preserve case/punctuation, include spaces in CER.
    Empty hypotheses count as complete deletions instead of being dropped.
    """
    if not isinstance(reference, str) or not isinstance(hypothesis, str):
        raise ValueError('reference and hypothesis must be strings')
    reference = ' '.join(reference.split())
    hypothesis = ' '.join(hypothesis.split())
    if not reference:
        raise ValueError('reference must contain text')
    words = reference.split()
    return {
        'WER': edit_distance(words, hypothesis.split()) / len(words),
        'CER': edit_distance(reference, hypothesis) / len(reference),
    }


def evaluate_rows(rows):
    """Macro mean over valid references, with every exclusion counted."""
    scores = []
    total = empty_reference = empty_hypothesis = 0
    for row in rows:
        total += 1
        reference, hypothesis = row['gt_text'], row['pred_text']
        if not isinstance(reference, str) or not isinstance(hypothesis, str):
            raise ValueError('CSV text fields must be present')
        if not reference.strip():
            empty_reference += 1
            continue
        if not hypothesis.strip():
            empty_hypothesis += 1
        scores.append(score_transcript(reference, hypothesis))
    if not scores:
        raise ValueError('no non-empty references to evaluate')
    return {
        'rows': total, 'evaluated': len(scores),
        'excluded_empty_reference': empty_reference,
        'empty_hypothesis': empty_hypothesis,
        'aggregation': 'macro_mean_per_record',
        'WER': sum(s['WER'] for s in scores) / len(scores),
        'CER': sum(s['CER'] for s in scores) / len(scores),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_path', help='UTF-8 CSV with gt_text,pred_text columns')
    args = parser.parse_args()
    try:
        with open(args.csv_path, encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            if not {'gt_text', 'pred_text'} <= set(reader.fieldnames or []):
                raise ValueError('required columns: gt_text,pred_text')
            result = evaluate_rows(reader)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'Evaluation failed: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
