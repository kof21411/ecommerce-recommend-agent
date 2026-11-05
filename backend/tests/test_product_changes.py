import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from api.product_routes import deactivate_product, delete_product, update_product
from schemas import ProductUpdateRequest


class ProductChangeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.product = SimpleNamespace(id=uuid4(), status="active", name="old", price=1, stock=1)
        self.db = SimpleNamespace(get=AsyncMock(return_value=self.product), commit=AsyncMock())

    async def test_update_commits_before_index(self):
        async def check(product):
            self.db.commit.assert_awaited_once()
            self.assertEqual(product.name, "new")
        with patch("api.product_routes.index_product", side_effect=check):
            response = await update_product(self.product.id, ProductUpdateRequest(name="new"), None, self.db)
        self.assertEqual(response.data["index_status"], "indexed")

    async def test_deactivate_and_delete_keep_db_change_on_index_failure(self):
        with patch("api.product_routes.delete_product_index", new=AsyncMock(side_effect=RuntimeError("unavailable"))):
            response = await deactivate_product(self.product.id, None, self.db)
            self.assertEqual(self.product.status, "inactive")
            self.assertEqual(response.data["index_status"], "failed")
            response = await delete_product(self.product.id, None, self.db)
            self.assertEqual(self.product.status, "deleted")
            self.assertEqual(response.data["index_status"], "failed")
