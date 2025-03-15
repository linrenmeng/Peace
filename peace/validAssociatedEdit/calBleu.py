import math
from collections import Counter

def n_grams(sequence, n):
    """Generate n-grams from a sequence."""
    return [tuple(sequence[i:i+n]) for i in range(len(sequence)-n+1)]

def compute_bleu(reference, candidate, max_n=4):
    """
    Compute the BLEU score between a reference and candidate sequence.

    Args:
        reference (str): The reference text.
        candidate (str): The generated candidate text.
        max_n (int): The maximum n-gram order to consider (default: 4).

    Returns:
        float: The BLEU score.
    """

    # Ensure input is valid
    if not reference or not candidate:
        raise ValueError("Both reference and candidate texts must be non-empty.")

    reference_tokens = reference.split()
    candidate_tokens = candidate.split()

    # Compute n-gram precision
    precision_scores = []
    for n in range(1, max_n + 1):
        reference_ngrams = Counter(n_grams(reference_tokens, n))
        candidate_ngrams = Counter(n_grams(candidate_tokens, n))

        # Count overlapping n-grams
        overlap = sum(min(candidate_ngrams[ngram], reference_ngrams[ngram]) for ngram in candidate_ngrams)
        total_ngrams = sum(candidate_ngrams.values())

        # Compute precision (avoid division by zero)
        if total_ngrams > 0:
            precision = overlap / total_ngrams
        else:
            precision = 0
        
        precision_scores.append(precision)

    # Compute brevity penalty
    c = len(candidate_tokens)
    r = len(reference_tokens)
    
    bp = math.exp(1 - r / c) if c > 0 and c < r else 1

    # Compute BLEU score (geometric mean of precision scores)
    precision_log_sum = sum(math.log(p) for p in precision_scores if p > 0)
    
    if precision_log_sum == 0:
        bleu_score = 0
    else:
        bleu_score = bp * math.exp(precision_log_sum / max_n)

    return bleu_score


# Example Usage
if __name__ == "__main__":
    reference_text = """@@ -388,6 +388,7 @@ def handle_parameter_change(self):
    
    def pg_control_timeline(self):
        try:
+
            return int(self.controldata().get("Latest checkpoint's TimeLineID"))
        except (TypeError, ValueError):
            logger.exception('Failed to parse timeline from pg_controldata output')"""
    
    candidate_text = """@@ -1283,6 +1283,7 @@ def post_bootstrap(self):
        if not self.watchdog.activate():
            logger.error('Cancelling bootstrap because watchdog activation failed')
            self.cancel_initialization()
+        self._rewind.ensure_checkpoint_after_promote(self.wakeup)
        self.dcs.initialize(create_new=(self.cluster.initialize is None), sysid=self.state_handler.sysid)
        self.dcs.set_config_value(json.dumps(self.patroni.config.dynamic_configuration, separators=(',', ':')))
        self.dcs.take_leader()"""

    try:
        bleu_score = compute_bleu(reference_text, candidate_text)
        print(f"BLEU Score: {bleu_score:.4f}")
    except ValueError as e:
        print(f"Error: {e}")
