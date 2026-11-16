import chillycord

from functools import reduce
from operator import or_

def test_permissions_all():
    assert chillycord.Permissions.all().value == reduce(or_, chillycord.Permissions.VALID_FLAGS.values())
