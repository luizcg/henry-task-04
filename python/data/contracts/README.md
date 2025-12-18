# Test Contract Pairs

This directory contains 5 pairs of contract images (10 images total) for testing the Contract Comparison Agent. Each pair consists of an original contract and its amendment, demonstrating different types of contractual changes across various contract types.

## Contract Pairs Overview

| Contract ID | Type | Original Date | Amendment Date | Changes |
|-------------|------|---------------|----------------|---------|
| contract_001 | Employment | Oct 14, 2024 | May 21, 2025 | 3 sections modified |
| contract_002 | Employment | Aug 16, 2024 | Apr 05, 2025 | 4 sections modified |
| contract_003 | NDA | Oct 27, 2024 | Sep 03, 2025 | 2 sections modified |
| contract_004 | NDA (Scanned) | May 06, 2024 | Apr 22, 2025 | 2 sections modified |
| contract_005 | Lease (Scanned) | Feb 10, 2024 | Feb 04, 2025 | 2 sections modified |

---

## Contract 001 - Employment Agreement

**Type:** Employment Agreement  
**Quality:** Clean digital scan  
**Complexity:** Medium - Multiple compensation and termination changes

### Original Contract
- **Title:** EMPLOYMENT AGREEMENT
- **Date:** October 14, 2024
- **Sections:** 8 sections (Parties, Position, Compensation, Benefits, Termination, Confidentiality, Non-Compete, Governing Law)

### Amendment
- **Title:** AMENDMENT TO EMPLOYMENT AGREEMENT
- **Date:** May 21, 2025

### Changes Made

#### Section 3 - Compensation (Modified)
- **Base Salary:** Increased from $75,000 to $95,000 (26.7% increase)
- **Performance Bonus:** Added 15% annual performance bonus eligibility
- **Impact:** Significant compensation improvement for employee

#### Section 5 - Termination (Modified)
- **Notice Period:** Extended from 30 days to 60 days
- **Severance:** Added severance policy (2 weeks per year of service) for termination without cause
- **Impact:** Enhanced employee protection and longer transition period

#### Section 7 - Non-Compete (Modified)
- **Duration:** Reduced from 12 months to 6 months
- **Geographic Scope:** Narrowed from 50-mile radius to 25-mile radius
- **Exception:** Non-compete waived if terminated without cause
- **Impact:** Less restrictive post-employment obligations

**Test Focus:** Multi-section changes, compensation increases, employee-favorable modifications

---

## Contract 002 - Employment Agreement

**Type:** Employment Agreement  
**Quality:** Clean digital scan  
**Complexity:** High - Four sections modified including benefits

### Original Contract
- **Title:** EMPLOYMENT AGREEMENT
- **Date:** August 16, 2024
- **Sections:** 8 sections

### Amendment
- **Title:** AMENDMENT TO EMPLOYMENT AGREEMENT
- **Date:** April 05, 2025

### Changes Made

#### Section 3 - Compensation (Modified)
- **Base Salary:** Increased from $120,000 to $138,000 (15% increase)
- **Performance Bonus:** Added 15% annual performance bonus eligibility
- **Impact:** Higher-tier compensation package

#### Section 4 - Benefits (Modified)
- **Vacation Days:** Increased from 13 to 18 days annually
- **Carryover Policy:** Added ability to carry over unused vacation
- **Insurance:** Reduced waiting period for health insurance eligibility
- **Impact:** Enhanced work-life balance and benefits package

#### Section 5 - Termination (Modified)
- **Notice Period:** Extended from 30 days to 60 days
- **Severance:** Added severance policy (2 weeks per year of service)
- **Impact:** Improved termination protections

#### Section 7 - Non-Compete (Modified)
- **Duration:** Reduced from 12 months to 6 months
- **Geographic Scope:** Narrowed from 50-mile radius to 25-mile radius
- **Exception:** Non-compete waived if terminated without cause
- **Impact:** More employee-friendly restrictions

**Test Focus:** Complex multi-section changes, benefits modifications, comprehensive package improvements

---

## Contract 003 - Non-Disclosure Agreement

**Type:** Non-Disclosure Agreement (NDA)  
**Quality:** Clean digital scan  
**Complexity:** Medium - Scope expansion and disclosure permissions

### Original Contract
- **Title:** NON-DISCLOSURE AGREEMENT
- **Date:** October 27, 2024
- **Sections:** 8 sections

### Amendment
- **Title:** AMENDMENT TO NON-DISCLOSURE AGREEMENT
- **Date:** September 03, 2025

### Changes Made

#### Section 1 - Definition of Confidential Information (Modified)
- **Scope Expansion:** Added explicit coverage for:
  - Source code and algorithms
  - Product roadmaps
  - Merger & acquisition plans
- **Presumption:** Added presumption that all disclosed information is confidential unless proven otherwise
- **Impact:** Broader protection for disclosing party

