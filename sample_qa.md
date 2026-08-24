# RAG System Evaluation: Sample Q&A Log

**Candidate Name:** Sanika Tikole  
**Date:** August 24, 2026  
**Project:** Atman Cloud RAG-Based Document Q&A System

---

## Document Knowledge Base Tested
- `Product_Manual.pdf`
- `Security_Policy.pdf`
- `Pricing_and_SLA.pdf`
- `API_Reference.pdf`
- `Onboarding_Guide.pdf`
- `Employee_Handbook.pdf`
- `FAQ_Support.pdf`

## Evaluation Matrix

| # | User Question | System's Answer | Sources Cited | Category |
|---|---------------|-----------------|---------------|----------|
| 1 | Hello, how can you help me? | Hello! 👋 I'm your Atman Cloud Document Q&A assistant. How can I help you with our products, policies, or API today? | *(None)* | Greeting / Small Talk |
| 2 | What is the difference in usable storage between the CSP-200 and CSP-400 models? | The CSP‑200 provides 4 TB of usable storage, while the CSP‑400 provides 16 TB of usable storage. The difference between the two models is 12 TB of usable storage [1]. | `Product_Manual.pdf` | Factual Retrieval |
| 3 | How quickly must a suspected data breach be reported, and when must clients be notified? | A suspected data breach must be reported to security@atmancloud.com within 1 hour of discovery. If the breach involves Confidential or Restricted data, the security team must notify the affected clients within 72 hours of the breach being identified [1]. | `Security_Policy.pdf` | Incident Response |
| 4 | What is the API rate limit for the Standard plan, and what happens if I exceed it? | The Standard tier allows 600 requests per minute (with a burst allowance of 100 requests). If you go over this limit, the API returns an HTTP 429 “Too Many Requests” response, and includes a Retry‑After header that tells you how many seconds to wait before sending more requests [1]. | `API_Reference.pdf` | Technical / API |
| 5 | If a Standard tier account exceeds its pooled storage, what are the overage charges? | If a Standard‑tier account uses more than the 500 GB of pooled storage, the excess is billed at $0.08 per GB per month. The overage amount is added to the end‑of‑cycle invoice [1]. | `Pricing_and_SLA.pdf` | Pricing / Billing |
| 6 | How long are deleted files retained in the Recovery Bin? | Deleted files stay in the Recovery Bin for 30 days before they are permanently removed. If the appliance is placed in Legal Hold mode, the files are kept indefinitely until an administrator disables the hold [1]. | `Product_Manual.pdf` | Policy / Retention |
| 7 | As a new remote employee, what equipment stipend am I eligible for? | As a new remote (or hybrid) employee you are eligible for a one‑time $500 home‑office setup stipend, which must be received within your first 90 days. After that, you can receive an annual $200 equipment‑refresh stipend (submitted via expense report with receipts) [1]. | `Employee_Handbook.pdf` | HR / Benefits |
| 8 | What happens to my data if I cancel my subscription? | If you cancel your subscription, your data is kept in a read‑only state for 90 days after the cancellation. After that period it is permanently deleted. During the 90‑day window you can export your data at any time via Account > Export [1]. | `FAQ_Support.pdf` | Support / FAQ |
| 9 | What is the specific monthly cost for an employee to upgrade to the Premium health insurance plan? | I cannot find the answer in the provided documents. The documents state that employees may upgrade at their own cost, but do not specify the exact monthly amount. | *(None)* | **Unanswerable (Edge Case)** |
| 10 | What is the penalty or procedure if an employee loses their hardware security key? | I cannot find the answer in the provided documents. The policy states that a hardware security key is required for Restricted Data access, but does not specify the lost key procedure. | *(None)* | **Unanswerable (Edge Case)** |

---

## Evaluation Notes

1. **Accuracy & Grounding:** The system accurately retrieved specific numerical values (e.g., 4TB vs 16TB, $0.08/GB overage, 1-hour breach reporting) directly from the respective documents.
2. **Citation Precision:** Every answerable question correctly cited the exact source PDF using the `[1]` format, demonstrating that the metadata tracking and strict prompting are functioning perfectly.
3. **Hallucination Prevention (Edge Cases):** For questions 9 and 10, the system correctly refused to answer and did not hallucinate information. It explicitly stated what was *not* in the documents, fulfilling the critical edge-case handling requirement.
4. **Smart UI Behavior:** During testing, the Streamlit UI correctly hid the "Sources" card for the greeting (Question 1) and the unanswerable questions (9–10), keeping the interface clean and preventing user confusion.
5. **Greeting Interceptor:** The system instantly responds to small talk without making unnecessary API calls or awkwardly stating "I cannot find the answer in the provided documents."
