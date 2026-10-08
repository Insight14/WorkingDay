from typing import Dict, Any, List

def compute_field_accuracy(ground_truth: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, float]:
    """
    Computes exact match and field-level accuracy metrics between candidate and ground truth.
    """
    matches = 0
    total = 0

    # 1. Name fields
    for k in ["given", "family"]:
        gt_val = ground_truth.get("name", {}).get(k)
        cand_val = candidate.get("name", {}).get(k)
        if isinstance(cand_val, dict):
            cand_val = cand_val.get("value")
        total += 1
        if (gt_val or "").strip().lower() == (cand_val or "").strip().lower():
            matches += 1

    # 2. Contact fields
    for k in ["email", "phone"]:
        gt_val = ground_truth.get("contact", {}).get(k)
        cand_val = candidate.get("contact", {}).get(k)
        if cand_val is None and k in candidate:
            cand_val = candidate.get(k)
        if isinstance(cand_val, dict):
            cand_val = cand_val.get("value")
        total += 1
        if (gt_val or "").strip() == (cand_val or "").strip():
            matches += 1

    # 3. Address fields
    for k in ["line1", "city", "state", "postal"]:
        gt_val = ground_truth.get("address", {}).get(k)
        cand_val = candidate.get("address", {}).get(k)
        if isinstance(cand_val, dict):
            cand_val = cand_val.get("value")
        total += 1
        if gt_val is None and cand_val is None:
            matches += 1
        elif gt_val and cand_val and gt_val.strip().lower() == cand_val.strip().lower():
            matches += 1

    # 4. Links
    for k in ["linkedin", "github"]:
        gt_val = ground_truth.get("links", {}).get(k)
        cand_val = candidate.get("links", {}).get(k)
        if isinstance(cand_val, dict):
            cand_val = cand_val.get("value")
        total += 1
        if gt_val is None and cand_val is None:
            matches += 1
        elif gt_val and cand_val and (gt_val in cand_val or cand_val in gt_val):
            matches += 1

    # 5. Education count & primary school
    gt_edu = ground_truth.get("education", [])
    cand_edu = candidate.get("education", [])
    total += 1
    if len(gt_edu) == len(cand_edu):
        matches += 1

    if gt_edu and cand_edu:
        total += 1
        gt_school = gt_edu[0].get("school", "")
        cand_school = cand_edu[0].get("school")
        if isinstance(cand_school, dict):
            cand_school = cand_school.get("value", "")
        if gt_school and cand_school and (gt_school.lower() in cand_school.lower() or cand_school.lower() in gt_school.lower()):
            matches += 1

    # 6. Experience count & company integrity
    gt_exp = ground_truth.get("experience", [])
    cand_exp = candidate.get("experience", [])
    total += 1
    if len(gt_exp) == len(cand_exp):
        matches += 1

    # Multiword company preservation check
    total += 1
    gt_companies = {e.get("company", "").lower() for e in gt_exp if e.get("company")}
    cand_companies = set()
    for e in cand_exp:
        comp = e.get("company")
        if isinstance(comp, dict):
            comp = comp.get("value")
        if comp:
            cand_companies.add(comp.lower())

    if gt_companies.issubset(cand_companies) or len(gt_companies.intersection(cand_companies)) == len(gt_companies):
        matches += 1

    accuracy = (matches / total) * 100.0 if total > 0 else 0.0
    return {
        "matches": matches,
        "total_fields": total,
        "accuracy_pct": round(accuracy, 1)
    }
