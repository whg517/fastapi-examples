import pytest


# @pytest.mark.asyncio
def test_get(api_client, init_user):
    """"""
    res = api_client.get('/')
    print(res.text)
