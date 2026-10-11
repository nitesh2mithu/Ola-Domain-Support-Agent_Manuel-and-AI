# Milestone 3 — RAG evidence

Labels frozen SHA-256: `b1740a9fc39295b218ac387bd2b39138f8f158080ab39e39049d01a59845c3b7`.

Top-k = 3 chunks; parent documents deduplicated before scoring. Macro means include only six in-scope evaluation queries; fallback queries have no relevant documents and undefined recall.

## fixed calibration

| ID | In scope | Top-1 cosine | Parent |
|---|---|---:|---|
| C1 | True | 0.72448504 | 10_vip_handling |
| C2 | True | 0.72365928 | 09_feedback |
| C3 | True | 0.68994534 | 07_repeat_complaints |
| C4 | False | 0.09160292 | 04_refund_compensation |
| C5 | False | 0.01842099 | 01_ticket_priority |

Maximum out-of-scope: 0.09160292; minimum in-scope: 0.68994534; gap: 0.59834242; chosen threshold: 0.390774130821228.

## fixed document-level evaluation

| Query | Relevant parents | Retrieved parents (dedup) | Precision arithmetic | Recall arithmetic |
|---|---|---|---|---|
| Q1 | 04_refund_compensation | 04_refund_compensation | 1/1 = 1.000000 | 1/1 = 1.000000 |
| Q2 | 06_business_hours | 06_business_hours | 1/1 = 1.000000 | 1/1 = 1.000000 |
| Q3 | 12_ticket_retention | 12_ticket_retention | 1/1 = 1.000000 | 1/1 = 1.000000 |
| Q4 | 11_outage_communication | 11_outage_communication | 1/1 = 1.000000 | 1/1 = 1.000000 |
| Q5 | 08_service_credit | 08_service_credit | 1/1 = 1.000000 | 1/1 = 1.000000 |
| Q6 | 01_ticket_priority, 02_severity_sla | 01_ticket_priority, 02_severity_sla | 2/2 = 1.000000 | 2/2 = 1.000000 |
| Q7 | none | 06_business_hours, 08_service_credit, 02_severity_sla | 0/3 = 0.000000 | undefined (no relevant documents) |

Mean precision: 1.000000; mean recall: 1.000000.

## fixed actual answers and retrieved context

### Q1: When can a duplicate charge be refunded and how long does processing take?

- Chunk `04_refund_compensation:fixed:000:f80d07bc14d4f8cb`, parent `04_refund_compensation`, cosine 0.78248781.
- Chunk `04_refund_compensation:fixed:002:01126a7ab8ef2101`, parent `04_refund_compensation`, cosine 0.49111795.
- Chunk `04_refund_compensation:fixed:001:92e90cec52f577db`, parent `04_refund_compensation`, cosine 0.48661697.

Retrieved policy excerpts:
[04_refund_compensation] A billing specialist may approve a refund after verifying a duplicate charge, a confirmed overcharge, or a charge for a service that was not delivered. Refund only the verified incorrect amount to the original payment method, with a target processing time of 5 to 7 business days after approval. A su
[04_refund_compensation] ise a refund or compensation before approval, and record whether a service credit already covers the same loss to prevent duplicate reimbursement.
[04_refund_compensation] processing time of 5 to 7 business days after approval. A support supervisor may approve goodwill compensation up to INR 200 for a documented service failure, while larger compensation requires the operations manager's approval. Do not promise a refund or compensation before approval, and record whe

### Q2: What hours is standard support available and what happens on holidays?

- Chunk `06_business_hours:fixed:000:3a9ed78829619321`, parent `06_business_hours`, cosine 0.68684024.
- Chunk `06_business_hours:fixed:002:63203da5aeb66f2c`, parent `06_business_hours`, cosine 0.64600790.
- Chunk `06_business_hours:fixed:001:efbb0d33b4eb8416`, parent `06_business_hours`, cosine 0.59722435.

