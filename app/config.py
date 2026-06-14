"""Environment configuration using pydantic-settings.

Loads all application settings from environment variables with sensible defaults
for local development. In production, values are injected via Docker/Railway.
"""

from typing import List, Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://lexuser:lexpass@postgres:5432/lexindia"
    # Sync URL variant for Alembic migrations (asyncpg → psycopg2)
    DATABASE_URL_SYNC: str = "postgresql://lexuser:lexpass@postgres:5432/lexindia"

    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"

    # ── LLM Providers ─────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    # Make Gemini optional for local dev
    GEMINI_API_KEY: Optional[str] = None
    GROK_API_KEY: str = ""
    # Comma-separated list: "openai,gemini,grok"
    LLM_PROVIDER_ORDER: str = "openai,gemini,grok"
    INDIAN_KANOON_API_KEY: str = ""
    # Legacy alias — kept for backward compatibility with existing .env files
    KANOON_API_KEY: str = ""

    # ── Application ──────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,https://lexindia.vercel.app,https://lexindiafrontend.vercel.app"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # ── Embedding Model ──────────────────────────────────────────────────
    # all-MiniLM-L6-v2 runs locally via FastEmbed (ONNX Runtime) — no API key needed.
    # Model name used by fastembed for download/cache.
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # ── RAG Pipeline ─────────────────────────────────────────────────────
    SIMILARITY_THRESHOLD: float = 0.70  # Increased from 0.50 for higher confidence
    MAX_RESULTS: int = 8
    CACHE_TTL_SECONDS: int = 86400  # 24 hours
    CACHE_VERSION: str = "v3"
    MIN_RESULT_CONFIDENCE: float = 0.60  # Warn if confidence below this
    
    # ── Data Quality ───────────────────────────────────────────────
    MIN_SECTION_TEXT_LENGTH: int = 100  # Minimum characters for valid section
    MIN_SIMPLIFIED_TEXT_LENGTH: int = 50  # Minimum characters for simplified text

    @model_validator(mode="after")
    def _backfill_kanoon_key(self) -> "Settings":
        """If INDIAN_KANOON_API_KEY is empty, fall back to legacy KANOON_API_KEY."""
        if not self.INDIAN_KANOON_API_KEY and self.KANOON_API_KEY:
            self.INDIAN_KANOON_API_KEY = self.KANOON_API_KEY

        # Patch Database Hostname if it fails to resolve locally (e.g. Supabase IPv6 only)
        import socket
        import urllib.parse

        def resolve_dns_over_udp(domain: str, dns_server: str = "8.8.8.8", port: int = 53) -> str | None:
            import struct
            parts = domain.split(".")
            packet = struct.pack(">HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0)
            for part in parts:
                packet += struct.pack("B", len(part)) + part.encode("utf-8")
            packet += b"\x00"
            packet_aaaa = packet + struct.pack(">HH", 28, 1)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(2.0)
                s.sendto(packet_aaaa, (dns_server, port))
                data, _ = s.recvfrom(1024)
                q_len = sum(len(p) + 1 for p in parts) + 1 + 4
                idx = 12 + q_len
                answers = struct.unpack(">HHHHHH", data[:12])[3]
                for _ in range(answers):
                    if data[idx] & 0xc0 == 0xc0:
                        idx += 2
                    else:
                        while data[idx] != 0:
                            idx += data[idx] + 1
                        idx += 1
                    type_, class_, ttl, data_len = struct.unpack(">HHIH", data[idx:idx+10])
                    idx += 10
                    rdata = data[idx:idx+data_len]
                    idx += data_len
                    if type_ == 28:  # AAAA
                        ipv6_parts = [rdata[i:i+2].hex() for i in range(0, 16, 2)]
                        return ":".join(ipv6_parts)
            except Exception:
                pass
            return None

        def patch_url(url: str) -> str:
            if not url:
                return url
            try:
                parsed = urllib.parse.urlparse(url)
                hostname = parsed.hostname
                if hostname:
                    try:
                        socket.gethostbyname(hostname)
                    except socket.gaierror:
                        # DNS resolution failed, try UDP resolver
                        resolved_ip = resolve_dns_over_udp(hostname)
                        if resolved_ip:
                            netloc = parsed.netloc
                            port_suffix = f":{parsed.port}" if parsed.port else ""
                            if "@" in netloc:
                                credentials, host_port = netloc.rsplit("@", 1)
                                new_netloc = f"{credentials}@[{resolved_ip}]{port_suffix}"
                            else:
                                new_netloc = f"[{resolved_ip}]{port_suffix}"
                            parsed = parsed._replace(netloc=new_netloc)
                            return urllib.parse.urlunparse(parsed)
            except Exception as e:
                import sys
                print(f"Error patching database URL: {e}", file=sys.stderr)
            return url

        self.DATABASE_URL = patch_url(self.DATABASE_URL)
        self.DATABASE_URL_SYNC = patch_url(self.DATABASE_URL_SYNC)
        return self

    @property
    def llm_providers(self) -> List[str]:
        """Parse comma-separated LLM_PROVIDER_ORDER into a list."""
        return [p.strip().lower() for p in self.LLM_PROVIDER_ORDER.split(",")]

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"


# Singleton instance — import this throughout the app
settings = Settings()
