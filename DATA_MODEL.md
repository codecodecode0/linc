# linc — Data Model

The canonical data model for linc. It covers every core entity, but only a
subset is **implemented** today (in-memory, no database). The rest is
**documented** so the schema is locked before we wire Postgres.

## Conventions

- **PK:** `id uuid` (`gen_random_uuid()`).
- **Timestamps:** `created_at` / `updated_at timestamptz default now()`.
- **Money:** `*_amount bigint` in **paise** + `currency char(3) default 'INR'` — never floats.
- **Enums:** shown inline as `field{a,b,c}`.
- **FKs:** `→table`.
- **camelCase out:** models serialize to camelCase for the frontend; Python stays snake_case.

## Implementation status

| Area | Status |
|---|---|
| Creator account (create/read/update) | ✅ implemented (in-memory) |
| Brand account (create/read/update) | ✅ implemented (in-memory) |
| Auth: email/phone **OTP** + **Google** login | ✅ implemented (mock-capable) |
| Social account linking (Instagram, YouTube) | ✅ implemented (existing OAuth flow) |
| Fetch social handle details / insights (on demand) | ✅ implemented (mock-capable) |
| Agency account | 📄 documented (trivial to add, mirrors Brand) |
| Likeness license, AI generation | 📄 documented |
| Campaign, Deal, Content | 📄 documented |
| Wallet, payments, payouts, invoicing | 📄 documented |
| Insight snapshot **jobs**, invoicing **jobs** | ⛔ not built (by design) |

---

## 1. Authentication & accounts

linc keeps accounts **simple**: each account type (creator, brand, agency)
is a standalone login — **one account = one login**. No multi-user teams /
memberships yet (additive later).

**Login methods** (all behind a mock until real credentials are set):

| Method | How | Production provider (India) |
|---|---|---|
| **Email OTP** | request code → verify | Amazon SES / Resend / SendGrid |
| **Phone OTP** | request code → verify | MSG91 / Twilio / WhatsApp OTP |
| **Google ("Sign in with Gmail")** | OAuth 2.0 / OpenID Connect | Google Identity |

Signup captures **email + phone** for both creators and brands. Sessions are
signed bearer tokens (`account_type` + `id` + `exp`, HMAC-signed).

```
creator   id, email citext UNIQUE, phone UNIQUE, name, handle UNIQUE, bio,
          niche, city, country, avatar, certified bool, certified_at,
          rating numeric(3,2), starting_rate_amount, currency,
          followers_display, engagement_display,   -- cached display strings
          google_sub TEXT NULL,                     -- set when linked to Gmail
          status{onboarding,active,paused}

brand     id, email citext UNIQUE, phone UNIQUE, name, legal_name, logo_url,
          website, category, gstin, billing_address jsonb,
          managing_agency_id →agency NULL, google_sub TEXT NULL,
          status{active,suspended}

agency    id, email citext UNIQUE, phone UNIQUE, name, legal_name, logo_url,
          gstin, billing_address jsonb, google_sub TEXT NULL,
          status{active,suspended}

otp_challenge  id, channel{email,phone}, value, code_hash, expires_at,
  (transient)  attempts int, consumed_at      -- in-memory now; short TTL
```

---

## 2. Social accounts & insights

```
social_account       id, creator_id →creator, platform{instagram,youtube},
                     account_ref, username, profile_picture_url, account_type,
                     followers_count bigint, status{connected,expired,revoked},
                     connected_at, last_synced_at,
                     metadata jsonb (ig_user_id / channel_id / linked_page_id)
                     UNIQUE(creator_id, platform)

oauth_credential     id, social_account_id →social_account UNIQUE,
                     access_token_enc, refresh_token_enc, scopes text[],
                     token_type, expires_at, obtained_at
                     -- split out so tokens are isolated & encrypted at rest

account_insight_     id, social_account_id →social_account, captured_at,
  snapshot           period{day,week,days_28,lifetime},
                     reach, views, accounts_engaged, total_interactions,
                     likes, comments, saves, shares, replies, reposts,
                     profile_links_taps, follower_count bigint,  -- all nullable
                     engagement_rate numeric(6,3), raw jsonb, source{api,mock}
                     INDEX(social_account_id, period, captured_at)

audience_demographic id, social_account_id →social_account, captured_at,
                     audience_type{followers,engaged,reached},
                     dimension{age,gender,age_gender,city,country,language},
                     bucket text, value_pct numeric(6,3), value_count bigint
                     INDEX(social_account_id, audience_type, dimension)

content_insight      id, social_account_id →social_account, media_ref,
  (optional)         media_type{reel,image,carousel,story,video}, permalink,
                     posted_at, reach, views, likes, comments, saves, shares,
                     plays, watch_time_secs, captured_at, raw jsonb
```