Retrieved policy excerpts:
[06_business_hours] Standard support hours are 09:00 to 18:00 Asia/Kolkata from Monday through Saturday, excluding holidays listed in the team's published support calendar. Support-hour SLA clocks pause outside those hours and resume at the next opening, while business-day refund processing uses Monday through Friday e
[06_business_hours] s received outside standard hours, acknowledge receipt automatically and state when staffed support resumes without promising immediate resolution.
[06_business_hours]  business-day refund processing uses Monday through Friday excluding listed holidays. P1 safety and major-outage reports reach the on-call team at all times, including Sundays and holidays, and use elapsed-time SLA clocks. For other requests received outside standard hours, acknowledge receipt autom

### Q3: How long are closed support tickets retained and when are identifying details deleted?

- Chunk `12_ticket_retention:fixed:000:3abdf5185121cb8d`, parent `12_ticket_retention`, cosine 0.82294858.
- Chunk `12_ticket_retention:fixed:001:1382f4294a33c865`, parent `12_ticket_retention`, cosine 0.69268394.
- Chunk `12_ticket_retention:fixed:002:8dd6ff87848d42ae`, parent `12_ticket_retention`, cosine 0.68213159.

Retrieved policy excerpts:
[12_ticket_retention] Retain a support ticket and its attached communication for 180 days after the ticket is closed, then delete identifying details through the scheduled retention process. For a resolved ticket that remains open, the support owner must either close it after confirming resolution or document why further
[12_ticket_retention] close it after confirming resolution or document why further work is required rather than leave it indefinitely unresolved. Restrict ticket access to staff assigned to support duties, and use masked phone numbers in diagnostic logs. An authorized legal hold pauses deletion only for the affected reco
[12_ticket_retention] orized legal hold pauses deletion only for the affected records, must be documented and reviewed every 30 days, and allows deletion to resume after the hold is released.

### Q4: How often must outage notices be updated?

- Chunk `11_outage_communication:fixed:001:2a50f755af392acd`, parent `11_outage_communication`, cosine 0.55069482.
- Chunk `11_outage_communication:fixed:000:e594a15651293c24`, parent `11_outage_communication`, cosine 0.50402611.
- Chunk `11_outage_communication:fixed:002:2a8cb59e2a16f2bb`, parent `11_outage_communication`, cosine 0.49818152.

Retrieved policy excerpts:
[11_outage_communication] ation and update it every 30 elapsed minutes while disruption continues. Each notice must distinguish confirmed impact from investigation findings and provide only verified workarounds, with no unconfirmed restoration promise. After recovery is verified, publish a recovery notice and attach a factua
[11_outage_communication] When monitoring or multiple validated tickets confirm an outage, the duty incident lead opens an incident record and identifies the affected service and regions. Publish an initial in-app notice within 15 elapsed minutes of incident confirmation and update it every 30 elapsed minutes while disruptio
[11_outage_communication] y is verified, publish a recovery notice and attach a factual incident summary to related support tickets within 2 business days.

### Q5: What is the maximum standard noncash service credit and how long is it valid?

- Chunk `08_service_credit:fixed:000:73e5b77be6988721`, parent `08_service_credit`, cosine 0.60664207.
- Chunk `08_service_credit:fixed:001:e019600e4052eaa0`, parent `08_service_credit`, cosine 0.60659009.
- Chunk `08_service_credit:fixed:002:80846bbe499e9ad7`, parent `08_service_credit`, cosine 0.44788778.

Retrieved policy excerpts:
[08_service_credit] A support supervisor may approve a noncash service credit up to INR 150 for a verified service interruption when a cash refund does not already compensate the same loss. Apply an approved service credit to the customer's fabricated capstone account balance, with validity of 30 days from issuance. Se
[08_service_credit]  account balance, with validity of 30 days from issuance. Service credits cannot be transferred or exchanged for cash, and a credit above INR 150 requires the operations manager's approval. Record the reason, approval, amount and expiry in the ticket and communicate those terms before issuing the cr
[08_service_credit] the ticket and communicate those terms before issuing the credit.

### Q6: How are P1 and P2 priorities classified and what are their acknowledgement targets?

