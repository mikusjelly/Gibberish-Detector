import gib_detect

def test():
    good_inputs = [
        'my name is rob and i like to hack',
        'is this thing working?',
        'i hope so',
        'seems okay',
        'yay!',
    ]
    bad_inputs = [
        't2 chhsdfitoixcv',
        'ytjkacvzw',
        'yutthasxcvqer',
        ]
    for inp in good_inputs:
        assert not gib_detect.is_gibberish(inp)
    for inp in bad_inputs:
        assert gib_detect.is_gibberish(inp)