#### Section 3 - Permitted Disclosures (Modified)
- **New Exceptions:** Extended permitted disclosures to include:
  - Independent contractors working on related projects
  - Professional advisors (lawyers, accountants)
- **Impact:** More operational flexibility while maintaining confidentiality

**Test Focus:** NDA-specific changes, scope modifications, balancing protection vs. operational needs

---

## Contract 004 - Non-Disclosure Agreement (Scanned Quality)

**Type:** Non-Disclosure Agreement (NDA)  
**Quality:** Realistic scanned document with slight imperfections  
**Complexity:** Medium - Tests OCR capabilities with real-world scan quality

### Original Contract
- **Title:** NON-DISCLOSURE AGREEMENT
- **Date:** May 06, 2024
- **Sections:** 8 sections

### Amendment
- **Title:** AMENDMENT TO NON-DISCLOSURE AGREEMENT
- **Date:** April 22, 2025

### Changes Made

#### Section 1 - Definition of Confidential Information (Modified)
- **Scope Expansion:** Added coverage for:
  - Source code and algorithms
  - Product roadmaps
  - M&A plans
- **Presumption:** Added confidentiality presumption
- **Impact:** Enhanced protection scope

#### Section 6 - Return of Materials (Modified)
- **Archival Exception:** Added provision allowing retention of one archival copy for legal compliance purposes
- **Impact:** Balances return obligations with regulatory requirements

**Test Focus:** Scanned document quality, OCR accuracy, handling realistic image imperfections

---

## Contract 005 - Residential Lease Agreement (Scanned Quality)

**Type:** Residential Lease Agreement  
**Quality:** Realistic scanned document  
**Complexity:** Medium - Financial terms and utility responsibilities

### Original Contract
- **Title:** RESIDENTIAL LEASE AGREEMENT
- **Date:** February 10, 2024
- **Sections:** 8 sections

### Amendment
- **Title:** AMENDMENT TO RESIDENTIAL LEASE AGREEMENT
- **Date:** February 04, 2025

### Changes Made

#### Section 4 - Security Deposit (Modified)
- **Deposit Amount:** Reduced from $7,276 to $5,457 (25% reduction)
- **Interest-Bearing:** Added requirement for deposit to be held in interest-bearing account
- **Return Period:** Shortened from 30 days to 21 days
- **Itemization:** Added requirement for itemized deductions
- **Impact:** More tenant-friendly deposit terms

#### Section 5 - Utilities (Modified)
- **Responsibility Shift:** Landlord now covers water, sewer, and trash (previously tenant responsibility)
- **Unusual Costs:** Added provision for sharing unusual utility costs exceeding baseline
- **Impact:** Reduced tenant monthly expenses, clearer cost allocation

**Test Focus:** Lease-specific terms, financial modifications, utility responsibility changes, scanned quality

---

## Testing Guidelines

### Image Quality Variations

1. **Contracts 001-003:** Clean digital scans
   - High resolution
   - Clear text
   - Minimal artifacts
   - Tests baseline parsing accuracy

2. **Contracts 004-005:** Realistic scanned documents
   - Slight imperfections
   - Real-world scan quality
   - Tests OCR robustness
   - Validates handling of typical document quality

### Contract Type Coverage

- **Employment Agreements (2):** Compensation, benefits, termination, non-compete
- **NDAs (2):** Confidentiality scope, permitted disclosures, return obligations
- **Lease Agreement (1):** Financial terms, utilities, deposits

### Change Type Coverage

- **Compensation Changes:** Salary increases, bonus additions
- **Benefit Modifications:** Vacation, insurance, severance
- **Restrictive Covenants:** Non-compete duration and scope
- **Confidentiality Scope:** Definition expansions, exceptions
- **Financial Terms:** Deposits, utility responsibilities
- **Operational Terms:** Notice periods, return obligations

### Expected Agent Behavior

The Contract Comparison Agent should:

1. **Parse both documents** with >90% accuracy
2. **Identify all modified sections** listed in metadata
3. **Distinguish change types** (additions, deletions, modifications)
4. **Generate accurate summaries** explaining business impact
5. **Handle scanned quality** without significant accuracy degradation
6. **Maintain document structure** in extracted text

### Running Tests

```bash
# Test individual contract pair
python -m src.main compare \
  data/contracts/contract_001/contract_original.png \
  data/contracts/contract_001/contract_amendment1.png \
  --pretty

# Test scanned document quality
python -m src.main compare \
  data/contracts/contract_004/contract_original_scanned.png \
  data/contracts/contract_004/contract_amendment1_scanned.png \
  --pretty
```

### Validation

Compare agent output against `metadata.json` in each contract directory to verify:
- All changed sections are detected
- Change descriptions are accurate
- No hallucinated changes (false positives)
- Proper handling of different contract types

---

## Metadata Files

Each contract directory contains a `metadata.json` file with:
- Contract type
- Original and amendment titles/dates
- Section structure
- Ground truth changes (section, type, description)

Use these files to validate agent accuracy and create automated test assertions.
