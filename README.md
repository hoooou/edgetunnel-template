# EdgeTunnel shared Clash/Mihomo template

Generated: 2026-09-21

## Files

- `clash-base.yaml`: base Clash configuration plus high-priority rules.
- `ACL4SSR_Online_Mini_Ai_Merged.ini`: ACL4SSR Mini AI template plus custom AI rule imports and the independent `💻 OpenCode` group.
- `rules/ai-direct.list`: China-based AI site and API rules, always `DIRECT`.
- `rules/ai-proxy.list`: overseas AI site/API/resource rules, via `💬 Ai平台`.

## GFW rule coverage

The template uses ACL4SSR's full `ProxyGFWlist.list` for `🚀 节点选择` instead of the smaller `ProxyLite.list`. Explicit AI rules remain earlier, so OpenAI/Claude-related domains and overseas AI resources such as `huggingface.co` enter `💬 Ai平台`; remaining GFW-listed non-AI sites use `🚀 节点选择`. Domains not matched by any rule still reach `🐟 漏网之鱼`, which can remain set to `🎯 全球直连`.

## Included policy

1. Local/private networks remain direct.
2. UDP whose destination IP is classified as mainland China goes direct.
3. All remaining UDP is rejected. This prevents an unsupported EdgeTunnel VLESS UDP flow from falling through to `DIRECT`.
4. `ip.me` explicitly goes to `🚀 节点选择`, even when `🐟 漏网之鱼` is configured as direct.
5. `opencode.ai` goes to the independent `💻 OpenCode` group.
6. `tech.bitauto.com`, `yiche.com`, `bitauto.com`, and `bitautotech.com` go direct.
7. `opencode.ai` remains in `💻 OpenCode` **before** app process matching; the OpenCode process is not pinned.
8. Dedicated domestic AI Android apps (DeepSeek/Kimi/Doubao/Zhipu/Yuanbao) and domestic AI website/API domains use `DIRECT`.
9. Dedicated overseas AI apps (ChatGPT/Claude/Gemini) and overseas AI website/API domains use `💬 Ai平台`.
10. Other domestic and overseas apps follow the reviewed `my_yml` app process catalog, with `find-process-mode: strict` and domain fallbacks.
11. Multi-model applications (Cursor, OpenCode, Python, Node, browsers) are not pinned to one node group by process; their API domain determines routing.

## Publish

1. Create a public GitHub repository, for example `edgetunnel-template`.
2. Upload both YAML and INI files to the repository root.
3. Edit `ACL4SSR_Online_Mini_Ai_Merged.ini` and replace:

   ```text
   hoooou
   ```

   If the repository is not named `edgetunnel-template`, replace that segment too.
4. Confirm both Raw URLs can be opened without authentication.

## EdgeTunnel backend

Set the custom subscription template URL to:

```text
https://raw.githubusercontent.com/hoooou/edgetunnel-template/main/ACL4SSR_Online_Mini_Ai_Merged.ini
```

Keep these unchecked for the current EdgeTunnel VLESS deployment:

```text
UDP
XUDP
Only output node information
```

## Rule ordering and client update

The generated Mihomo configuration must preserve: LAN/private exceptions -> existing UDP policy -> `opencode.ai` via `💻 OpenCode` -> dedicated AI and other app processes -> custom domestic AI domains via literal `DIRECT` -> custom overseas AI domains via `💬 Ai平台` -> upstream ACL4SSR AI/GFW/general rules. The base file is prepended when `overwrite_original_rules=false`.

Update the EdgeTunnel subscription by asking EdgeTunnel/Subconverter to **regenerate** its subscription using the existing `.ini` URL, then update that same subscription in FlClash. A cached/static converted YAML does not refresh just because the referenced base or rules files changed. Use FlClash connection logs to verify process matching; the client must capture app traffic and provide Android package names.

Avoid blanket rules for shared `googleapis.com`, `aliyuncs.com`, `volcengine.com`, `auth0.com`, `stripe.com` or `sentry.io`: a shared service domain may be used by unrelated apps. The upstream ACL4SSR lists are retained unchanged.

## Note about later duplicate OpenAI rules

The upstream ACL4SSR `ProxyLite.list` also contains some OpenAI domains and sends them to `🚀 节点选择`. The dedicated `AI.list` and `OpenAi.list` rules assigned to `💬 Ai平台` are generated earlier, so Mihomo matches those first. The later ProxyLite duplicates are unreachable for the same OpenAI domains and do not override `💬 Ai平台`. No custom `openai.com` rule is added by this repository.

## Clash Verge local enhancement cleanup

The current local rules enhancement still contains these two rules:

```yaml
- 'DOMAIN-SUFFIX,openai.com,🚀 节点选择'
- 'DOMAIN-SUFFIX,opencode.ai,DIRECT'
```

They would override the shared template's `💬 Ai平台` and `💻 OpenCode` behavior. After switching to the shared template, disable that local rules enhancement or remove those two entries. The company-domain rules are already included in `clash-base.yaml`, so the local enhancement can be disabled entirely.

## Expected leading rules

The final generated Clash/Mihomo profile must put these before the downloaded ACL4SSR rules:

```yaml
- AND,((NETWORK,UDP),(GEOIP,CN)),DIRECT
- NETWORK,UDP,REJECT
- DOMAIN-SUFFIX,opencode.ai,💻 OpenCode
```

LAN/private rules intentionally precede them.
