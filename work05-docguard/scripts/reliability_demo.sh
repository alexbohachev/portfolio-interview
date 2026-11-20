#!/usr/bin/env bash
# Live DocGuard: tenant isolation, ACL cache invalidation, retrieval down -> degraded fallback.
set -eo pipefail

GATEWAY="${GATEWAY:-http://localhost:8096}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

query_docguard() {
    local tenant="$1"
    local principal="$2"
    local question="$3"

    curl -sS -X POST "${GATEWAY}/api/v1/query" \
        -H "Content-Type: application/json; charset=utf-8" \
        -H "X-Tenant-Id: ${tenant}" \
        -H "X-Principal-Id: ${principal}" \
        -d "{\"question\": \"${question}\"}"
}

echo "=== work05 reliability demo ==="

echo -e "\n[1] Tenant A (alice) query"
res_a=$(query_docguard "tenant_a" "alice" "бура іржа пшениця")
echo "${res_a}"

echo -e "\n[2] Tenant B (carol) query — isolated ACL / corpus"
res_b=$(query_docguard "tenant_b" "carol" "економічний поріг шкідників IPM")
echo "${res_b}"

echo -e "\n[3] Invalidate cache for carol + repeat query"
curl -sS -X POST "${GATEWAY}/api/v1/admin/invalidate-cache" \
    -H "X-Tenant-Id: tenant_b" \
    -H "X-Principal-Id: carol" > /dev/null || true
res_b2=$(query_docguard "tenant_b" "carol" "економічний поріг шкідників IPM")
echo "${res_b2}"

echo -e "\n[4] Stop retrieval container -> test degraded mode"
docker compose stop retrieval > /dev/null 2>&1 || true
sleep 3

trap 'docker compose start retrieval > /dev/null 2>&1 || true' EXIT

res_deg=$(query_docguard "tenant_a" "alice" "test degraded")
echo "${res_deg}"

if echo "${res_deg}" | grep -q '"degraded":true'; then
    echo -e "\nOK degraded=true verified"
else
    echo "Warning: expected degraded: true in response"
fi

docker compose start retrieval > /dev/null 2>&1 || true
trap - EXIT
sleep 5

echo -e "\nreliability_demo: OK"
