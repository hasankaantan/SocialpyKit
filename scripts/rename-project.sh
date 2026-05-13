#!/usr/bin/env bash
#
# rename-project.sh — one-command rename after cloning from this template.
#
# Replaces every project literal across the tree (env-var prefix, db name,
# docker image, display name, github org) with the values you pass in.
#
# Usage:
#   ./scripts/rename-project.sh <new_slug> "<New Display Name>" <github_org>
#
# Example:
#   ./scripts/rename-project.sh myapi "My API" my-org
#

set -euo pipefail

if [[ $# -ne 3 ]]; then
  cat >&2 <<USAGE
Usage: $0 <new_slug> '<New Display Name>' <github_org>
Example: $0 myapi 'My API' my-org

  new_slug        lowercase, alphanumeric. Used for env-var prefix, db name,
                  docker image. Example: myapi
  New Display     human-readable project name. Example: 'My API'
  github_org      github user or org that will host the renamed repo.
USAGE
  exit 1
fi

new_slug="$1"
new_display="$2"
new_org="$3"
new_upper=$(printf '%s' "$new_slug" | tr '[:lower:]' '[:upper:]')

# Sanity: only run from the repo root.
if [[ ! -f pyproject.toml || ! -d app ]]; then
  echo "Error: must be run from the repository root (no pyproject.toml or app/ here)" >&2
  exit 1
fi

# Detect sed flavour: BSD on macOS expects `-i ''`, GNU on Linux expects `-i`.
if [[ "$(uname)" == "Darwin" ]]; then
  sed_inplace=(sed -i "")
else
  sed_inplace=(sed -i)
fi

# Find every tracked file that contains any of the literals.
mapfile -t files < <(git grep -lE 'socialpykit|SOCIALPYKIT_|SocialpyKit|hasankaantan' || true)

if [[ ${#files[@]} -eq 0 ]]; then
  echo "Nothing to rename — no matching literals found."
  exit 0
fi

cat <<PLAN
Renaming literals:
  socialpykit       -> $new_slug
  SOCIALPYKIT_      -> ${new_upper}_
  SocialpyKit       -> $new_display
  hasankaantan      -> $new_org

Files affected: ${#files[@]}
PLAN

# Apply replacements. Order matters: uppercase prefix first so the shorter
# lowercase slug pattern does not collide with it. Display name before slug
# for the same reason.
for file in "${files[@]}"; do
  "${sed_inplace[@]}" \
    -e "s/SOCIALPYKIT_/${new_upper}_/g" \
    -e "s/SocialpyKit/${new_display}/g" \
    -e "s/socialpykit/${new_slug}/g" \
    -e "s/hasankaantan/${new_org}/g" \
    "$file"
done

cat <<NEXT

Done. Review with: git diff

Manual follow-up:
  - Update [project].authors / maintainers in pyproject.toml if you are not
    Socialbug Apps LLC / Hasan Kaan Tan.
  - Update LICENSE copyright holder to your own name or company.
  - Set your sentry DSN: ${new_upper}_SENTRY_DSN
  - Regenerate ui types if you touched the api: just ui-gen-api
  - Tear down and recreate the dev db so the new credentials take effect:
      docker compose down -v && docker compose up -d db
NEXT
