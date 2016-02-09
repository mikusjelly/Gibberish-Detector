from __future__ import print_function, division
import argparse
import json
import math
import os.path


default_model_path = os.path.join(os.path.dirname(__file__), 'en_model.json')
default_accepted_chars = 'abcdefghijklmnopqrstuvwxyz '
_default_model = None


def is_gibberish(l, model=None):
    """ Return True if texts is gibberish, False if not.
    """
    if model is None:
        model = get_default_model()
    return avg_transition_prob(l, model) < model['threshold']


def train(line_iter, good_inputs, bad_inputs,
        accepted_chars=default_accepted_chars):
    """ Train model.
    :param line_iter: Line iterator with normal texts (should be big!).
    :param good_inputs: A number of good inputs
    (to estimate gibberish threshold).
    :param bad_inputs: A similar iterator with bad inputs (gibberish).
    :param accepted_chars: Include only this characters.
    :returns: Trained model, suitable to passing into is_gibberish.
    """

    k = len(accepted_chars)
    # Assume we have seen 10 of each character pair.  This acts as a kind of
    # prior or smoothing factor.  This way, if we see a character transition
    # live that we've never observed in the past, we won't assume the entire
    # string has 0 probability.
    counts = [[10 for _ in range(k)] for _ in range(k)]

    # Count transitions from big text file
    pos = dict((char, idx) for idx, char in enumerate(accepted_chars))
    for line in line_iter:
        for a, b in _ngram(2, line, accepted_chars):
            counts[pos[a]][pos[b]] += 1

    # Normalize the counts so that they become log probabilities.
    # We use log probabilities rather than straight probabilities to avoid
    # numeric underflow issues with long texts.
    # This contains a justification:
    # http://squarecog.wordpress.com/2009/01/10/dealing-with-underflow-in-joint-probability-calculations/
    for row in counts:
        s = float(sum(row))
        for j in range(len(row)):
            row[j] = math.log(row[j] / s)

    model = {
        'log_prob_mat': counts,
        'accepted_chars': accepted_chars,
        'pos': pos,
    }

    # Find the probability of generating a few arbitrarily choosen good and
    # bad phrases.
    good_probs = [avg_transition_prob(l, model) for l in good_inputs]
    bad_probs = [avg_transition_prob(l, model) for l in bad_inputs]

    # Assert that we actually are capable of detecting the junk.
    assert min(good_probs) > max(bad_probs)

    # And pick a threshold halfway between the worst good and best bad inputs.
    model['threshold'] = (min(good_probs) + max(bad_probs)) / 2

    return model


def avg_transition_prob(l, model=None):
    """ Return the average transition prob from l through log_prob_mat.
    """
    if model is None:
        model = get_default_model()
    log_prob = 1.0
    transition_ct = 0
    log_prob_mat = model['log_prob_mat']
    pos = model['pos']
    for a, b in _ngram(2, l, model['accepted_chars']):
        log_prob += log_prob_mat[pos[a]][pos[b]]
        transition_ct += 1
    # The exponentiation translates from log probs to probs.
    return math.exp(log_prob / (transition_ct or 1))


def get_default_model():
    global _default_model
    if _default_model is None:
        with open(default_model_path) as f:
            _default_model = json.load(f)
    return _default_model


def train_cli():
    parser = argparse.ArgumentParser()
    arg = parser.add_argument
    arg('texts', help='big file with texts')
    arg('good_inputs', help='file with good examples')
    arg('bad_inputs', help='file with bad examples')
    arg('output', help='file to save the model to')
    arg('--accepted-chars', default=default_accepted_chars)
    args = parser.parse_args()
    model = train(
        open(args.texts), open(args.good_inputs), open(args.bad_inputs),
        accepted_chars=args.accepted_chars)
    with open(args.output, 'w') as f:
        json.dump(model, f)


def _normalize(line, accepted_chars):
    """ Return only the subset of chars from accepted_chars.
    This helps keep the  model relatively small by ignoring punctuation,
    infrequenty symbols, etc.
    """
    return [c.lower() for c in line if c.lower() in accepted_chars]


def _ngram(n, l, accepted_chars):
    """ Return all n grams from l after normalizing.
    """
    filtered = _normalize(l, accepted_chars)
    for start in range(0, len(filtered) - n + 1):
        yield ''.join(filtered[start:start + n])
