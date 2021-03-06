import secrets

import factory
from passlib.hash import bcrypt  # type: ignore

from web_api.accounts.tests.factories.repositories import (
    AccountRepositoryFactory,
    AccountSessionRepositoryFactory,
)
from web_api.accounts.usecases import AccountRegisterUseCase, AccountSessionInteractor
from web_api.commons.tests.factories import AsyncFactory, BaseFactory


class AccountSessionInteractorFactory(
    BaseFactory[AccountSessionInteractor], AsyncFactory,
):
    class Meta:
        model = AccountSessionInteractor

    account_session_repository = factory.SubFactory(AccountSessionRepositoryFactory)
    generate_user_session_id = factory.LazyFunction(lambda: secrets.token_hex)


class AccountRegisterUseCaseFactory(BaseFactory[AccountRegisterUseCase]):
    class Meta:
        model = AccountRegisterUseCase

    user_repository = factory.SubFactory(AccountRepositoryFactory)
    hasher = factory.LazyFunction(lambda: bcrypt)
