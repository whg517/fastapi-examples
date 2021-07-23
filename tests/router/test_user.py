import pytest
from sqlalchemy.exc import InvalidRequestError



def test_get(
        api_client,
        init_user,
        url_builder,
        assert_status_code_factory,
):
    """"""
    response = api_client.get(url_builder('users'))
    assert_status_code_factory(response)
    assert len(response.json()) == 2


@pytest.mark.parametrize(
    'pk, expect_value',
    [
        (1, None),
        (5, 'a'),
    ]
)
def test_get_by_id(
        api_client,
        init_user,
        url_builder,
        assert_status_code_factory,
        pk,
        expect_value
):
    resource = api_client.get(url_builder(f'users/{pk}'))
    if expect_value:
        pass
    assert_status_code_factory(resource)
    assert resource.json().get('id') == 1
