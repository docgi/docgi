from django.test import TestCase

from . import factory_models
from .. import services


class TestDocumentService(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = factory_models.UserFactory()
        cls.workspace = factory_models.WorkspaceFactory(creator=cls.admin)

    def test_get_user_collection(self):
        # admin can access
        factory_models.CollectionFactory(creator=self.admin, workspace=self.workspace)
        factory_models.CollectionFactory(creator=self.admin, workspace=self.workspace)
        factory_models.CollectionFactory(creator=self.admin, workspace=self.workspace)
        factory_models.CollectionFactory(creator=self.admin, workspace=self.workspace, private=True)
        factory_models.CollectionFactory(creator=self.admin, workspace=self.workspace, private=True)
        factory_models.CollectionFactory(workspace=self.workspace)

        # admin can't access
        factory_models.CollectionFactory(workspace=self.workspace, private=True)
        factory_models.CollectionFactory(workspace=self.workspace, private=True)
        factory_models.CollectionFactory(workspace=self.workspace, private=True)

        count_collections_for_admin = services.get_user_collections(
            user=self.admin,
            workspace=self.workspace
        ).count()
        self.assertEqual(count_collections_for_admin, 6)

    def test_get_user_collection_same_user_mix_workspace(self):
        diff_workspace = factory_models.WorkspaceFactory(creator=self.admin)

        factory_models.CollectionFactory(creator=self.admin, workspace=self.workspace)
        factory_models.CollectionFactory(creator=self.admin, workspace=self.workspace, private=True)
        factory_models.CollectionFactory(creator=self.admin, workspace=self.workspace, private=True)
        factory_models.CollectionFactory(workspace=self.workspace)

        factory_models.CollectionFactory(creator=self.admin, workspace=diff_workspace)
        factory_models.CollectionFactory(creator=self.admin, workspace=diff_workspace)

        count_collections_for_admin_in_main_workspace = services.get_user_collections(
            user=self.admin,
            workspace=self.workspace
        ).count()
        self.assertEqual(count_collections_for_admin_in_main_workspace, 4)

        count_collections_for_admin_in_diff_workspace = services.get_user_collections(
            user=self.admin,
            workspace=diff_workspace
        ).count()
        self.assertEqual(count_collections_for_admin_in_diff_workspace, 2)

    def test_get_user_documents(self):
        col = factory_models.CollectionFactory(creator=self.admin, workspace=self.workspace)
        factory_models.DocumentFactory(collection=col, creator=self.admin, draft=False)
        factory_models.DocumentFactory(collection=col, creator=self.admin, draft=False)
        factory_models.DocumentFactory(collection=col, creator=self.admin, draft=True)

        diff_user = factory_models.UserFactory()
        diff_col = factory_models.CollectionFactory(creator=diff_user, workspace=self.workspace)
        factory_models.DocumentFactory(collection=diff_col, creator=diff_user, draft=False)
        factory_models.DocumentFactory(collection=diff_col, creator=diff_user, draft=False)
        factory_models.DocumentFactory(collection=diff_col, creator=diff_user, draft=True)

        private_col_of_diff_user = factory_models.CollectionFactory(creator=diff_user, workspace=self.workspace,
                                                                    private=True)
        factory_models.DocumentFactory(collection=private_col_of_diff_user, creator=diff_user, draft=False)
        factory_models.DocumentFactory(collection=private_col_of_diff_user, creator=diff_user, draft=False)
        factory_models.DocumentFactory(collection=private_col_of_diff_user, creator=diff_user, draft=True)

        count_document_for_admin = services.get_user_documents(user=self.admin,
                                                               workspace=self.workspace).count()
        self.assertEqual(count_document_for_admin, 5)

        count_document_for_diff_user = services.get_user_documents(user=diff_user,
                                                                   workspace=self.workspace).count()
        self.assertEqual(count_document_for_diff_user, 8)
