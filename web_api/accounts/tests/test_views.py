from fastapi import status
from syrupy.filters import props

from web_api.accounts.dependencies.usecases import get_account_session_id_generator
from web_api.accounts.repositories import AccountRepository
from web_api.accounts.tests.factories.repositories import AccountRepositoryFactory
from web_api.accounts.tests.factories.usecases import (
    AccountRegisterUseCaseFactory,
    AccountSessionInteractorFactory,
)
from web_api.accounts.tests.factories.values import (
    AccountValueFactory,
    AuthenticationCredentialsValueFactory,
    RegistrationCredentialsValueFactory,
)


def get_dummy_session_id():
    return 'session_id'


async def test_register(client, app, reverse_route, snapshot):
    app.dependency_overrides[get_account_session_id_generator] = lambda: get_dummy_session_id

    registration_credentials = RegistrationCredentialsValueFactory()
    response = await client.post(reverse_route('register'), json=registration_credentials.dict())

    assert dict(response.cookies) == snapshot
    assert response.status_code == status.HTTP_200_OK


async def test_register_duplicate_username(
    client, app, reverse_route, snapshot,
):
    app.dependency_overrides[get_account_session_id_generator] = lambda: get_dummy_session_id

    test_username = 'test username'

    account_repository = AccountRepositoryFactory()
    account_value = AccountValueFactory(username=test_username)

    await account_repository.add(account_value_list=[account_value])

    registration_credentials = RegistrationCredentialsValueFactory(username=test_username)
    response = await client.post(reverse_route('register'), json=registration_credentials.dict())

    assert response.json() == snapshot(exclude=props('id_', 'created_at'))
    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_authenticate(client, app, reverse_route, snapshot):
    app.dependency_overrides[get_account_session_id_generator] = lambda: get_dummy_session_id

    password = 'test_password'
    username = 'test_username'

    registration_credentials = RegistrationCredentialsValueFactory(
        username=username, password1=password, password2=password,
    )
    account_register_use_case = AccountRegisterUseCaseFactory(
        account_session_interactor=await AccountSessionInteractorFactory(),
    )

    await account_register_use_case.register(registration_credentials=registration_credentials)

    authentication_credentials = AuthenticationCredentialsValueFactory(
        username=username, password=password,
    )
    response = await client.post(
        reverse_route('authenticate'), json=authentication_credentials.dict(),
    )

    assert dict(response.cookies) == snapshot
    assert response.status_code == status.HTTP_200_OK


async def test_profile(client, reverse_route, snapshot):
    account_repository: AccountRepository = AccountRepositoryFactory()
    account_session_interactor = await AccountSessionInteractorFactory()

    account_entities = await account_repository.add(
        account_value_list=[AccountValueFactory(username='test username')],
    )
    account_session_entity = await account_session_interactor.add(
        account_entity=account_entities[0],
    )

    response = await client.get(
        reverse_route('profile'),
        cookies={'authentication_token': account_session_entity.token.value},
    )

    assert response.json() == snapshot(exclude=props('created_at', 'id_'))
    assert response.status_code == status.HTTP_200_OK
