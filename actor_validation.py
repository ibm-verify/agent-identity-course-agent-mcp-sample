# Copyright IBM Corp. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

"""Validate delegated actors against the stable registry AgentID."""
from typing import Any, Dict
from config import settings


def validate_actor(claims: Dict[str, Any]) -> Dict[str, Any]:
    expected = settings.agent_id
    if not expected:
        return {"valid": False, "reason": "AGENT_ID is not configured; set the registry ID in .env and restart"}
    act = claims.get("act")
    actor_sub = act.get("sub") if isinstance(act, dict) else None
    if not isinstance(actor_sub, str) or not actor_sub:
        return {"valid": False, "reason": "Missing delegated actor act.sub"}
    if actor_sub != expected:
        return {"valid": False, "reason": f"Invalid actor. Expected AgentID '{expected}', token act.sub={actor_sub}"}
    return {"valid": True}
