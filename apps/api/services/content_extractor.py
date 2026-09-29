import io
import ipaddress
import logging
import re
import socket
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from pypdf import PdfReader

from apps.api.core.config import settings

logger = logging.getLogger(__name__)

# Max allowed content length: 5 MB for web pages, 10 MB for uploaded documents
MAX_URL_CONTENT_LENGTH = 5 * 1024 * 1024
MAX_FILE_SIZE = 10 * 1024 * 1024

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 (Noesis Reference Ingestion)"
)

# Elements that almost never contain primary reference knowledge
BOILERPLATE_TAGS = [
    "script",
    "style",
    "noscript",
    "nav",
    "header",
    "footer",
    "aside",
    "svg",
    "canvas",
    "iframe",
    "form",
    "button",
    "menu",
    "dialog",
    "select",
    "option",
    "textarea",
    "input",
]

BOILERPLATE_ATTR_PATTERN = re.compile(
    r"(cookie|banner|consent|sidebar|navbar|menu|social-share|advertisement|ads-|ad-container|modal|popup)",
    re.IGNORECASE,
)


def validate_url(raw_url: str) -> str:
    """Validates the input URL for correctness and SSRF protection."""
    url = raw_url.strip()
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL cannot be empty.",
        )

    parsed = urlparse(url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL scheme. Only HTTP and HTTPS protocols are supported.",
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL: Missing hostname.",
        )

    # Disallow localhost / local domains
    lower_host = hostname.lower()
    if (
        lower_host in ("localhost", "127.0.0.1", "0.0.0.0", "::1")
        or lower_host.endswith((".local", ".internal", ".localhost"))
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access to private or local hostnames is forbidden.",
        )

    # Check for direct IP address or resolve DNS to check for private networks
    try:
        # Check if hostname is an IP literal
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access to private, loopback, or reserved IP addresses is forbidden.",
            )
    except ValueError:
        # Hostname is a domain name; resolve DNS to check target IP
        try:
            resolved_ips = socket.getaddrinfo(hostname, None)
            for item in resolved_ips:
                sockaddr = item[4]
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Access to private or internal network endpoints is forbidden.",
                    )
        except socket.gaierror:
            if hostname.endswith((".test", ".example", ".invalid")) or settings.ENVIRONMENT == "test":
                pass
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not resolve domain name: '{hostname}'.",
                )

    return url