- Chunk `01_ticket_priority:fixed:000:f1252f8593080a60`, parent `01_ticket_priority`, cosine 0.62344378.
- Chunk `01_ticket_priority:fixed:001:467e14d88ab04b30`, parent `01_ticket_priority`, cosine 0.51693636.
- Chunk `02_severity_sla:fixed:000:b78b055efceb846b`, parent `02_severity_sla`, cosine 0.42395151.

Retrieved policy excerpts:
[01_ticket_priority] Assign P1 priority when a report describes an immediate safety concern or a widespread inability to use the ride service. Assign P2 priority to a blocked account or an incorrect charge that prevents a rider or driver from continuing normal service use. Assign P3 priority to a nonblocking technical i
[01_ticket_priority] service use. Assign P3 priority to a nonblocking technical issue or product defect, and assign P4 priority to a general inquiry or feedback request. When several conditions apply, record the highest priority and the facts that justify it without treating VIP status as a safety severity.
[02_severity_sla] For P1 severity, acknowledge within 15 elapsed minutes and target resolution or a documented workaround within 4 elapsed hours. For P2 severity, acknowledge within 1 support hour and target resolution within 24 support hours. For P3 severity, acknowledge within 4 support hours and target resolution 

### Q7: How can I calculate the orbital period of a planet?

- Chunk `06_business_hours:fixed:000:3a9ed78829619321`, parent `06_business_hours`, cosine 0.12251306.
- Chunk `08_service_credit:fixed:001:e019600e4052eaa0`, parent `08_service_credit`, cosine 0.11971521.
- Chunk `02_severity_sla:fixed:002:62fc1a72f6be9210`, parent `02_severity_sla`, cosine 0.08837545.

I don't know based on the available policy documents.

## sentence calibration

| ID | In scope | Top-1 cosine | Parent |
|---|---|---:|---|
| C1 | True | 0.74592054 | 10_vip_handling |
| C2 | True | 0.73351645 | 09_feedback |
| C3 | True | 0.68911171 | 07_repeat_complaints |
| C4 | False | 0.07866859 | 09_feedback |
| C5 | False | 0.01867789 | 06_business_hours |

Maximum out-of-scope: 0.07866859; minimum in-scope: 0.68911171; gap: 0.61044312; chosen threshold: 0.38389015197753906.

## sentence document-level evaluation

| Query | Relevant parents | Retrieved parents (dedup) | Precision arithmetic | Recall arithmetic |
|---|---|---|---|---|
| Q1 | 04_refund_compensation | 04_refund_compensation, 07_repeat_complaints, 08_service_credit | 1/3 = 0.333333 | 1/1 = 1.000000 |
| Q2 | 06_business_hours | 06_business_hours, 02_severity_sla | 1/2 = 0.500000 | 1/1 = 1.000000 |
| Q3 | 12_ticket_retention | 12_ticket_retention, 11_outage_communication | 1/2 = 0.500000 | 1/1 = 1.000000 |
| Q4 | 11_outage_communication | 11_outage_communication, 02_severity_sla | 1/2 = 0.500000 | 1/1 = 1.000000 |
| Q5 | 08_service_credit | 08_service_credit, 04_refund_compensation | 1/2 = 0.500000 | 1/1 = 1.000000 |
| Q6 | 01_ticket_priority, 02_severity_sla | 01_ticket_priority, 02_severity_sla | 2/2 = 1.000000 | 2/2 = 1.000000 |
| Q7 | none | 06_business_hours, 02_severity_sla | 0/2 = 0.000000 | undefined (no relevant documents) |

Mean precision: 0.555556; mean recall: 1.000000.

## sentence actual answers and retrieved context

### Q1: When can a duplicate charge be refunded and how long does processing take?

- Chunk `04_refund_compensation:sentence:000:d9ace4c0918f616e`, parent `04_refund_compensation`, cosine 0.79725498.
- Chunk `07_repeat_complaints:sentence:000:c9d3c8b51fed299d`, parent `07_repeat_complaints`, cosine 0.48921639.
- Chunk `08_service_credit:sentence:000:87342290dbfac260`, parent `08_service_credit`, cosine 0.43416399.