> **Today:** insights are fetched **on demand** during the connect flow and
> returned as a `SocialInsights` payload (followers + a metric list +
> audience). The `account_insight_snapshot` / `audience_demographic` tables are
> where a future periodic job would persist history. No job is built yet.

### Meta (Instagram) metrics we can pull — reference

Account-level (Graph API v22+): `reach`, **`views`** (replaced `impressions`),
`accounts_engaged`, `total_interactions`, `likes`, `comments`, `saves`,
`shares`, `replies`, `reposts`, `profile_links_taps`, `follower_count`.
Demographics: `follower_demographics` / `engaged_audience_demographics`
broken down by **age, gender, city, country** (needs `metric_type=total_value`
+ `timeframe` + `breakdown`, **100+ followers**, ~48h delay).

⚠️ Deprecated (≈Apr 2025): `impressions`, `profile_views`, `website_clicks`,
`email_contacts`, `phone_call_clicks`, `text_message_clicks`. YouTube parallels:
subscribers, views, watch-time, avg-view-duration.

---

## 3. Certified Digi Creator (consent + AI)

```
likeness_license id, creator_id →creator, grantee_type{platform,brand},
                 brand_id →brand NULL, media_scope{static,video,both},
                 allowed_use text, territory, term_start date, term_end date NULL,
                 rate_model{per_generation,per_use,flat_monthly},
                 rate_amount, currency,
                 status{active,paused,revoked,expired}, contract_id →contract NULL

ai_generation    id, brand_id →brand, campaign_id →campaign NULL,
                 creator_id →creator, license_id →likeness_license,
                 kind{static_image,video}, spec jsonb,
                 output_asset_id →content_asset NULL,
                 status{queued,generating,ready,failed,published},
                 cost_amount, royalty_amount, ready_at
```

---

## 4. Campaigns, deals, content

```
campaign     id, brand_id →brand, name,
             objective{awareness,traffic,engagement,conversions,app_installs},
             product_category, status{draft,active,paused,completed,archived},
             budget_amount, spend_amount default 0, currency,
             start_date, end_date, target_audience jsonb, platforms text[]

deal         id, campaign_id →campaign, creator_id →creator,
             type{real_video,ai_static,ai_video},
             status{draft,offered,countered,accepted,rejected,withdrawn,
                    contracted,in_production,content_submitted,in_review,
                    revisions,approved,completed,cancelled,disputed},
             quote_amount, currency, brief jsonb, due_date,
             contract_id →contract NULL, accepted_at, completed_at

deal_offer   id, deal_id →deal, proposed_by{brand,creator,agency}, amount,
             message, status{pending,accepted,countered,rejected,withdrawn,expired}

content      id, deal_id →deal, title,
             type{raw_video,edited_video,image,reel,story},
             status{requested,submitted,in_review,revisions_requested,
                    approved,delivered,rejected},
             revision_no int, due_date, submitted_at, approved_at,
             current_asset_id →content_asset NULL

content_asset  id, content_id →content NULL, ai_generation_id →ai_generation NULL,
               storage_key, url, mime_type, size_bytes, duration_secs,
               width, height, checksum, uploaded_by

content_review id, content_id →content,
               decision{approved,revisions_requested,rejected}, comment

contract     id, subject_type{deal,license}, subject_id, document_url,
             esign_provider, provider_ref,
             status{draft,sent,viewed,signed,declined,expired},
             signed_by_creator_at, signed_by_brand_at
```

---

## 5. Money & payments (India / provider-agnostic)

**Principle:** linc **never custodies funds**. Brands pre-fund into a Payment
Aggregator's **escrow** (Razorpay/Cashfree); the `wallet` is an internal
**ledger mirror**. Disbursement to creators goes through **Razorpay Route**
linked accounts (held until content is approved). All money state transitions
are driven by **signature-verified, idempotent webhooks**.
`provider{razorpay,cashfree,stripe}` (Stripe reserved for future cross-border).

