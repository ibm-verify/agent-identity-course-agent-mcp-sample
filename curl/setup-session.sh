# Copyright IBM Corp. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0

# Source this file in Bash or zsh from the project root.
# This helper checks exact HTTP status codes; it does not follow redirects.
umask 077
mkdir -p .local
chmod 700 .local

setup_request() {
  local expected="$1" output="$2" http_status
  shift 2
  case "${TENANT:-}" in
    https://*) ;;
    *) printf 'Set TENANT to an HTTPS origin before continuing.\n' >&2; return 1 ;;
  esac
  if ! http_status=$(curl --silent --show-error --connect-timeout 15 --max-time 60 \
      --output "$output" --write-out '%{http_code}' "$@"); then
    printf 'Transport error; stop here.\n' >&2
    return 1
  fi
  printf 'HTTP %s (expected %s)\n' "$http_status" "$expected"
  if [ "$http_status" != "$expected" ]; then
    printf 'Stop here. Response saved to %s. Check the error without sharing tokens or secrets.\n' "$output" >&2
    return 1
  fi
}

setup_field() {
  jq -er --arg key "$2" '.[$key] | select(type == "string" and length > 0)' "$1"
}