Retrieved policy excerpts:
[04_refund_compensation] A billing specialist may approve a refund after verifying a duplicate charge, a confirmed overcharge, or a charge for a service that was not delivered. Refund only the verified incorrect amount to the original payment method, with a target processing time of 5 to 7 business days after approval.
[07_repeat_complaints] Treat a report as a repeat complaint when the same customer reports the same underlying issue within 30 days of the earlier ticket. Link the new report to the earlier ticket and reopen that ticket when the previous resolution has not held, preserving the original history.
[08_service_credit] A support supervisor may approve a noncash service credit up to INR 150 for a verified service interruption when a cash refund does not already compensate the same loss. Apply an approved service credit to the customer's fabricated capstone account balance, with validity of 30 days from issuance.

### Q2: What hours is standard support available and what happens on holidays?

- Chunk `06_business_hours:sentence:000:114c384cf5726487`, parent `06_business_hours`, cosine 0.68675876.
- Chunk `06_business_hours:sentence:001:c1371503f1ddf5c5`, parent `06_business_hours`, cosine 0.64909470.
- Chunk `02_severity_sla:sentence:001:96663d27ea10e6ee`, parent `02_severity_sla`, cosine 0.50933778.

Retrieved policy excerpts:
[06_business_hours] Standard support hours are 09:00 to 18:00 Asia/Kolkata from Monday through Saturday, excluding holidays listed in the team's published support calendar. Support-hour SLA clocks pause outside those hours and resume at the next opening, while business-day refund processing uses Monday through Friday excluding listed holidays.
[06_business_hours] P1 safety and major-outage reports reach the on-call team at all times, including Sundays and holidays, and use elapsed-time SLA clocks. For other requests received outside standard hours, acknowledge receipt automatically and state when staffed support resumes without promising immediate resolution.
[02_severity_sla] For P3 severity, acknowledge within 4 support hours and target resolution within 72 support hours; for P4 severity, acknowledge within 8 support hours and target resolution within 120 support hours. These SLA targets use the business-hours policy for support-hour calculations and require an update before a deadline is missed, while external dependencies must be documented rather than presented as guaranteed completion times.

### Q3: How long are closed support tickets retained and when are identifying details deleted?

- Chunk `12_ticket_retention:sentence:000:e6c1ea1c4aeadb47`, parent `12_ticket_retention`, cosine 0.82529122.
- Chunk `12_ticket_retention:sentence:001:6b4d893bfc18e8e8`, parent `12_ticket_retention`, cosine 0.69773376.
- Chunk `11_outage_communication:sentence:001:a1e71105c32d8029`, parent `11_outage_communication`, cosine 0.45294631.

Retrieved policy excerpts:
[12_ticket_retention] Retain a support ticket and its attached communication for 180 days after the ticket is closed, then delete identifying details through the scheduled retention process. For a resolved ticket that remains open, the support owner must either close it after confirming resolution or document why further work is required rather than leave it indefinitely unresolved.
[12_ticket_retention] Restrict ticket access to staff assigned to support duties, and use masked phone numbers in diagnostic logs. An authorized legal hold pauses deletion only for the affected records, must be documented and reviewed every 30 days, and allows deletion to resume after the hold is released.
[11_outage_communication] Each notice must distinguish confirmed impact from investigation findings and provide only verified workarounds, with no unconfirmed restoration promise. After recovery is verified, publish a recovery notice and attach a factual incident summary to related support tickets within 2 business days.

### Q4: How often must outage notices be updated?

- Chunk `11_outage_communication:sentence:001:a1e71105c32d8029`, parent `11_outage_communication`, cosine 0.56870186.
- Chunk `11_outage_communication:sentence:000:2f6146f10782d5d1`, parent `11_outage_communication`, cosine 0.51314580.
- Chunk `02_severity_sla:sentence:001:96663d27ea10e6ee`, parent `02_severity_sla`, cosine 0.45688677.

