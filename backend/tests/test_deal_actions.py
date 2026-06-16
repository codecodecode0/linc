import unittest

from fastapi.testclient import TestClient

from app import deps
from app.config import get_settings
from app.main import app


def reset_state():
    for fn in (
        get_settings,
        deps.get_creator_repository,
        deps.get_brand_repository,
        deps.get_otp_repository,
        deps.get_connection_repository,
        deps.get_state_repository,
        deps.get_catalog_repository,
        deps.get_registry,
        deps.get_creator_service,
        deps.get_account_service,
        deps.get_token_service,
        deps.get_auth_service,
        deps.get_campaign_service,
        deps.get_deal_service,
        deps.get_content_service,
        deps.get_license_service,
        deps.get_payout_account_service,
        deps.get_payment_method_service,
    ):
        fn.cache_clear()


def login(client: TestClient, account_type: str, email: str) -> dict:
    response = client.post(
        "/api/auth/otp/verify",
        json={
            "channel": "email",
            "value": email,
            "code": "000000",
            "accountType": account_type,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def create_offered_deal(client: TestClient, brand_session: dict) -> dict:
    campaign_response = client.post(
        f"/api/brands/{brand_session['accountId']}/campaigns",
        json={
            "name": "Glow Serum Launch",
            "objective": "conversions",
            "productCategory": "skincare",
            "budgetAmount": 150000,
        },
    )
    assert campaign_response.status_code == 201, campaign_response.text
    campaign = campaign_response.json()

    deal_response = client.post(
        f"/api/campaigns/{campaign['id']}/deals",
        json={
            "creatorId": "1",
            "type": "real_video",
            "status": "offered",
            "quoteAmount": 90000,
            "brief": {"campaign": campaign["name"], "productCategory": "skincare"},
            "deliverables": [
                {
                    "title": "Launch reel",
                    "type": "real_video",
                    "quantity": 1,
                    "notes": "Creator video with usage-ready edit",
                }
            ],
        },
    )
    assert deal_response.status_code == 201, deal_response.text
    return deal_response.json()


class DealActionTests(unittest.TestCase):
    def setUp(self):
        reset_state()
        self.client = TestClient(app)

    def test_creator_counter_blocks_creator_accept_until_brand_acts(self):
        brand = login(self.client, "brand", "state-brand@example.com")
        creator = login(self.client, "creator", "maya@example.com")
        deal = create_offered_deal(self.client, brand)

        counter = self.client.post(
            f"/api/deals/{deal['id']}/actions",
            headers={"Authorization": f"Bearer {creator['token']}"},
            json={"action": "negotiate", "quoteAmount": 95000},
        )
        self.assertEqual(counter.status_code, 200, counter.text)
        countered = counter.json()
        self.assertEqual(countered["status"], "countered")
        self.assertEqual(countered["lastOfferBy"], "creator")
        self.assertEqual(countered["quoteAmount"], 95000)
        self.assertEqual(countered["deliverables"][0]["title"], "Launch reel")

        creator_accept = self.client.post(
            f"/api/deals/{deal['id']}/actions",
            headers={"Authorization": f"Bearer {creator['token']}"},
            json={"action": "accept"},
        )
        self.assertEqual(creator_accept.status_code, 409)
        self.assertIn("latest brand offer", creator_accept.json()["detail"])

        brand_accept = self.client.post(
            f"/api/deals/{deal['id']}/actions",
            headers={"Authorization": f"Bearer {brand['token']}"},
            json={"action": "accept"},
        )
        self.assertEqual(brand_accept.status_code, 200, brand_accept.text)
        self.assertEqual(brand_accept.json()["status"], "accepted")

    def test_brand_revision_reopens_offer_for_creator_acceptance(self):
        brand = login(self.client, "brand", "revision-brand@example.com")
        creator = login(self.client, "creator", "maya@example.com")
        deal = create_offered_deal(self.client, brand)

        counter = self.client.post(
            f"/api/deals/{deal['id']}/actions",
            headers={"Authorization": f"Bearer {creator['token']}"},
            json={"action": "negotiate", "quoteAmount": 95000},
        )
        self.assertEqual(counter.status_code, 200, counter.text)

        revision = self.client.post(
            f"/api/deals/{deal['id']}/actions",
            headers={"Authorization": f"Bearer {brand['token']}"},
            json={"action": "revise_offer", "quoteAmount": 97000},
        )
        self.assertEqual(revision.status_code, 200, revision.text)
        revised = revision.json()
        self.assertEqual(revised["status"], "offered")
        self.assertEqual(revised["lastOfferBy"], "brand")
        self.assertEqual(revised["quoteAmount"], 97000)

        accepted = self.client.post(
            f"/api/deals/{deal['id']}/actions",
            headers={"Authorization": f"Bearer {creator['token']}"},
            json={"action": "accept"},
        )
        self.assertEqual(accepted.status_code, 200, accepted.text)
        self.assertEqual(accepted.json()["status"], "accepted")


if __name__ == "__main__":
    unittest.main()
