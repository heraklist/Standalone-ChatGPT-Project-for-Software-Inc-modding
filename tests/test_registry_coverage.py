import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.verify_repo import KNOWLEDGE_FILES

REGISTRY = ROOT / "production/knowledge/17_EVIDENCE_REGISTRY.json"
OWNER_DOCUMENTS = {name for name in KNOWLEDGE_FILES if name.endswith(".md")}


def _registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_every_claim_owner_document_is_a_canonical_knowledge_file():
    claims = _registry()["claims"]
    for cid, claim in claims.items():
        owner = claim.get("owner_document")
        assert owner in OWNER_DOCUMENTS, f"claim {cid}: owner_document {owner!r} is not one of the 18 knowledge files"


def test_hard_generation_rules_cite_evidence():
    claims = _registry()["claims"]
    for cid, claim in claims.items():
        if claim.get("hard_generation_rule"):
            refs = claim.get("evidence_refs")
            assert isinstance(refs, list) and refs, f"claim {cid}: hard_generation_rule must cite at least one evidence ref"


def test_every_source_role_is_schema_recognized():
    data = _registry()
    schema = json.loads((ROOT / "schemas/evidence-registry.schema.json").read_text(encoding="utf-8"))
    allowed_roles = set(schema["properties"]["sources"]["additionalProperties"]["properties"]["source_role"]["enum"])
    for sid, source in data["sources"].items():
        assert source["source_role"] in allowed_roles, f"source {sid}: unrecognized source_role {source['source_role']!r}"
