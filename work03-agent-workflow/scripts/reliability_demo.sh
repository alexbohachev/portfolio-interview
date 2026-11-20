#!/usr/bin/env bash
# Live workflow: idempotent retry + conflict on payload change.
set -eo pipefail

BASE_URL="${BASE_URL:-http://localhost:8083}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

post_app() {
    local key="$1"
    local area="$2"

    curl -sS -w "\n%{http_code}" -X POST "${BASE_URL}/api/v1/applications" \
        -H "Content-Type: application/json" \
        -d "{\"tenantId\": \"tenant_a\", \"idempotencyKey\": \"${key}\", \"equipmentType\": \"sprayer\", \"areaHa\": ${area}}"
}

echo "=== work03 reliability demo ==="
echo "(Make sure application is running: ./gradlew bootRun or docker compose)"

KEY="reliability-demo-$(date +%s%N | cut -b1-12)"

echo -e "\n[1] First submit (idempotency key: ${KEY})"
out1=$(post_app "${KEY}" 10.0 || true)
code1=$(echo "${out1}" | tail -n1)
echo "HTTP status: ${code1}"

echo -e "\n[2] Retry same idempotency key (safe idempotent retry)"
out2=$(post_app "${KEY}" 10.0 || true)
code2=$(echo "${out2}" | tail -n1)
echo "HTTP status: ${code2} (expected 200, single external effect in DB)"

echo -e "\n[3] Same key, different payload -> conflict detection"
out3=$(post_app "${KEY}" 99.0 || true)
code3=$(echo "${out3}" | tail -n1)
if [ "${code3}" = "409" ]; then
    echo "OK: HTTP 409 idempotency conflict detected"
else
    echo "HTTP status: ${code3} (expected 409 if API up and payload altered)"
fi

echo -e "\nOffline fault matrix:"
python scripts/demo_offline.py

echo -e "\nreliability_demo: OK"
