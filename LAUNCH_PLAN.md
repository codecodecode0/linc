# linc — Product Spec & Launch Requirements (v1)

A focused plan for what to build, what to cut, and what must be true to go live.
Opinionated on purpose.

---

## 1. The one decision that matters: pick the wedge

linc's PRD has **three products** (real video delivery, AI static ads, AI video
ads) plus a recommendation engine and three audiences. **You cannot launch all
of that.** Trying to will mean shipping everything at 60% and winning nothing.

**The wedge is the delivery workflow — and the consent it captures.**

- The pain that is real, urgent, and unsolved *today* is **operational**:
  brands juggle WhatsApp + Drive + contracts + manual bank transfers; creators
  chase invoices. That gets you paying customers on day one.
- The **defensible** part is what that workflow *captures*: a real shoot + a
  signed likeness consent. That is the seed for AI ads and passive income —
  but it only exists *after* you own the delivery relationship.

So the sequence is: **win delivery → capture consent → upsell AI static →
later AI video.** Not the reverse.

> **v1 = a beautifully simple brand↔creator deal platform for India, with
> likeness consent captured at contract time. AI static ads are a fast-follow
> upsell. AI video, agencies, and the "recommendation data moat" are v2+.**

---

## 2. v1 scope (MoSCoW)

### MUST have to launch
- **Auth & accounts** — creator + brand, email/phone OTP + Google (you have the
  shell; needs real OTP delivery + hardening).
- **Creator onboarding** — profile, **Instagram/YouTube connect with real
  insights** (followers, engagement, audience), KYC (PAN).
- **Brand brief → match → offer → negotiate → accept** (you have the deal
  lifecycle; keep rules-based matching, not ML).
- **Contract e-sign** — deliverable contract **+ likeness consent opt-in**.
- **File delivery** — creator uploads raw/edited video; brand reviews/approves
  (needs real object storage, not URLs).
- **Payments with escrow** — brand funds upfront → held → released on approval
  (India PA, see §5). This is non-negotiable for marketplace trust.
- **Notifications** — WhatsApp + email on every state change (India = WhatsApp).
- **In-platform messaging** — brand↔creator chat (a core PRD promise).
- **Dispute/refund path** — even if manual at first.

### SHOULD have (fast-follow, weeks after launch)
- **AI static ad generation** — consented, human-reviewed, watermarked,
  disclosed. Per-generation creator royalty (the passive-income story).
- Ratings/reviews (two-sided).
- Basic brand analytics (deal status, spend, delivery times).

### WON'T have in v1 (deliberately cut — see §3)
- AI **video** generation.
- **Agencies** (multi-tenant, permissions, rebilling).
- ML **recommendation engine / data moat**.
- Multi-currency / cross-border brands.
- Platforms beyond Instagram + YouTube.

---

## 3. What to cut or defer (and why)

| Cut from v1 | Why | When |
|---|---|---|
| **AI video ads** | Hardest to get right (quality, compute cost, legal/deepfake risk). Crowded (Arcads, Icon, HeyGen). High blast radius if a bad asset ships. | v2, after static proves the consent→royalty loop works |
| **Agencies** | Adds multi-user auth, permissions, and agency-billed money flow. Real demand, but it triples complexity. Schema is already agency-ready. | v2 |
| **"AI recommendation engine" as a launch claim** | A data moat is *earned* after thousands of deals. Day one you have no data. Rules-based matching (niche + audience + budget + rate fit) is enough and honest. | v2+ |
| **Wallet as custodial balance** | RBI: you can't pool customer funds. Use the PA's escrow; keep your `wallet` a ledger mirror only. | keep as-is |
| **More social platforms** | Instagram + YouTube cover the India creator market. Each new platform = new OAuth + review. | later |

**Also trim the marketing story:** lead with "everything in one place, paid
fast," not "three paths + AI data moat." Sell the pain you solve *today*.

---

## 4. Legal & consent — the make-or-break for the AI angle in India

This is where most "AI likeness" startups die. Treat it as a launch blocker,
not a footnote. **Get a lawyer.**

- **Likeness License agreement** (e-signed, the core IP asset): explicit,
  **revocable**, scope = *static only* for v1, **term-limited**, territory,
  permitted use = *performance ads for the contracting brand only*, per-use
  rate. Versioned and auditable.
- **Personality / publicity rights** — Indian courts increasingly protect a
  person's likeness/voice. A clean consent layer is a *tailwind*, but consent
  must be airtight and revocation must actually stop generation + honor
  takedowns within a defined SLA.
