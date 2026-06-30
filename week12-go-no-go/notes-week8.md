# Week 8 notes — Go/no-go pack

## Three outcomes

| Decision | When |
|----------|------|
| **GO** | All gates PASS, pytest green |
| **GO-WITH-CONDITIONS** | Warnings only (e.g. grounding demo cases) |
| **NO-GO** | Any FAIL gate or pytest failure |

## Why demo shows NO-GO

Calibration ECE exceeds threshold — mimics a real release blocker.

Fix in production: retrain calibrator, adjust prompts, or block high-confidence auto-replies.

## What to attach in Confluence/Jira

1. HTML go/no-go report
2. Link to pytest CI run
3. List of open risks from rationale section
4. SME sign-off checkbox

## You finished 8 weeks

Congratulations — this portfolio now maps directly to the job description you shared.
