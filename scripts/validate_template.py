#!/usr/bin/env python3
"""Static EdgeTunnel template checks (stdlib only); not a replacement for live Subconverter/Mihomo validation."""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = (ROOT / "clash-base.yaml").read_text(encoding="utf-8")
INI = (ROOT / "ACL4SSR_Online_Mini_Ai_Merged.ini").read_text(encoding="utf-8")
DIRECT = (ROOT / "rules/ai-direct.list").read_text(encoding="utf-8")
PROXY = (ROOT / "rules/ai-proxy.list").read_text(encoding="utf-8")


def entries(text: str, prefix: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith(prefix)]


def required_order(text: str, needles: list[str]) -> None:
    indexes = [text.find(needle) for needle in needles]
    assert all(i >= 0 for i in indexes), list(zip(needles, indexes))
    assert indexes == sorted(indexes), list(zip(needles, indexes))


def main() -> None:
    app_files = ["app-direct.list", "app-ai-proxy.list", "app-proxy.list"]
    policies = ["DIRECT", "💬 Ai平台", "🚀 节点选择"]
    process_names: dict[str, str] = {}
    for file_name, policy in zip(app_files, policies):
        text = (ROOT / "rules" / file_name).read_text(encoding="utf-8")
        rows = entries(text, "PROCESS-NAME,")
        assert rows, f"Empty process file: {file_name}"
        for row in rows:
            name = row.removeprefix("PROCESS-NAME,")
            assert "," not in name, row
            assert name not in process_names, f"Conflicting process: {name}"
            process_names[name] = policy

    assert process_names["com.openai.chatgpt"] == "💬 Ai平台"
    assert process_names["com.anthropic.claude"] == "💬 Ai平台"
    assert process_names["com.deepseek.chat"] == "DIRECT"
    assert process_names["com.tencent.mm"] == "DIRECT"
    for process in ["OpenCode", "opencode", "Cursor", "Cursor.exe", "python", "node", "Chrome"]:
        assert process not in process_names, f"Multi-model/browser process pinned: {process}"

    required_order(BASE, [
        "DOMAIN-SUFFIX,lan,DIRECT",
        "NETWORK,UDP,REJECT",
        "DOMAIN-SUFFIX,opencode.ai,💻 OpenCode",
        "DOMAIN-SUFFIX,yieti.top,DIRECT",
        "DOMAIN-SUFFIX,bitautotech.com,DIRECT",
    ])
    assert "find-process-mode: strict" in BASE
    assert "  enable: true" in BASE and "  enhanced-mode: fake-ip" in BASE
    assert "proxy-server-nameserver:" in BASE and "direct-nameserver:" in BASE
    # Corporate split-horizon DNS must never silently switch back to system/public DNS.
    for domain in ("tech.bitauto.com", "yiche.com", "bitauto.com", "bitautotech.com"):
        dns_entry = "    '+." + domain + "':\n      - 192.168.70.49\n      - 192.168.70.1\n"
        assert dns_entry in BASE, f"Wrong corporate DNS policy: {domain}"
        assert f"    - '+.{domain}'" in BASE, f"Missing fake-IP exclusion: {domain}"
        assert f"DOMAIN-SUFFIX,{domain},DIRECT" in BASE, f"Missing direct route: {domain}"
    # Website proxy route and DNS transport are independent. DNS intentionally
    # no longer embeds AI/OpenCode group suffixes after the successful DNS fix.
    assert "ruleset=💬 Ai平台,https://raw.githubusercontent.com/hoooou/edgetunnel-template/main/rules/ai-proxy.list" in INI
    assert "DOMAIN-SUFFIX,opencode.ai,💻 OpenCode" in BASE
    assert not re.search(r"^  - 'PROCESS-NAME,com\\.", BASE, re.M), "App process rules remain in base"

    # Backfilled my_yml domain classes must remain before generic ACL4SSR/GFW.
    restored = [
        ("rules/explicit-direct.list", "DIRECT", 17),
        ("rules/explicit-proxy.list", "🚀 节点选择", 5),
        ("rules/app-proxy-domains.list", "🚀 节点选择", 34),
        ("rules/app-direct-domains.list", "DIRECT", 43),
        ("rules/overseas-services.list", "🚀 节点选择", 83),
        ("rules/domestic-services.list", "DIRECT", 42),
    ]
    for path, policy, count in restored:
        rows = [x for x in (ROOT / path).read_text(encoding="utf-8").splitlines()
                if x.startswith(("DOMAIN,", "DOMAIN-SUFFIX,"))]
        assert len(rows) == count, f"{path} count changed; review reference my_yml"
        assert len(rows) == len(set(rows)), f"{path} duplicate domain rules"
        assert f"ruleset={policy},https://raw.githubusercontent.com/hoooou/edgetunnel-template/main/{path}" in INI
    required_order(INI, [
        "rules/ai-direct.list", "rules/ai-proxy.list",
        "Clash/Ruleset/AI.list", "Clash/Ruleset/OpenAi.list",
        "rules/explicit-direct.list", "rules/explicit-proxy.list",
        "rules/app-proxy-domains.list", "rules/app-direct-domains.list",
        "rules/overseas-services.list", "rules/domestic-services.list",
        "Clash/ProxyLite.list", "Clash/ChinaDomain.list", "[]FINAL",
    ])
    assert "DOMAIN-SUFFIX,microsoft.com" in (ROOT / "rules/explicit-direct.list").read_text(encoding="utf-8")
    assert "DOMAIN-SUFFIX,onedrive.com" in (ROOT / "rules/explicit-direct.list").read_text(encoding="utf-8")
    assert "DOMAIN-SUFFIX,bilibili.com" in (ROOT / "rules/app-direct-domains.list").read_text(encoding="utf-8")
    assert "DOMAIN-SUFFIX,discord.com" in (ROOT / "rules/app-proxy-domains.list").read_text(encoding="utf-8")
    assert "DOMAIN-SUFFIX,googleapis.com" not in (ROOT / "rules/overseas-services.list").read_text(encoding="utf-8")

    required_order(INI, [
        "rules/app-direct.list",
        "rules/app-ai-proxy.list",
        "rules/app-proxy.list",
        "rules/ai-direct.list",
        "rules/ai-proxy.list",
        "Clash/Ruleset/AI.list",
        "Clash/ProxyLite.list",
        "[]FINAL",
    ])
    # Lightweight mobile ruleset: never pull in full 7K-entry GFW domain list.
    assert "Clash/ProxyLite.list" in INI, "Missing lightweight ACL4SSR proxy rules"
    assert "Clash/ProxyGFWlist.list" not in INI, "Full ProxyGFWlist unexpectedly enabled"
    # GEOIP,CN must resolve: unlisted domestic sites (lianjia/lagou/nowcoder...)
    # otherwise fall to 漏网之鱼 and go through the tunnel. DNS here is domestic
    # DoH only (no tunnel fallback), so resolving is cheap.
    assert "ruleset=🎯 全球直连,[]GEOIP,CN\n" in INI
    assert "[]GEOIP,CN,no-resolve" not in INI
    assert "ruleset=🐟 漏网之鱼,[]FINAL" in INI
    assert "overwrite_original_rules=false" in INI
    assert "clash_rule_base=https://raw.githubusercontent.com/hoooou/edgetunnel-template/main/clash-base.yaml" in INI
    assert "custom_proxy_group=💻 OpenCode" in INI
    assert "custom_proxy_group=💬 Ai平台" in INI
    assert "custom_proxy_group=🚀 节点选择" in INI
    # Default proxy/fallback group is 节点选择; proxies must precede DIRECT.
    assert "custom_proxy_group=🚀 节点选择`select`.*`[]DIRECT" in INI
    assert "custom_proxy_group=🚀 节点选择`select`[]DIRECT`.*" not in INI
    for name in ("💬 Ai平台", "💻 OpenCode", "🐟 漏网之鱼"):
        line = next(l for l in INI.splitlines() if l.startswith(f"custom_proxy_group={name}`"))
        assert "`select`[]🚀 节点选择" in line, f"Wrong default for {name}"
    assert "♻️ 自动选择" not in INI, "Removed auto-select group must not be referenced"
    assert "自动测速：支持" not in INI, "Stale automatic-speed-test comment"
    assert "cfw-latency-url:" not in BASE, "Remove legacy Clash for Windows latency probe"
    assert "cfw-latency-timeout:" not in BASE, "Remove legacy Clash for Windows latency timeout"
    assert "`url-test`" not in INI, "Auto-test group must not be generated"
    assert "ruleset=DIRECT,https://raw.githubusercontent.com/hoooou/edgetunnel-template/main/rules/ai-direct.list" in INI

    direct_domains = entries(DIRECT, "DOMAIN,") + entries(DIRECT, "DOMAIN-SUFFIX,")
    proxy_domains = entries(PROXY, "DOMAIN,") + entries(PROXY, "DOMAIN-SUFFIX,")
    assert len(direct_domains) == len(set(direct_domains))
    assert len(proxy_domains) == len(set(proxy_domains))
    a = {x.split(",", 1)[1] for x in direct_domains}
    b = {x.split(",", 1)[1] for x in proxy_domains}
    assert a.isdisjoint(b), f"Domestic/overseas exact-domain overlap: {a & b}"
    # Domestic AI keeps explicit local DNS; overseas AI relies on fake-IP,
    # domain routing, and the existing global nameserver/fallback only when needed.
    dns_policy = BASE.split("  nameserver-policy:\n", 1)[1].split("  fake-ip-filter:", 1)[0]
    for rule in direct_domains:
        kind, domain = rule.split(",", 1)
        key = f"+.{domain}" if kind == "DOMAIN-SUFFIX" else domain
        assert f"    '{key}':" in dns_policy, f"Missing domestic AI DNS policy: {key}"
    for rule in proxy_domains:
        kind, domain = rule.split(",", 1)
        key = f"+.{domain}" if kind == "DOMAIN-SUFFIX" else domain
        assert f"    '{key}':" not in dns_policy, f"Unexpected overseas AI DNS policy: {key}"
    assert "'+.opencode.ai':" in BASE
    # Do not resolve OpenCode through EdgeTunnel: its proxied DoH URLs timed out.
    # Website traffic stays routed to the OpenCode group by high-priority rules.
    opencode_dns = BASE.split("    '+.opencode.ai':\n", 1)[1].split("    # Domestic AI domains", 1)[0]
    assert "https://dns.alidns.com/dns-query" in opencode_dns
    assert "https://doh.pub/dns-query" in opencode_dns
    assert "#💻 OpenCode" not in opencode_dns
    assert "#💬 Ai平台" not in opencode_dns
    dns_config = BASE.split("dns:\n", 1)[1].split("  fake-ip-filter:", 1)[0]
    assert "https://1.1.1.1/dns-query#" not in dns_config
    assert "https://8.8.8.8/dns-query#" not in dns_config
    # General fallback through the tunnel was removed; keep it from coming back.
    assert "\n  fallback:" not in dns_config, "Tunnel DoH fallback must stay removed"
    assert "\n  fallback-filter:" not in dns_config
    assert "\nallow-lan: false\n" in BASE, "allow-lan must stay off"
    # No per-AI-domain proxied DNS override should be reintroduced.
    assert "https://9.9.9.9/dns-query#💬 Ai平台" not in dns_config
    assert "https://doh.opendns.com/dns-query#💬 Ai平台" not in dns_config
    # OpenCode remains a deliberately tested exception using direct Chinese DNS.
    assert "'+.opencode.ai':\n      - 'https://dns.alidns.com/dns-query'\n      - 'https://doh.pub/dns-query'" in BASE
    assert len(process_names) == 74, f"Unexpected process count: {len(process_names)}"
    print(f"Static checks passed: {len(process_names)} processes, {len(direct_domains)} domestic AI domains, {len(proxy_domains)} overseas AI domains.")
    print("Not verified: live Subconverter expansion, Mihomo runtime, Shadowrocket import, Android process identity and real DNS behavior.")


if __name__ == "__main__":
    main()
