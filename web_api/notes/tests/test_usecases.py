from fastapi.encoders import jsonable_encoder
from syrupy.filters import props

from web_api.accounts.entities import AccountEntity
from web_api.accounts.tests.factories.repositories import AccountRepositoryFactory
from web_api.accounts.tests.factories.values import AccountValueFactory
from web_api.notes.tests import factories


async def get_account_entity() -> AccountEntity:
    account_value = AccountValueFactory()
    account_repository = AccountRepositoryFactory()

    account_entities = await account_repository.add(account_value_list=[account_value])

    return account_entities[0]


class TestNoteInteractor:
    async def test_add_get(self, snapshot) -> None:
        # Given
        account_entity = await get_account_entity()
        note_list = factories.NoteValueFactory.create_batch(3)
        # And
        interactor = factories.NoteInteractorFactory()
        # When
        await interactor.add(
            account_entity=account_entity, note_value_list=note_list,
        )
        note_entity_list = await interactor.get(
            account_entity=account_entity,
            paging=factories.PagingFactory(),
            ordering=factories.NoteOrderingFactory(),
            tag_value_list=[],
        )
        # Then
        assert jsonable_encoder(note_entity_list) == snapshot(exclude=props('id_', 'created_at'))

    async def test_get_by_tags(self, snapshot) -> None:
        # Given
        account_entity = await get_account_entity()
        search_tag = factories.TagValueFactory(name='search tag')
        note_list = []
        note_list.append(factories.NoteValueFactory())
        note_list.append(factories.NoteValueFactory(tags=[search_tag]))
        # And
        interactor = factories.NoteInteractorFactory()
        # When
        await interactor.add(
            account_entity=account_entity, note_value_list=note_list,
        )
        note_entity_list = await interactor.get(
            account_entity=account_entity,
            paging=factories.PagingFactory(),
            ordering=factories.NoteOrderingFactory(),
            tag_value_list=[search_tag],
        )
        # Then
        assert len(note_entity_list) == 1
        assert note_entity_list[0].tags == [search_tag]

    async def test_update(self) -> None:
        # Given
        account_entity = await get_account_entity()
        interactor = factories.NoteInteractorFactory()
        note_list = factories.NoteValueFactory.create_batch(3)
        entity_list = await interactor.add(
            account_entity=account_entity, note_value_list=note_list,
        )
        # When
        entity_list[0].text = 'New text'
        await interactor.update(
            account_entity=account_entity, note_entity_list=entity_list,
        )
        entity_list = await interactor.get(
            account_entity=account_entity,
            paging=factories.PagingFactory(),
            ordering=factories.NoteOrderingFactory(),
            tag_value_list=[],
        )
        # Then
        assert entity_list[0].text == 'New text'

    async def test_delete(self) -> None:
        # Given
        interactor = factories.NoteInteractorFactory()
        # And
        account_entity = await get_account_entity()
        note_list = factories.NoteValueFactory.create_batch(3)
        entity_list = await interactor.add(
            account_entity=account_entity, note_value_list=note_list,
        )
        # Ensure:
        note_entity_list = await interactor.get(
            account_entity=account_entity,
            paging=factories.PagingFactory(),
            ordering=factories.NoteOrderingFactory(),
            tag_value_list=[],
        )
        assert note_entity_list != []

        # When
        await interactor.delete(
            account_entity=account_entity, note_entity_list=entity_list,
        )
        # Then
        note_entity_list = await interactor.get(
            account_entity=account_entity,
            paging=factories.PagingFactory(),
            ordering=factories.NoteOrderingFactory(),
            tag_value_list=[],
        )
        assert note_entity_list == []


async def test_add_welcome_note(snapshot) -> None:
    # Given: account with no notes.
    account_entity = await get_account_entity()

    # When: add welcome note usecase is called.
    add_welcome_note_usecase = factories.AddWelcomeNoteUsecaseFactory()
    await add_welcome_note_usecase.add_welcome_note(account_entity=account_entity)

    # Then: welcome note is created.
    note_interactor = factories.NoteInteractorFactory()
    account_note_entity_list = await note_interactor.get(
        account_entity=account_entity,
        paging=factories.PagingFactory(),
        ordering=factories.NoteOrderingFactory(),
        tag_value_list=[],
    )

    assert len(account_note_entity_list) == 1
    assert account_note_entity_list[0] == snapshot(exclude=props('created_at', 'id_'))
