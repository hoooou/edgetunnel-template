# EdgeTunnel shared Clash/Mihomo template

Generated: 2026-09-21

## Files

- `clash-base.yaml`: base Clash configuration plus high-priority rules.
- `ACL4SSR_Online_Mini_Ai_Merged.ini`: ACL4SSR Mini AI template plus custom AI rule imports and the independent `💻 OpenCode` group.
- `rules/ai-direct.list`: China-based AI site and API rules, always `DIRECT`.
- `rules/ai-proxy.list`: overseas AI site/API/resource rules, via `💬 Ai平台`.
- `rules/app-direct.list`: domestic apps and domestic dedicated AI app processes; converted into literal `DIRECT` rules.
- `rules/app-ai-proxy.list`: dedicated overseas AI processes via `💬 Ai平台`.
- `rules/app-proxy.list`: other overseas app processes via `🚀 节点选择`.
- `rules/app-direct-domains.list`: domestic application domains from `my_yml`.
- `rules/app-proxy-domains.list`: overseas application domains from `my_yml`.
- `rules/domestic-services.list`: general domestic services from `my_yml`.
- `rules/overseas-services.list`: general overseas services from `my_yml`.
- `rules/explicit-direct.list` / `rules/explicit-proxy.list`: original explicit routing exceptions.
- `scripts/validate_template.py`: standard-library static checks for rule order, DNS coverage and conflicts.

## GFW rule coverage

The template uses ACL4SSR's lightweight `ProxyLite.list` for `🚀 节点选择`, replacing the much larger `ProxyGFWlist.list`. This **only reduces the imported generic GFW list** and does not change DNS, Fake-IP, IPv6, UDP, application or AI policies. Explicit AI rules still take priority; other overseas services use the existing app/service lists or `🐟 漏网之鱼` (which defaults to `🚀 节点选择`). After Subconverter regenerates the subscription, compare mobile FlClash behavior under the same node/network. A smaller rule list alone is not evidence that DNS timeouts or Cloudflare Worker egress restrictions are fixed.

## Mobile DNS-resolution A/B test (2026-10-14)

The final country-IP fallback has been changed from `ruleset=🎯 全球直连,[]GEOIP,CN` to `ruleset=🎯 全球直连,[]GEOIP,CN,no-resolve`. This prevents the country-IP match itself from initiating a domain DNS lookup solely to classify an unknown hostname. Existing resolved-IP traffic can still match CN; unmatched domain traffic can reach `🐟 漏网之鱼` (defaults to `🚀 节点选择`), including some Chinese domains not in the earlier direct lists. The 71 dedicated overseas AI DNS policies were **subsequently removed** in a separate test; Quad9/OpenDNS fallback, the `opencode.ai` exception, corporate split DNS, UDP and proxy groups remain unchanged. This is **not** a fix for foreign DoH connection timeouts or Cloudflare entrance TCP resets.

For the A/B test, have EdgeTunnel/Subconverter regenerate the subscription, refresh/restart FlClash on Android, and verify the emitted YAML includes `GEOIP,CN,🎯 全球直连,no-resolve`. Then compare the same selected node over the same mobile network against the prior profile. To rollback only this experiment, restore `ruleset=🎯 全球直连,[]GEOIP,CN` in the `.ini`.

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

## Node-group selection

**Manual delay tests:** The legacy Clash for Windows `cfw-latency-url` and `cfw-latency-timeout` properties have been deleted. Subconverter groups are all `select`; no `url-test` or periodic health-check is introduced.

FlClash keeps the manual latency probe URL as an **application setting**, not a universal subscription property. In FlClash settings, find **测速链接 / Test URL** and set it to `https://www.gstatic.com/generate_204` instead of a Cloudflare-hosted 204 probe. After that, the user may trigger a **manual** delay test in the proxies screen. FlClash reads this setting and passes it to the core independently of the downloaded Clash YAML. Other clients such as Shadowrocket need to configure their own test URL if they support it.

Mihomo also supports a `url` property on a `select` policy group, and setting `interval: 0` disables periodic health checks, but the Subconverter `.ini` group declarations in this repository do **not** inject group-level `url` metadata. We do not add a potentially ineffective or incompatible field to the source template, nor claim this would override FlClash's client-level setting. A group-level probe can be added later only after verifying the actual generated Mihomo YAML and target clients.

The former `♻️ 自动选择` url-test group has been removed. `🚀 节点选择`, `💬 Ai平台`, `💻 OpenCode`, `🎯 全球直连`, `🛑 全球拦截`, and `🐟 漏网之鱼` remain. Select EdgeTunnel nodes manually under `🚀 节点选择` or the relevant AI/OpenCode group. No automatic health-based node switching group is generated by this template.

