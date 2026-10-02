import hashlib
import json


def digest(document):
    serialized = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def contract_digest(feature, evidence):
    evidence_by_id = {item["id"]: item for item in evidence}
    fields = ("id", "domain", "capabilityType", "actors", "inputs", "outputs", "preconditions")
    contract = {field: feature[field] for field in fields}
    if "admitted" in feature:
        contract["admitted"] = feature["admitted"]
    for field in ("actors", "inputs", "outputs", "preconditions"):
        contract[field] = sorted(contract[field])
    contract["behaviors"] = sorted(feature["behaviors"], key=lambda behavior: behavior["id"])
    contract["evidence"] = [evidence_by_id[identifier] for identifier in sorted(feature["evidenceRefs"])]
    return digest(contract)