from pointy.api.add_points import parse_add_points

# TODO hypothesis testing?
valid_add_points = '<@U1234|Alex Lloyd> 10'  # TODO how to run test on list of input: expected response
invalid_add_points = 'U1234|Alex Lloyd 10'

valid_get_score = '<@U1234|Alex Lloyd>'
invalid_get_score = '@username'


def test_valid():
    assert parse_add_points(valid_add_points)


def test_invalid():
    assert not parse_add_points(invalid_add_points)