```
wallet              id, owner_type{brand,agency}, owner_id, currency,
                    balance_amount default 0,        -- MIRROR of escrow
                    status{active,frozen}

ledger_entry        id, wallet_id →wallet, direction{credit,debit}, amount,
                    balance_after,
                    reason{prefund,refund,hold,hold_release,deal_charge,
                           ai_charge,platform_fee,gst,tds,transfer,settlement,adjustment},
                    ref_type, ref_id, memo

payment_customer    id, owner_type{brand,agency}, owner_id, provider,
                    provider_customer_id
payment_method      id, owner_type, owner_id, provider, provider_token,
                    kind{card,upi,netbanking,upi_autopay,enach}, label,
                    is_default, status

payment             id, owner_type{brand,agency}, owner_id, provider,
  (money IN)        provider_order_id, provider_payment_id UNIQUE,
                    purpose{wallet_prefund,direct_charge},
                    amount, fee_amount, tax_amount, currency, method,
                    status{created,authorized,captured,failed,
                           refunded,partially_refunded},
                    wallet_id →wallet NULL, invoice_id →invoice NULL,
                    captured_at, raw jsonb
refund              id, payment_id →payment, provider, provider_refund_id,
                    amount, reason, status{pending,processed,failed}, processed_at

linked_account      id, owner_type{creator,agency}, owner_id, provider,
  (Route/vendor)    provider_linked_account_id,
                    kyc_status{pending,under_review,activated,suspended,rejected},
                    settlement_config jsonb
transfer            id, provider, provider_transfer_id UNIQUE,
  (money OUT/split) linked_account_id →linked_account, source_payment_id →payment NULL,
                    wallet_id →wallet, deal_id →deal NULL, ai_generation_id NULL,
                    gross_amount, platform_fee_amount, tds_amount, net_amount,
                    on_hold bool, status{created,on_hold,processed,reversed,failed},
                    settled_at, raw jsonb
payout              id, owner_type{creator,agency}, owner_id, provider,
  (bulk fallback)   provider_payout_id UNIQUE, provider_fund_account_id, utr,
                    method{bank,upi}, period_start, period_end,
                    gross_amount, platform_fee_amount, tds_amount, net_amount,
                    status{queued,processing,paid,failed,reversed,on_hold},
                    failure_reason, paid_at, raw jsonb
settlement          id, provider, provider_settlement_id UNIQUE, amount,
                    fees_amount, tax_amount, utr, settled_at,
                    status{pending,settled,failed}, raw jsonb

provider_webhook_   id, provider, provider_event_id UNIQUE, event_type,
  event             payload jsonb, signature_verified bool,
                    status{received,processed,failed,ignored}, processed_at

earning             id, creator_id →creator, type{shoot_fee,usage_royalty,bonus},
                    amount, currency, source_type{deal,ai_generation}, source_id,
                    status{pending,cleared,settled,reversed},
                    transfer_id →transfer NULL, payout_id →payout NULL

invoice             id, bill_to_type{brand,agency}, bill_to_id,
                    kind{advance_prefund,usage_tax,credit_note}, number UNIQUE,
                    status{draft,issued,partially_paid,paid,void},
                    subtotal_amount, tax_amount, total_amount, currency,
                    period_start, period_end, due_date, issued_at, paid_at,
                    pdf_url, gst_breakup jsonb, payment_id →payment NULL
invoice_line_item   id, invoice_id →invoice, description, qty, unit_amount,
                    amount, tax_rate, hsn_sac, ref_type, ref_id
```

**Upfront flow:** brand pays → `payment(wallet_prefund)` into escrow →
`ledger_entry(credit, prefund)` mirrors to `wallet` → `advance_prefund` invoice.
Content approved → `transfer` to creator's `linked_account` (held → released),
retaining `platform_fee` + `tds` → `earning(settled)`. Monthly `usage_tax`
invoice reconciles GST/fees to actual spend.

> **Not built yet:** invoice generation, payout batching, reconciliation jobs.

---

## 6. Supporting (documented only)

```
message_thread  id, deal_id →deal NULL, brand_id →brand, creator_id →creator,
                subject, last_message_at
message         id, thread_id →message_thread, sender_type{brand,creator,agency},
                sender_id, body, attachments jsonb, read_at
notification    id, recipient_type, recipient_id, kind, title, body, read_at
audit_log       id, actor_type, actor_id, action, entity_type, entity_id, meta jsonb
```