Default behavior: `💬 Ai平台`, `💻 OpenCode`, and `🐟 漏网之鱼` select `🚀 节点选择` first. Inside `🚀 节点选择`, actual proxy nodes appear **before** the optional `DIRECT` entry, so first-time/default selection is not direct. `🎯 全球直连` still defaults to `DIRECT`, and `🛑 全球拦截` defaults to `REJECT`. A client may preserve a previously stored manual selection; verify it after refreshing.

## Backfilled application and service rules

The source `hoooou/my_yml/优选配置.yaml` includes four explicit domain lists (43 domestic-app, 34 overseas-app, 42 domestic-service, and 84 overseas-service entries) and 24 standalone exceptions. These are now represented in six Surge-style rule lists loaded by Subconverter, after high-priority OpenCode/AI rules and before generic ACL4SSR media/GFW/China lists. Existing app process routing remains ahead of the domain lists.

- Restored entries: **43 + 34 + 42 + 83** application/service domain rules, **17** explicit direct exceptions and **5** explicit proxy exceptions.
- `googleapis.com` is deliberately not blanket-proxied, as it is a shared service provider domain. Dedicated Google AI API rules stay under `💬 Ai平台`; `googleapis.cn` remains proxied.
- Two original standalone office domain exceptions, `yiche.com` and `bitautotech.com`, were already in `clash-base.yaml` and are therefore not duplicated in `explicit-direct.list`.
- Microsoft and OneDrive retain explicit DIRECT overrides. Copilot and other foreign AI endpoints still follow the earlier `💬 Ai平台` rules.
- Sources may overlap intentionally; Mihomo uses the first matched rule. No corporate DNS, Fake-IP exceptions, general DNS policy, UDP restrictions, node definitions or select-group defaults were modified.
- Subconverter must actually fetch these six ruleset files when **regenerating** the full subscription. Merely refreshing a cached/static generated YAML may not include them. The repository static checks cannot prove conversion or real FlClash/Shadowrocket behavior.

## Rule ordering and client update

The generated Mihomo configuration must preserve: LAN/private exceptions -> existing UDP policy -> `opencode.ai` via `💻 OpenCode` -> app process lists from Subconverter (`app-direct`, `app-ai-proxy`, `app-proxy`) -> dedicated domestic AI and overseas AI domains -> restored service exceptions and app/service domains -> generic ACL4SSR media/GFW/China rules. The base file is prepended when `overwrite_original_rules=false`.

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

## Phase 2: Mihomo DNS (2026-10-13)

The base profile now enables `dns.enhanced-mode: fake-ip` and split DNS, based on the principles in `hoooou/my_yml` including its **company-only DNS exceptions** for use on the corporate network.

- Default DNS and domestic AI policy use Chinese HTTPS DNS (`dns.alidns.com` and `doh.pub`). Corporate split-horizon DNS and its Fake-IP exceptions are unchanged.
- **Overseas AI DNS (71 domains):** no dedicated `nameserver-policy` entries. Preserve `fake-ip` and the `💬 Ai平台` routing rules so supported domain-based proxy traffic can proceed without the former forced per-domain DoH override. When a real foreign IP is needed, the **unchanged global DNS** (domestic `nameserver` plus Quad9/OpenDNS `fallback` routed via `🚀 节点选择`) can still be used. This does **not** guarantee immunity to DNS pollution or overseas DoH timeout.
- Other overseas domains use the same two non-Cloudflare DoH upstreams for fallback HTTPS DNS via `🚀 节点选择` when the geo-IP filter selects fallback. Whether the fallback is selected depends on Mihomo's filter, not a guaranteed ordered failover.
- Proxy-node hostnames use domestic bootstrap resolvers to prevent a proxy-resolution cycle. Direct-domain resolution uses domestic HTTPS DNS; `direct-nameserver-follow-policy: true` follows explicit AI/company overrides.
- Office domains (`*.tech.bitauto.com`, `*.yiche.com`, `*.bitauto.com`, `*.bitautotech.com`) bypass fake-IP and are resolved via corporate DNS servers `192.168.70.49` and `192.168.70.1` (as in `hoooou/my_yml`). These names are also explicitly routed `DIRECT`. This requires the company Wi-Fi/LAN or a company VPN with reachability to those DNS servers. Offsite without VPN, these internal sites may fail to resolve, intentionally avoiding the public-DNS result that redirects to a public parent domain.
- DNS AAAA answers are disabled (`dns.ipv6: false`) to reduce IPv6 direct-route surprises; the pre-existing IPv6 LAN/CIDR rules remain. This is not an absolute leak prevention guarantee.
- Existing EdgeTunnel UDP rules remain **unchanged**. Overseas DoH uses HTTPS over TCP via an existing proxy group; normal overseas UDP stays rejected.


