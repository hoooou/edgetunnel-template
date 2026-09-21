# EdgeTunnel shared Clash/Mihomo template

Generated: 2026-09-21

## Files

- `clash-base.yaml`: base Clash configuration plus high-priority rules.
- `ACL4SSR_Online_Mini_Ai_Merged.ini`: ACL4SSR Mini AI template plus the independent `💻 OpenCode` group.

## Included policy

1. Local/private networks remain direct.
2. UDP whose destination IP is classified as mainland China goes direct.
3. All remaining UDP is rejected. This prevents an unsupported EdgeTunnel VLESS UDP flow from falling through to `DIRECT`.
4. `opencode.ai` goes to the independent `💻 OpenCode` group.
5. `tech.bitauto.com`, `yiche.com`, `bitauto.com`, and `bitautotech.com` go direct.
6. No extra `openai.com` rule is added. OpenAI is handled by the upstream `AI.list` and `OpenAi.list` rulesets and the `💬 Ai平台` group.

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
