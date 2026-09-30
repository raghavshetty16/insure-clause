"""Generate the three sample policy wordings used for development.

These are NOT real policies. They are written to look like retail health
policy wordings so that the pipeline can be built and tested before the real
insurer PDFs are dropped in. Replace data/policies with the genuine downloads
and update manifest.json; nothing else has to change.

Run:  python scripts/make_sample_policies.py
Then render the HTML to PDF (see README).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT_DIR = ROOT / "data" / "policies"

POLICIES = [
    {
        "policy_id": "sample-securehealth",
        "insurer": "Sample General Insurance",
        "product": "SecureHealth Plus",
        "file": "sample_securehealth",
        "room_rent": "1% of the sum insured per day",
        "ped_months": 36,
        "specific_months": 24,
        "cataract": "40,000 per eye",
        "knee": "1,50,000",
        "copay": "20% of every admissible claim where the insured person's age at "
                 "entry was above 60 years",
    },
    {
        "policy_id": "sample-arogyashield",
        "insurer": "Bharat Health Assurance",
        "product": "ArogyaShield",
        "file": "sample_arogyashield",
        "room_rent": "Rs. 5,000 per day",
        "ped_months": 48,
        "specific_months": 24,
        "cataract": "30,000 per eye",
        "knee": "2,00,000",
        "copay": "15% of every admissible claim where the insured person is above "
                 "65 years of age at the date of admission",
    },
    {
        "policy_id": "sample-totalcare",
        "insurer": "Meridian Insurance",
        "product": "TotalCare Gold",
        "file": "sample_totalcare",
        "room_rent": "2% of the sum insured per day",
        "ped_months": 24,
        "specific_months": 12,
        "cataract": "50,000 per eye",
        "knee": "2,50,000",
        "copay": "no co-payment is applicable under this policy",
    },
]

TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{insurer} - {product}</title>
<style>
  @page {{ size: A4; margin: 22mm 20mm; }}
  body {{ font-family: Georgia, serif; font-size: 10.5pt; line-height: 1.55; color: #111; }}
  h1 {{ font-size: 15pt; text-align: center; margin-bottom: 2px; }}
  .sub {{ text-align: center; font-size: 10pt; color: #444; margin-bottom: 4px; }}
  .warn {{ text-align: center; font-size: 9pt; color: #777; margin-bottom: 22px;
           border: 1px solid #bbb; padding: 4px; }}
  h2 {{ font-size: 11.5pt; margin-top: 20px; page-break-after: avoid; }}
  h3 {{ font-size: 10.8pt; margin-top: 13px; page-break-after: avoid; }}
  p {{ margin: 0 0 8px; text-align: justify; }}
  ul {{ margin: 0 0 8px; padding-left: 20px; }}
  li {{ margin-bottom: 4px; }}
</style></head><body>

<h1>{insurer}</h1>
<div class="sub">{product} &mdash; Policy Wording</div>
<div class="warn">SAMPLE DOCUMENT. Generated for development and testing only.
This is not a real insurance policy.</div>

<h2>1 DEFINITIONS</h2>

<h3>1.1 Hospitalisation</h3>
<p>Hospitalisation means admission in a Hospital for a minimum period of twenty four
consecutive hours, except for day care procedures where such limit is not applied.</p>

<h3>1.2 Pre-Existing Disease</h3>
<p>Pre-Existing Disease means any condition, ailment, injury or disease that is
diagnosed by a physician within forty eight months prior to the effective date of
the policy issued by the insurer, or for which medical advice or treatment was
recommended by, or received from, a physician within forty eight months prior to
the effective date of the policy.</p>

<h3>1.3 Sum Insured</h3>
<p>Sum Insured means the pre-defined limit specified in the policy schedule. It
represents the maximum liability of the Company for any and all claims made during
the policy year in respect of the insured person.</p>

<h3>1.4 Co-Payment</h3>
<p>Co-Payment means a cost sharing requirement under which the insured person bears
a specified percentage of the admissible claim amount. A co-payment does not reduce
the Sum Insured.</p>

<h2>2 SCOPE OF COVER</h2>

<h3>2.1 In-Patient Treatment</h3>
<p>The Company shall indemnify the medical expenses incurred by the insured person
for hospitalisation during the policy period, following an illness or injury that
occurs during the policy period, up to the Sum Insured specified in the schedule.</p>

<h3>2.2 Pre and Post Hospitalisation</h3>
<p>Medical expenses incurred for a period of thirty days immediately before the date
of admission, and sixty days immediately after the date of discharge, are payable
provided the hospitalisation claim itself has been admitted.</p>

<h2>3 ROOM RENT AND ASSOCIATED CHARGES</h2>

<h3>3.1 Room Rent Limit</h3>
<p>The eligible room rent under this policy is {room_rent}. Where the insured person
occupies a room whose rent exceeds this eligible limit, the Company shall be liable
only for a proportionate share of the associated medical expenses, in the ratio that
the eligible room rent bears to the room rent actually charged.</p>

<h3>3.2 Associated Charges</h3>
<p>Associated charges for the purpose of clause 3.1 include surgeon fees, anaesthetist
fees, operation theatre charges, consultant visit charges and nursing charges. The
cost of pharmacy, implants and diagnostics is not subject to proportionate deduction.</p>

<h2>4 WAITING PERIODS</h2>

<h3>4.1 Initial Waiting Period</h3>
<p>Expenses related to the treatment of any illness within thirty days from the first
policy commencement date shall be excluded, except claims arising due to an accident.
This exclusion does not apply if the insured person has continuous coverage for more
than twelve months.</p>

<h3>4.2 Specific Waiting Period</h3>
<p>Expenses related to the treatment of the following listed conditions, surgeries and
treatments shall be excluded until the expiry of {specific_months} months of continuous
coverage after the date of inception of the first policy with the Company:</p>
<ul>
  <li>Cataract and diseases of the eye lens</li>
  <li>Total or partial replacement of a knee or hip joint</li>
  <li>Hernia of all types, hydrocele and fistula in ano</li>
  <li>Benign prostatic hypertrophy</li>
  <li>Hysterectomy and diseases of the uterus</li>
  <li>Calculi in the urinary and biliary systems</li>
  <li>Varicose veins and varicose ulcers</li>
</ul>

<h3>4.3 Pre-Existing Disease Waiting Period</h3>
<p>Expenses related to the treatment of a pre-existing disease and its direct
complications shall be excluded until the expiry of {ped_months} months of continuous
coverage after the date of inception of the first policy with the Company.</p>

<h2>5 PERMANENT EXCLUSIONS</h2>

<h3>5.1 Excluded Treatments</h3>
<p>The Company shall not be liable to make any payment under this policy in respect of
any expenses incurred in connection with or in respect of the following. These are
permanent exclusions and are not subject to any waiting period:</p>
<ul>
  <li>Cosmetic or plastic surgery, unless required as part of medically necessary
      treatment to remove a direct consequence of an accident or burn</li>
  <li>Dental treatment and surgery of any kind, unless requiring hospitalisation
      following an accident</li>
  <li>Treatment for obesity or weight control, including bariatric surgery</li>
  <li>Expenses related to any treatment necessitated due to participation in
      hazardous or adventure sports</li>
  <li>Treatment for alcoholism, drug or substance abuse</li>
  <li>Any expenses incurred on external congenital anomalies</li>
  <li>Cost of spectacles, contact lenses and hearing aids</li>
  <li>Unproven treatments and experimental procedures</li>
</ul>

<h2>6 SUB-LIMITS ON SPECIFIC PROCEDURES</h2>

<h3>6.1 Table of Benefits</h3>
<p>The Company's liability in respect of the following procedures is capped at the
amounts stated below, irrespective of the Sum Insured:</p>
<ul>
  <li>Cataract surgery: Rs. {cataract}</li>
  <li>Total knee replacement: Rs. {knee} per knee</li>
  <li>Maternity expenses: Rs. 50,000 for normal delivery and Rs. 75,000 for
      caesarean section, subject to the maternity waiting period</li>
  <li>Ambulance charges: Rs. 3,000 per hospitalisation</li>
</ul>

<h3>6.2 Modern Treatment Methods</h3>
<p>Expenses for modern treatment methods including robotic surgery, deep brain
stimulation and stem cell therapy are payable up to fifty percent of the Sum Insured.</p>

<h2>7 CO-PAYMENT</h2>

<h3>7.1 Applicable Co-Payment</h3>
<p>Under this policy, {copay}. The co-payment is applied to the admissible claim amount
after all other deductions under this policy have been made.</p>

<h2>8 CLAIMS PROCEDURE</h2>

<h3>8.1 Notification</h3>
<p>Notice of any claim must be given to the Company within twenty four hours of
admission in the case of emergency hospitalisation, and at least forty eight hours
prior to admission in the case of planned hospitalisation.</p>

<h3>8.2 Documents</h3>
<p>The claim form, discharge summary, itemised hospital bill, payment receipts,
investigation reports and the treating doctor's certificate must be submitted to the
Company within fifteen days of discharge.</p>

</body></html>
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = []
    for policy in POLICIES:
        html = TEMPLATE.format(**policy)
        html_path = OUT_DIR / f"{policy['file']}.html"
        html_path.write_text(html, encoding="utf-8")
        manifest.append(
            {
                "policy_id": policy["policy_id"],
                "insurer": policy["insurer"],
                "product": policy["product"],
                "file": f"{policy['file']}.pdf",
            }
        )
        print(f"wrote {html_path.name}")

    manifest_path = OUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {manifest_path.name}")


if __name__ == "__main__":
    main()