**2026-10-13 overseas DNS test:** Regenerate the full EdgeTunnel subscription, clear DNS cache/restart Mihomo, and test OpenCode (direct CN DoH exception), ChatGPT, Claude, Gemini (foreign DoH via `🚀 节点选择`), and one ordinary overseas domain (foreign DoH fallback via `🚀 节点选择`). If the foreign DoH still times out, changing its suffix from `#💬 Ai平台` to `#🚀 节点选择` is insufficient when both groups point to the same EdgeTunnel node; inspect real proxy-node connectivity rather than switching to untrusted domestic DNS for overseas AI.


**DNS policy correction 2026-10-14:** Previously, 71 overseas AI DNS rules used Quad9/OpenDNS via `🚀 节点选择` to reduce DNS poisoning risk. They were later removed as a **separate mobile stability test** after `GEOIP,CN,no-resolve`, to avoid per-domain forced DNS upstreams and rely on domain routing where possible. This does not remove or repair the global overseas DNS fallback. `opencode.ai` remains the one confirmed-working domestic DoH exception. Keep in mind that local DNS for foreign services can still be polluted, and Cloudflare Worker TCP resets remain independent issues.

**2026-10-14 AI DNS policy removal A/B test:** Remove only 71 `nameserver-policy` overrides, not the 71 `ai-proxy.list` domain routing entries. The resulting template keeps the same DNS `fallback` and `GEOIP,CN,no-resolve`. Regenerate the EdgeTunnel subscription and verify in the generated Mihomo YAML that dedicated keys such as `'+.chatgpt.com'` are absent from `nameserver-policy`, while ChatGPT is still routed to `💬 Ai平台`. Observe both the foreign DoH timeout logs and any incorrect IP/DNS answers; if they persist, address general fallback/edge-node reachability in a separate change.

**Compatibility note:** This is a Mihomo-specific DNS enhancement. A Shadowrocket import may ignore or reinterpret parts of the DNS and process configuration; no live iOS compatibility claim is made. Likewise, Subconverter must inline the three new Surge-format `.list` files during conversion. Inspect the resulting YAML and runtime logs after regenerating the EdgeTunnel subscription. A static YAML refresh alone does not re-run Subconverter.

Run local static tests from the repository root:

```bash
python3 scripts/validate_template.py
```

Static tests do not confirm live EdgeTunnel VLESS connectivity, actual AI exit country, certificate trust, DNS response behavior or Android/Shadowrocket app capture. The P2 speed-test/proxy grouping strategy is intentionally unchanged.

## 2026-10-14 (later): drop tunnel DoH fallback, restore GEOIP resolve, close LAN proxy

Supersedes the `GEOIP,CN,no-resolve` A/B test above. Tested with mihomo v1.19.32 against the real generated subscription.

- `dns.fallback` / `fallback-filter` removed. With fake-ip, a proxied domain is resolved at the remote end; the local answer only feeds IP rules. A polluted answer is a non-CN IP and still lands in the proxy group, so the fallback never changed routing; it only made lookups wait on DoH through the selected EdgeTunnel node.
- `GEOIP,CN` resolves again. With `no-resolve`, unlisted domestic sites (tested: lianjia.com, lagou.com, nowcoder.com) fell to `🐟 漏网之鱼` and went out through the US node. With resolve + domestic-only DoH they match `GeoIP(cn)` and go direct, and no lookup touches the tunnel.
- The `UDP + GEOIP,CN` rule resolves too: with the old fallback, every rejected overseas QUIC packet (e.g. YouTube) first triggered tunnel DoH. Without fallback this costs one domestic DoH lookup.
- Kept from the earlier commits: ProxyLite instead of ProxyGFWlist, the 71 overseas AI `nameserver-policy` removals.
- `allow-lan: false`, `bind-address: "127.0.0.1"`: the template has no `authentication`, so LAN mode exposed an open proxy on 7890/7891 to the whole Wi-Fi.
- `scripts/validate_template.py`: a local `entries` variable shadowed the `entries()` function, so the script always crashed with UnboundLocalError before any check ran. Renamed; added checks for the above.