async def fetch_web_page(url: str, timeout: float = 15.0) -> tuple[str, str, dict[str, Any]]:
    """Fetches a web page over HTTP/HTTPS with size and content-type safety checks."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8,fr;q=0.7,*;q=0.5",
    }

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=timeout,
            headers=headers,
            max_redirects=5,
        ) as client:
            response = await client.get(url)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Web server returned HTTP {response.status_code} {response.reason_phrase}.",
                )

            content_type = response.headers.get("content-type", "").lower()
            # Verify text or html content
            if not any(t in content_type for t in ("text/html", "text/plain", "application/xhtml+xml", "text/markdown")):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported Content-Type '{content_type}'. Only HTML or plain text web pages are supported.",
                )

            content_bytes = response.content
            if len(content_bytes) > MAX_URL_CONTENT_LENGTH:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Web page content exceeds maximum allowed size (5 MB).",
                )

            text_content = response.text
            final_url = str(response.url)
            meta = {
                "final_url": final_url,
                "status_code": response.status_code,
                "content_type": content_type,
            }
            return text_content, final_url, meta

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timed out while attempting to connect to the provided URL.",
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Network error while connecting to URL: {exc}",
        )


def extract_clean_text_from_html(
    html: str, fallback_url: str | None = None
) -> tuple[str, str, dict[str, Any]]:
    """
    Parses HTML, removes navigation, scripts, styling, ads, and boilerplate,
    and returns meaningful clean textual content, title, and metadata.
    """
    soup = BeautifulSoup(html, "html.parser")

    # 1. Extract Title
    title = ""
    # Try OpenGraph or Twitter title
    og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "twitter:title"})
    if og_title and og_title.get("content"):
        title = str(og_title["content"]).strip()
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.h1:
        title = soup.h1.get_text().strip()

    if not title:
        parsed = urlparse(fallback_url or "")
        title = parsed.path.strip("/").split("/")[-1] or parsed.netloc or "Web Reference"

    # 2. Extract Document Metadata
    metadata: dict[str, Any] = {}
    desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
    if desc and desc.get("content"):
        metadata["description"] = str(desc["content"]).strip()

    author = soup.find("meta", attrs={"name": "author"})
    if author and author.get("content"):
        metadata["author"] = str(author["content"]).strip()

    html_tag = soup.find("html")
    if html_tag and html_tag.get("lang"):
        metadata["language"] = str(html_tag["lang"]).strip()

    if fallback_url:
        metadata["source_url"] = fallback_url
        metadata["domain"] = urlparse(fallback_url).netloc

    # 3. Strip boilerplate tags
    for tag_name in BOILERPLATE_TAGS:
        for element in soup.find_all(tag_name):
            element.decompose()

    # 4. Strip boilerplate by common class and id patterns
    for element in list(soup.find_all(True)):
        if not hasattr(element, "attrs") or element.attrs is None:
            continue
        classes = element.attrs.get("class", [])
        class_str = " ".join(classes) if isinstance(classes, list) else str(classes)
        id_str = str(element.attrs.get("id", ""))
        combined = f"{class_str} {id_str}"
        if BOILERPLATE_ATTR_PATTERN.search(combined) and element.name not in ("body", "html", "main", "article"):
            element.decompose()

    # 5. Extract text from primary container if available
    main_container = soup.find("main") or soup.find("article") or soup.find(attrs={"role": "main"})
    target_node = main_container if main_container else (soup.body if soup.body else soup)

    # 6. Extract formatted text preserving paragraphs and headings
    text_blocks: list[str] = []
    for elem in target_node.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "pre", "dt", "dd"]):
        txt = elem.get_text(separator=" ", strip=True)
        if txt and len(txt) > 3:
            text_blocks.append(txt)

    if text_blocks:
        cleaned_text = "\n\n".join(text_blocks)
    else:
        # Fallback to general get_text
        cleaned_text = target_node.get_text(separator="\n", strip=True)

    # Clean whitespace: normalize multiple spaces/tabs and consecutive newlines
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()

    if len(cleaned_text) < 25:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The target web page contains insufficient or unextractable textual content.",
        )

    return cleaned_text, title, metadata


def extract_text_from_document(
    file_bytes: bytes,
    file_name: str,
    content_type: str | None = None,
) -> tuple[str, str, dict[str, Any]]:
    """
    Extracts plain text and metadata from uploaded documents (PDF, TXT, MD).
    """
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file exceeds maximum allowed size (10 MB).",
        )

    file_name_lower = file_name.lower().strip()
    title = file_name

    # Check extension
    if file_name_lower.endswith(".pdf") or (content_type and "pdf" in content_type.lower()):
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            if reader.is_encrypted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Encrypted or password-protected PDF files are not supported.",
                )

            page_texts: list[str] = []
            for i, page in enumerate(reader.pages):
                ptxt = page.extract_text()
                if ptxt and ptxt.strip():
                    page_texts.append(ptxt.strip())

            if not page_texts:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="No extractable text found in the uploaded PDF. Scanned images without OCR are not supported.",
                )

            cleaned_text = "\n\n".join(page_texts)
            # Try to get title from PDF metadata
            meta: dict[str, Any] = {"page_count": len(reader.pages)}
            if reader.metadata:
                if reader.metadata.title:
                    title = str(reader.metadata.title).strip()
                if reader.metadata.author:
                    meta["author"] = str(reader.metadata.author).strip()

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reading PDF file {file_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse PDF document: {e}",
            )

    elif file_name_lower.endswith((".md", ".markdown", ".txt")) or (content_type and "text" in content_type.lower()):
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = file_bytes.decode("latin-1")
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to decode text file. Ensure it is encoded in UTF-8 or Latin-1.",
                )

        # For markdown, check if first line is a title
        meta = {}
        if file_name_lower.endswith((".md", ".markdown")):
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            for line in lines[:5]:
                if line.startswith("# "):
                    title = line.lstrip("# ").strip()
                    break

        cleaned_text = text

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_name}'. Allowed document formats: .pdf, .txt, .md",
        )

    # Clean whitespace
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()

    if len(cleaned_text) < 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The document does not contain sufficient textual content.",
        )

    return cleaned_text, title, meta
