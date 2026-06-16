"""Deal CRUD (a campaign ↔ creator booking).

  POST/GET   /api/campaigns/{campaign_id}/deals
  GET/PATCH/DELETE  /api/deals/{deal_id}
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException

from ..deps import (
    get_auth_service,
    get_campaign_service,
    get_creator_service,
    get_deal_service,
)
from ..models import (
    AccountType,
    Campaign,
    Deal,
    DealAction,
    DealActionType,
    DealActor,
    DealCreate,
    DealEvent,
    DealStatus,
    DealUpdate,
    Session,
)
from ..services import AuthService, CreatorNotFound, CreatorService, CrudService, NotFound

router = APIRouter(tags=["deals"])

TERMINAL_STATUSES = {
    DealStatus.rejected,
    DealStatus.withdrawn,
    DealStatus.completed,
    DealStatus.cancelled,
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _session_from_header(authorization: str, auth: AuthService) -> Optional[Session]:
    token = authorization[7:] if authorization.lower().startswith("bearer ") else ""
    return auth.account_from_token(token) if token else None


def _actor_from_session(session: Optional[Session], fallback: Optional[DealActor]) -> DealActor:
    if session:
        return (
            DealActor.creator
            if session.account_type == AccountType.creator
            else DealActor.brand
        )
    if fallback:
        return fallback
    raise HTTPException(status_code=401, detail="Login required")


def _assert_actor_can_access(
    actor: DealActor,
    session: Optional[Session],
    deal: Deal,
    campaign: Campaign,
) -> None:
    if not session:
        return
    if actor == DealActor.brand and session.account_id != campaign.brand_id:
        raise HTTPException(status_code=403, detail="Brand cannot manage this deal")
    if actor == DealActor.creator and session.account_id != deal.creator_id:
        raise HTTPException(status_code=403, detail="Creator cannot manage this deal")


def _transition(deal: Deal, action: DealAction, actor: DealActor) -> Deal:
    if deal.status in TERMINAL_STATUSES:
        raise HTTPException(status_code=409, detail="Deal is already closed")

    next_status = deal.status
    last_offer_by = deal.last_offer_by
    quote_amount = deal.quote_amount
    deliverables = deal.deliverables
    accepted_at = deal.accepted_at
    completed_at = deal.completed_at

    def require(condition: bool, message: str) -> None:
        if not condition:
            raise HTTPException(status_code=409, detail=message)

    if action.action == DealActionType.send_offer:
        require(actor == DealActor.brand, "Only brands can send offers")
        require(deal.status == DealStatus.draft, "Only draft deals can be offered")
        next_status = DealStatus.offered
        last_offer_by = DealActor.brand
    elif action.action == DealActionType.accept:
        if actor == DealActor.creator:
            require(
                deal.status == DealStatus.offered and deal.last_offer_by == DealActor.brand,
                "Creator can only accept the latest brand offer",
            )
        elif actor == DealActor.brand:
            require(
                deal.status == DealStatus.countered and deal.last_offer_by == DealActor.creator,
                "Brand can only accept a creator counteroffer",
            )
        else:
            raise HTTPException(status_code=403, detail="System cannot accept deals")
        next_status = DealStatus.accepted
        accepted_at = _now()
    elif action.action == DealActionType.reject:
        if actor == DealActor.creator:
            require(
                deal.status == DealStatus.offered and deal.last_offer_by == DealActor.brand,
                "Creator can only reject an active brand offer",
            )
            next_status = DealStatus.rejected
        elif actor == DealActor.brand:
            require(
                deal.status == DealStatus.countered and deal.last_offer_by == DealActor.creator,
                "Brand can only reject a creator counteroffer",
            )
            next_status = DealStatus.withdrawn
        else:
            raise HTTPException(status_code=403, detail="System cannot reject deals")
    elif action.action == DealActionType.negotiate:
        require(actor == DealActor.creator, "Only creators can counter a brand offer")
        require(
            deal.status == DealStatus.offered and deal.last_offer_by == DealActor.brand,
            "Creator can only negotiate the latest brand offer",
        )
        require(action.quote_amount is not None, "Counter amount is required")
        quote_amount = action.quote_amount
        next_status = DealStatus.countered
        last_offer_by = DealActor.creator
    elif action.action == DealActionType.revise_offer:
        require(actor == DealActor.brand, "Only brands can revise offers")
        require(
            deal.status in {DealStatus.countered, DealStatus.offered, DealStatus.draft},
            "Offer can only be revised before acceptance",
        )
        quote_amount = action.quote_amount if action.quote_amount is not None else quote_amount
        deliverables = action.deliverables if action.deliverables is not None else deliverables
        next_status = DealStatus.offered
        last_offer_by = DealActor.brand
    elif action.action == DealActionType.withdraw:
        require(actor == DealActor.brand, "Only brands can withdraw offers")
        require(deal.status in {DealStatus.draft, DealStatus.offered, DealStatus.countered}, "Accepted deals cannot be withdrawn")
        next_status = DealStatus.withdrawn
    elif action.action == DealActionType.mark_contracted:
        require(actor == DealActor.brand, "Only brands can mark deals contracted")
        require(deal.status == DealStatus.accepted, "Deal must be accepted before contracting")
        next_status = DealStatus.contracted
    elif action.action == DealActionType.start_production:
        require(actor == DealActor.brand, "Only brands can start production")
        require(deal.status == DealStatus.contracted, "Deal must be contracted before production")
        next_status = DealStatus.in_production
    elif action.action == DealActionType.submit_content:
        require(actor == DealActor.creator, "Only creators can submit content")
        require(deal.status in {DealStatus.in_production, DealStatus.revisions}, "Content can only be submitted during production")
        next_status = DealStatus.content_submitted
    elif action.action == DealActionType.request_revisions:
        require(actor == DealActor.brand, "Only brands can request revisions")
        require(deal.status in {DealStatus.content_submitted, DealStatus.in_review}, "Revisions require submitted content")
        next_status = DealStatus.revisions
    elif action.action == DealActionType.approve_content:
        require(actor == DealActor.brand, "Only brands can approve content")
        require(deal.status in {DealStatus.content_submitted, DealStatus.in_review, DealStatus.revisions}, "Content must be submitted before approval")
        next_status = DealStatus.approved
    elif action.action == DealActionType.complete:
        require(actor == DealActor.brand, "Only brands can complete deals")
        require(deal.status == DealStatus.approved, "Content must be approved before completion")
        next_status = DealStatus.completed
        completed_at = _now()
    elif action.action == DealActionType.cancel:
        require(actor == DealActor.brand, "Only brands can cancel deals")
        next_status = DealStatus.cancelled

    event = DealEvent(
        actor=actor,
        action=action.action,
        from_status=deal.status,
        to_status=next_status,
        quote_amount=quote_amount,
        note=action.note,
    )
    return deal.model_copy(
        update={
            "status": next_status,
            "quote_amount": quote_amount,
            "deliverables": deliverables,
            "last_offer_by": last_offer_by,
            "accepted_at": accepted_at,
            "completed_at": completed_at,
            "events": [*deal.events, event],
        }
    )


@router.post("/api/campaigns/{campaign_id}/deals", response_model=Deal, status_code=201)
def create_deal(
    campaign_id: str,
    body: DealCreate,
    campaigns: CrudService[Campaign] = Depends(get_campaign_service),
    creators: CreatorService = Depends(get_creator_service),
    service: CrudService[Deal] = Depends(get_deal_service),
):
    try:
        campaign = campaigns.get(campaign_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Campaign not found")
    try:
        creators.get_creator(body.creator_id)
    except CreatorNotFound:
        raise HTTPException(status_code=404, detail="Creator not found")

    payload = body.model_dump(exclude_none=True)
    status = payload.get("status", DealStatus.draft)
    last_offer_by = DealActor.brand if status == DealStatus.offered else None
    deal = Deal(id=str(uuid.uuid4()), campaign_id=campaign_id, last_offer_by=last_offer_by, **payload)
    if status == DealStatus.offered:
        deal = deal.model_copy(
            update={
                "events": [
                    DealEvent(
                        actor=DealActor.brand,
                        action=DealActionType.send_offer,
                        from_status=DealStatus.draft,
                        to_status=DealStatus.offered,
                        quote_amount=deal.quote_amount,
                        note=f"Offer created for campaign {campaign.name}",
                    )
                ]
            }
        )
    return service.create(deal)


@router.get("/api/campaigns/{campaign_id}/deals", response_model=List[Deal])
def list_deals(
    campaign_id: str, service: CrudService[Deal] = Depends(get_deal_service)
):
    return service.list(campaign_id=campaign_id)


@router.get("/api/creators/{creator_id}/deals", response_model=List[Deal])
def list_creator_deals(
    creator_id: str, service: CrudService[Deal] = Depends(get_deal_service)
):
    return service.list(creator_id=creator_id)


@router.get("/api/deals/{deal_id}", response_model=Deal)
def get_deal(deal_id: str, service: CrudService[Deal] = Depends(get_deal_service)):
    try:
        return service.get(deal_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Deal not found")


@router.patch("/api/deals/{deal_id}", response_model=Deal)
def update_deal(
    deal_id: str,
    body: DealUpdate,
    service: CrudService[Deal] = Depends(get_deal_service),
):
    try:
        return service.update(deal_id, body.model_dump(exclude_none=True))
    except NotFound:
        raise HTTPException(status_code=404, detail="Deal not found")


@router.post("/api/deals/{deal_id}/actions", response_model=Deal)
def act_on_deal(
    deal_id: str,
    body: DealAction,
    authorization: str = Header(default=""),
    service: CrudService[Deal] = Depends(get_deal_service),
    campaigns: CrudService[Campaign] = Depends(get_campaign_service),
    auth: AuthService = Depends(get_auth_service),
):
    try:
        deal = service.get(deal_id)
        campaign = campaigns.get(deal.campaign_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Deal not found")

    session = _session_from_header(authorization, auth)
    actor = _actor_from_session(session, body.actor)
    _assert_actor_can_access(actor, session, deal, campaign)
    updated = _transition(deal, body, actor)
    return service.update(deal_id, updated.model_dump())


@router.delete("/api/deals/{deal_id}", status_code=204)
def delete_deal(deal_id: str, service: CrudService[Deal] = Depends(get_deal_service)):
    try:
        service.delete(deal_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Deal not found")
