# GreenLoopAI — Extended Producer Responsibility (EPR) Module

## 1. What is Extended Producer Responsibility (EPR)?
Extended Producer Responsibility is an environmental policy approach under which producers, importers, and brand owners (PIBOs) bear financial and operational responsibility for the post-consumer management of their products.

---

## 2. Regulatory Standards Supported
GreenLoopAI aligns with regulatory guidelines (including Central Pollution Control Board (CPCB) and International Circularity Standards):

| Waste Material Stream | Recyclability Multiplier | Regulatory Tier | Applicable Standard |
| :--- | :--- | :--- | :--- |
| **PET Rigid Plastic** | `1.2` | `TIER_1_HIGH` | CPCB EPR Guidelines (Category I - Rigid) |
| **HDPE Rigid Plastic** | `1.1` | `TIER_1_HIGH` | CPCB EPR Guidelines (Category I - Rigid) |
| **LDPE Flexible Plastic** | `0.9` | `TIER_2_MEDIUM` | CPCB EPR Guidelines (Category II - Flexible) |
| **Aluminum & Metals** | `1.5` | `TIER_1_HIGH` | Industrial Metal Recovery & EPR Norms |
| **Cardboard & Packaging** | `0.85` | `TIER_2_MEDIUM` | Paper & Packaging Circularity Standards |
| **E-Waste & Electronics** | `2.0` | `TIER_1_HIGH` | E-Waste Management Rules |
| **Glass Containers** | `1.1` | `TIER_1_HIGH` | Glass Packaging Circularity Norms |
| **Textiles & Biomass** | `0.75` | `TIER_3_STANDARD` | Textile & Circular Economy Framework |

---

## 3. EPR Credit Calculation Formula
$$\text{EPR Credits} = \text{Weight (kg)} \times \text{Material Multiplier} \times \left(\frac{\text{Verification Score}}{100}\right)$$

### Example
* **Item**: 0.08 kg PET Bisleri Water Bottle
* **Verification Score**: $86.5\%$
* **Calculation**: $0.08 \text{ kg} \times 1.2 \times 0.865 = \mathbf{0.083 \text{ EPR Credits}}$
* **Evidence Hash**: `EPR-20261005-7F9B1E4A`

---

## 4. Producer & Municipal Audit Trail
* Every generated EPR credit is linked to an immutable SHA-256 evidence record.
* Municipalities can query total collected volumes per brand for municipal compliance reporting.
* Brand producers can inspect and export digital proof of recovery for official compliance filings.