Retrieved policy excerpts:
[11_outage_communication] Each notice must distinguish confirmed impact from investigation findings and provide only verified workarounds, with no unconfirmed restoration promise. After recovery is verified, publish a recovery notice and attach a factual incident summary to related support tickets within 2 business days.
[11_outage_communication] When monitoring or multiple validated tickets confirm an outage, the duty incident lead opens an incident record and identifies the affected service and regions. Publish an initial in-app notice within 15 elapsed minutes of incident confirmation and update it every 30 elapsed minutes while disruption continues.
[02_severity_sla] For P3 severity, acknowledge within 4 support hours and target resolution within 72 support hours; for P4 severity, acknowledge within 8 support hours and target resolution within 120 support hours. These SLA targets use the business-hours policy for support-hour calculations and require an update before a deadline is missed, while external dependencies must be documented rather than presented as guaranteed completion times.

### Q5: What is the maximum standard noncash service credit and how long is it valid?

- Chunk `08_service_credit:sentence:000:87342290dbfac260`, parent `08_service_credit`, cosine 0.60688919.
- Chunk `08_service_credit:sentence:001:ba76ac0c2b042949`, parent `08_service_credit`, cosine 0.47787201.
- Chunk `04_refund_compensation:sentence:001:3848988ea6bf42e0`, parent `04_refund_compensation`, cosine 0.27496719.

Retrieved policy excerpts:
[08_service_credit] A support supervisor may approve a noncash service credit up to INR 150 for a verified service interruption when a cash refund does not already compensate the same loss. Apply an approved service credit to the customer's fabricated capstone account balance, with validity of 30 days from issuance.
[08_service_credit] Service credits cannot be transferred or exchanged for cash, and a credit above INR 150 requires the operations manager's approval. Record the reason, approval, amount and expiry in the ticket and communicate those terms before issuing the credit.
[04_refund_compensation] A support supervisor may approve goodwill compensation up to INR 200 for a documented service failure, while larger compensation requires the operations manager's approval. Do not promise a refund or compensation before approval, and record whether a service credit already covers the same loss to prevent duplicate reimbursement.

### Q6: How are P1 and P2 priorities classified and what are their acknowledgement targets?

- Chunk `01_ticket_priority:sentence:000:f59c0fd2b775b400`, parent `01_ticket_priority`, cosine 0.61787486.
- Chunk `01_ticket_priority:sentence:001:4ae8f4dba0c52b2d`, parent `01_ticket_priority`, cosine 0.57579178.
- Chunk `02_severity_sla:sentence:000:e5ba0f35e59164a0`, parent `02_severity_sla`, cosine 0.42330867.

Retrieved policy excerpts:
[01_ticket_priority] Assign P1 priority when a report describes an immediate safety concern or a widespread inability to use the ride service. Assign P2 priority to a blocked account or an incorrect charge that prevents a rider or driver from continuing normal service use.
[01_ticket_priority] Assign P3 priority to a nonblocking technical issue or product defect, and assign P4 priority to a general inquiry or feedback request. When several conditions apply, record the highest priority and the facts that justify it without treating VIP status as a safety severity.
[02_severity_sla] For P1 severity, acknowledge within 15 elapsed minutes and target resolution or a documented workaround within 4 elapsed hours. For P2 severity, acknowledge within 1 support hour and target resolution within 24 support hours.

### Q7: How can I calculate the orbital period of a planet?

- Chunk `06_business_hours:sentence:000:114c384cf5726487`, parent `06_business_hours`, cosine 0.12519479.
- Chunk `06_business_hours:sentence:001:c1371503f1ddf5c5`, parent `06_business_hours`, cosine 0.10913777.
- Chunk `02_severity_sla:sentence:001:96663d27ea10e6ee`, parent `02_severity_sla`, cosine 0.10411745.

I don't know based on the available policy documents.

## Deployment recommendation

Deploy fixed chunking: fixed chunks achieved mean document precision 1.0000 and recall 1.0000, while sentence chunks achieved precision 0.5556 and recall 1.0000 on the same six labelled queries. Selection prioritizes recall and then precision, with complete sentence boundaries breaking metric ties. These small-corpus measurements support this deployment choice but do not establish performance on broader or near-domain questions.