- **AI disclosure** — ASCI (influencer/AI rules) and Meta require disclosing
  synthetic content and the material connection (#ad). Bake labels into every
  generated asset + the ad metadata.
- **Misuse guardrails** — only the consenting creator's approved brand/products;
  block political/adult/medical/financial misuse; content moderation; an
  **audit log of every generation** (who, what, when, which license).
- **DPDP Act (India privacy)** — consent for personal data + likeness; right to
  erasure; privacy policy; DPA with vendors. Required *before* you touch real
  Meta data anyway.
- **Standard deal contract** — deliverable, usage rights/IP license of the
  video, revisions, exclusivity, kill fee.
- **Content provenance** — embed C2PA content credentials / watermark on AI
  assets. Increasingly expected and protective.

---

## 5. Payments (India) — launch-critical

- **Provider:** Razorpay (collections + **Route** for marketplace split) and/or
  Cashfree (payouts). **Do not custody funds** — money sits in the PA's escrow.
- **Flow:** brand pays upfront → escrow → **released to creator on approval**
  (held-until-approved is the trust mechanism that solves cold-start). Refund on
  dispute.
- **Tax:** GST on your platform fee; **TDS 194-O (1%)** on creator payouts;
  auto-generated invoices + payout statements.
- **Take rate (decide now):** e.g. **10–20% commission** on deals; a
  **per-generation fee** on AI static (split with creator as royalty).
- **KYC for payouts:** creator PAN + bank/UPI (you have payout accounts); brand
  GSTIN.

---

## 6. Meta / Google — start the long-lead items NOW

- **Meta App Review + Business Verification** takes weeks. To pull *any*
  creator's real Instagram insights in production you need approved permissions.
  **Begin immediately.**
- Use **Instagram Login** (no Facebook Page required) for creator onboarding.
- You need a **public Privacy Policy + Terms URL** to even submit. (Also needed
  for DPDP.)
- Handle token refresh, rate limits, and the metric deprecations
  (`impressions`→`views`, etc. — noted in `DATA_MODEL.md`).

---

## 7. AI static generation (the SHOULD, scoped tight)

- **Pipeline:** capture reference frames from the real shoot → consented
  generation (hosted model or partner) → **mandatory human review** → watermark
  + disclosure → export Meta-ready sizes.
- **Human-in-the-loop is required** before any AI ad goes live — protects the
  brand and the creator and is your quality moat early on.
- **Unit economics:** know your cost per generation; price = cost + margin +
  creator royalty. The royalty *is* the passive-income product.
- Keep it **static-only** until the loop (consent → generate → approve → pay
  royalty) is proven end-to-end.

---

## 8. Platform engineering — go-live checklist

The current build is an excellent prototype (FastAPI + in-memory + a clean
modular frontend). To be production-ready:

- [ ] **Postgres** (replace in-memory; schema already designed) + Alembic
      migrations. The repository pattern means this is a swap, not a rewrite.
- [ ] **Real auth** — JWT + refresh, real OTP (MSG91/SES), Google OAuth app,
      rate limiting, token/secret encryption at rest.
- [ ] **Object storage** — S3-compatible for heavy video (multipart upload,
      signed URLs, virus scan). Replace `assetUrl` placeholders.
- [ ] **Notifications** — WhatsApp (MSG91/Gupshup) + email (SES/Resend) on deal,
      delivery, payment, payout events.
- [ ] **Messaging** — persistent brand↔creator threads.
- [ ] **Background jobs** — payouts, invoice generation, insight refresh,
      AI-generation queue (don't do these inline).
- [ ] **Observability** — structured logs, Sentry, uptime/health, audit log.
- [ ] **Deploy** — backend on Render/Railway/Fly; managed Postgres; CI/CD (you
      already have CI). The static UI on Pages won't run the app — it needs the
      backend host.
- [ ] **Security pass** — OWASP basics, secrets manager, webhook signature
      verification (payments + Meta).

---

## 9. Instrument from day one

Liquidity, not vanity. Track:

- **Match → fill:** time-to-match, % briefs filled, % offers accepted.
- **Money:** GMV, take rate, AOV, time-to-first-payout for creators.
- **Quality:** deal completion rate, revision count, dispute rate.
- **AI loop (once live):** % deals that opt into licensing, generations per
  creator, passive ₹ per creator/month.
- **Funnel:** signup → social connect → first deal → repeat.

---

## 10. Phased roadmap

- **Phase 0 — Launch prep (do first):** Postgres, real auth, escrow payments,
  object storage, WhatsApp/email, messaging, **start Meta App Review**, legal
  docs (license + privacy + terms), KYC.
- **Phase 1 — v1 launch:** delivery marketplace (brief → deliver → pay) +
  consent capture + rules-based matching. **Concierge the first ~20 deals** by
  hand. Win one niche.
- **Phase 2 — Monetize the moat:** AI static ads + passive royalties; ratings;
  brand analytics.
- **Phase 3 — Expand:** AI video, agencies, recommendation ML, scale.

---

## 11. GTM focus to actually get to "live"

- **Pick one vertical + one city** to seed liquidity (e.g. D2C beauty/skincare
  in Mumbai, or food in Bengaluru). Marketplaces die from thin liquidity, not
  bad features.
- Recruit ~50–100 creators in that niche and ~10–20 brands; **manually match
  the first deals.** Do things that don't scale.
- Lead with the **today pain** (one place, fast UPI payouts, real insights);
  introduce **AI + passive income** once trust exists.

---

## 12. Open decisions for you (founder calls)

1. **Wedge confirmation:** delivery-first, AI static fast-follow — yes?
2. **Take rate:** % on deals + per-generation fee — set the numbers.
3. **First niche + city** to seed.
4. **AI build vs buy:** partner an image model vs build the pipeline.
5. **Legal budget/owner:** who drafts the license + privacy + terms (blocker).
6. **Escrow provider:** Razorpay Route vs Cashfree.

---

### TL;DR
Cut AI video, agencies, and the "ML recommendation moat" from launch. Ship a
**delivery marketplace that captures likeness consent**, with **escrow payments,
real Meta insights, WhatsApp notifications, and Postgres** — then turn on
**AI static ads + passive royalties** as the wedge that makes linc different.
The two real launch blockers are **legal/consent** and **payments+Meta review**;
start both now because they have the longest lead times.
