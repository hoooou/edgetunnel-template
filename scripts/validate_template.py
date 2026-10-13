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
    assert "#💬 Ai平台" in BASE and "#💻 OpenCode" in BASE
    assert not re.search(r"^  - 'PROCESS-NAME,com\\.", BASE, re.M), "App process rules remain in base"

    required_order(INI, [
        "rules/app-direct.list",
        "rules/app-ai-proxy.list",
        "rules/app-proxy.list",
        "rules/ai-direct.list",
        "rules/ai-proxy.list",
        "Clash/Ruleset/AI.list",
        "Clash/ProxyGFWlist.list",
        "[]FINAL",
    ])
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
    for rule in direct_domains + proxy_domains:
        kind, domain = rule.split(",", 1)
        key = f"+.{domain}" if kind == "DOMAIN-SUFFIX" else domain
        assert f"'{key}':" in BASE, f"Missing DNS policy: {key}"
    assert "'+.opencode.ai':" in BASE
    assert len(process_names) == 74, f"Unexpected process count: {len(process_names)}"
    print(f"Static checks passed: {len(process_names)} processes, {len(direct_domains)} domestic AI domains, {len(proxy_domains)} overseas AI domains.")
    print("Not verified: live Subconverter expansion, Mihomo runtime, Shadowrocket import, Android process identity and real DNS behavior.")


if __name__ == "__main__":
    main()
