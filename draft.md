Machen wir daraus einen echten Standard. Arbeitstitel: AXP – Agentic Experience Protocol. Ziel: Ein einheitliches Datenformat und eine minimalistische MCP Schnittstelle, damit Agenten nicht nur Preis und Lagerbestand sehen, sondern die ganze Story eines Produkts und einer Marke – Uniqueness, Trust, Differenzierung, echte Experiences. AXP ergänzt AP2 sauber auf der Erlebnis Seite und folgt dessen Extension Logik für A2A und Cards, nur eben für Experiences statt Payments.  ￼

Below ist ein präziser Auftrag an den Coding Agent. Bitte ohne Absprache vollständig umsetzen.

⸻

Auftrag an den Coding Agent

0. Deliverables
	1.	Schemas

	•	JSON Schema Dateien für alle AXP Objekte
	•	TypeScript Typen aus den Schemas generiert
	•	Pydantic Modelle in Python als zweite Referenz

	2.	Referenzdaten

	•	Vollständige Beispiel Exporte als JSON Lines und als Zip Bundle
	•	Drei Beispiel Produkte, eine Beispiel Marke, ein Beispiel Micro Experience Capsule

	3.	Minimal MCP Server

	•	Implementiert die AXP Tools unten
	•	In Memory Store mit Beispiel Daten
	•	OpenAPI Beschreibung für Debug

	4.	Security und Embedding

	•	Sandbox für Experience Capsules mit strikter Policy
	•	Signiertes Manifest für Capsules
	•	Evidence und Provenance Felder mit einfachen Prüfungen

	5.	Docs

	•	Readme mit Quickstart
	•	Kurzer Architekturtour
	•	Mapping AXP zu AP2

⸻

1. Namensraum und Version
	•	Namespace: axp.v0_1
	•	Extension URI: https://agentic-commerce.org/axp/v0.1
	•	Versionierung nach SemVer
	•	Alle Top Level Objekte haben Felder spec, version, generated_at

⸻

2. Top Level Exportformat

AXP Export ist ein Zip mit Manifest plus JSONL Dateien.

axp_bundle.zip
 ├─ manifest.json
 ├─ brand_profile.json
 ├─ catalog_products.jsonl
 ├─ experiences.jsonl
 ├─ policies.json
 ├─ ratings_reviews.jsonl
 ├─ assets/
 │   ├─ images/…   (optional, nur für Demo)
 │   └─ capsules/… (AXP Capsules)

2.1 manifest.json

{
  "spec": "axp",
  "version": "0.1.0",
  "publisher": {
    "name": "Shopware Demo Store",
    "domain": "demo.shop",
    "public_keys": ["did:web:demo.shop#axp"]
  },
  "brand_profile": "brand_profile.json",
  "files": {
    "catalog_products": "catalog_products.jsonl",
    "experiences": "experiences.jsonl",
    "policies": "policies.json",
    "ratings_reviews": "ratings_reviews.jsonl"
  },
  "signature": {
    "alg": "RS256",
    "value": "base64url..."
  }
}


⸻

3. Datenmodell

3.1 Brand Profile

{
  "spec": "axp",
  "version": "0.1.0",
  "brand": {
    "id": "brand_001",
    "legal_name": "Demo Commerce GmbH",
    "founded_year": 2011,
    "employee_count": 480,
    "customer_count_estimate": 55000,
    "headquarters_country": "DE",
    "domains": ["demo.shop"],
    "certifications": ["ISO9001", "ClimatePartner"],
    "independent_ratings": [
      {"source": "Trustpilot", "score": 4.6, "reviews": 12873, "url": "https://..."},
      {"source": "Google", "score": 4.4, "reviews": 2034, "url": "https://..."}
    ],
    "csat": 0.87,
    "nps": 54,
    "return_rate": 0.11,
    "service_sla": {
      "first_response_hours": 4,
      "resolution_hours_p50": 24
    },
    "unique_value_props": [
      "Lifetime repair service",
      "Local production",
      "Open spare parts catalog"
    ],
    "trust_factors": {
      "badges": ["PCI DSS ready", "GDPR controls"],
      "warranties": [{"name": "Extended warranty", "duration_days": 730}],
      "data_provenance": "signed_by_brand_key"
    }
  }
}

3.2 Catalog Product

Ein Eintrag pro Zeile in catalog_products.jsonl.

{
  "product": {
    "id": "sku_123",
    "parent_id": null,
    "title": "Classic High Top Sneaker Red",
    "short_desc": "Retro look, durable sole",
    "tech_specs": {
      "material": "Leather",
      "weight_grams": 420,
      "sizes": ["41","42","43","44"],
      "care": "Hand wash, no dryer"
    },
    "price": {"currency": "EUR", "value": 129.90},
    "availability": {"state": "in_stock", "quantity": 220},
    "media": {
      "images": [
        {
          "url": "https://cdn.demo.shop/img/sneaker_red_1.jpg",
          "machine_captions": [
            {"lang": "en", "text": "Red high top sneaker on wood floor"},
            {"lang": "de", "text": "Roter High Top Sneaker auf Holzboden"}
          ],
          "embeddings": {"clip": {"dim": 768, "vector": "base64float..."}}
        }
      ],
      "documents": [
        {
          "url": "https://cdn.demo.shop/docs/sneaker_red_specs.pdf",
          "semantic_summary": {"lang": "en", "text": "Care guide and sizing"},
          "checksum_sha256": "abc123..."
        }
      ]
    },
    "experiences": {
      "capsules": [
        {
          "id": "cap_sneaker_3d",
          "title": "3D configurator",
          "capsule_uri": "axp://capsules/cap_sneaker_3d.zip",
          "modality": "canvas3d",
          "preferred_size": {"width": 720, "height": 480},
          "params_schema": {
            "type": "object",
            "properties": {
              "color": {"enum": ["red","black","white"]},
              "size": {"type": "string"}
            },
            "required": ["color"]
          }
        }
      ],
      "demo_videos": [
        {"url": "https://cdn.demo.shop/vids/sneaker_walk.mp4", "caption": "On foot"}
      ]
    },
    "soft_signals": {
      "uniqueness_score": 0.82,
      "craftsmanship_score": 0.76,
      "sustainability_score": 0.61,
      "innovation_score": 0.55,
      "evidence": [
        {"kind": "certification", "name": "Leather Working Group", "url": "https://..."},
        {"kind": "award", "name": "Design Award 2024", "url": "https://..."}
      ]
    },
    "trust_signals": {
      "review_summary": {
        "avg_rating": 4.5,
        "count_total": 1342,
        "top_positive": ["Comfort", "Looks"],
        "top_negative": ["Runs small"]
      },
      "return_reasons": [
        {"reason": "size_issue", "share": 0.56},
        {"reason": "color_mismatch", "share": 0.18}
      ],
      "return_rate": 0.14,
      "warranty_days": 365
    },
    "intent_signals": [
      {"intent": "daily_commute", "share": 0.34},
      {"intent": "basketball", "share": 0.28},
      {"intent": "fashion", "share": 0.38}
    ],
    "policies": {
      "shipping": {"regions": ["DE","AT","NL"], "days": 2},
      "returns": {"days": 30, "restocking_fee": 0.0}
    },
    "provenance": {
      "brand_id": "brand_001",
      "last_verified": "2025-09-18T08:30:00Z",
      "signature": "base64url..."
    }
  }
}

3.3 Ratings und Reviews

Zeilenbasiert, normalisiert für Agenten Ranking.

{
  "product_id": "sku_123",
  "source": "Trustpilot",
  "rating": 5,
  "title": "Great fit",
  "text": "Comfortable for city walks",
  "lang": "en",
  "verified_purchase": true,
  "timestamp": "2025-08-31T10:13:00Z",
  "aspects": {"comfort": 0.9, "build": 0.8, "style": 0.85}
}

3.4 Experience Capsules

Kapsel als Zip mit Manifest, UI und Policy.

capsule manifest

{
  "id": "cap_sneaker_3d",
  "name": "3D configurator",
  "version": "0.1.0",
  "entry": {"html": "index.html"},
  "surfaces": ["canvas3d", "html"],
  "sandbox_policy": {
    "dom": true,
    "storage": "none",
    "network": {"allow": ["https://cdn.demo.shop/assets/"], "block_all_others": true},
    "lifetime_seconds": 600,
    "permissions": []
  },
  "api": {
    "inbound_events": ["init", "configure", "set_variant", "request_quote"],
    "outbound_events": ["ready", "state_changed", "add_to_cart", "telemetry"]
  },
  "signature": "base64url..."
}

postMessage Contract

type Inbound =
  | {type: "init", correlationId: string}
  | {type: "configure", params: Record<string, unknown>}
  | {type: "set_variant", sku: string, params: Record<string, unknown>}
  | {type: "request_quote"};

type Outbound =
  | {type: "ready"}
  | {type: "state_changed", state: Record<string, unknown>}
  | {type: "add_to_cart", sku: string, quantity: number}
  | {type: "telemetry", event: string, data: Record<string, unknown>};


⸻

4. Kontrollierte Vokabulare
	•	return_reasons: size_issue, damaged, color_mismatch, quality_expectation, changed_mind, shipping_delay
	•	intent: gift, daily_commute, hobby, professional_use, travel, fashion
	•	trust_badges: pci_dss_ready, climate_partner, fair_wear, gdpr_controls

Vokabulare als JSON mit Version im Repo pflegen.

⸻

5. Scoring Leitplanken
	•	Alle Scores in [0,1]
	•	Immer mit evidence Liste aus Quellen und optional Belegen
	•	Agenten sollen Feld agent_ranking_hint berücksichtigen:

{"agent_ranking_hint": {"primary": ["uniqueness_score","review_summary.avg_rating"], "secondary": ["return_rate","sustainability_score"]}}


⸻

6. Minimal MCP Protocol

Server implementiert die folgenden Tools im Namespace axp.

6.1 Tool: axp.getBrandProfile
	•	input: { }
	•	output: BrandProfile wie oben

6.2 Tool: axp.searchCatalog
	•	input:

{
  "query": "string",
  "filters": {
    "price": {"min": 0, "max": 9999},
    "availability": ["in_stock","preorder"],
    "intent": ["fashion","daily_commute"],
    "soft_min": {"uniqueness_score": 0.5}
  },
  "limit": 20,
  "cursor": "optional"
}

	•	output:

{
  "items": [/* array von Product Cards, ohne große Media Arrays */],
  "next_cursor": "optional"
}

6.3 Tool: axp.getProduct
	•	input: {"product_id": "sku_123"}
	•	output: kompletter Product Eintrag

6.4 Tool: axp.getExport
	•	input: {"since": "2025-09-01T00:00:00Z"}
	•	output:

{
  "bundle_uri": "axp://export/axp_bundle_2025_09_18.zip",
  "checksum_sha256": "abc123...",
  "expires_at": "2025-09-18T23:59:59Z"
}

6.5 Tool: axp.getCapsule
	•	input: {"capsule_id": "cap_sneaker_3d"}
	•	output:

{
  "capsule_uri": "axp://capsules/cap_sneaker_3d.zip",
  "sandbox_embed": {
    "kind": "iframe",
    "policy": {
      "allow_scripts": true,
      "allow_forms": false,
      "allow_fullscreen": false
    },
    "preferred_size": {"width": 720, "height": 480}
  }
}

6.6 Tool: axp.subscribeInventory  (optional)
	•	input: {"product_ids": ["sku_123","sku_456"]}
	•	output: {"subscription_id": "inv_abc", "ttl_seconds": 600}
	•	Server sendet Events über MCP Events Channel:
{"type":"inventory_update","product_id":"sku_123","availability":{"state":"in_stock","quantity":205}}

6.7 Tool: axp.health
	•	input: {}
	•	output: {"status":"ok","version":"0.1.0"}

Auth
	•	Bearer Token oder mTLS
	•	Optional Verifiable Presentation mit Brand Key

⸻

7. Security und Privacy
	•	Provenance: alle Top Level Objekte können signiert werden
	•	Capsule Sandbox: keine Cookies, kein Local Storage, enger Network Allowlist, Ablaufzeit
	•	PII: keine personenbezogenen Daten im Export
	•	Rate Limits: default 600 requests pro Minute, 50 parallel
	•	Abuse Control: serverseitige Blocklisten für ungewöhnliche Abfragen

⸻

8. A2A Extension für AXP Unterstützung

Analog zu AP2 eine AgentCard Erweiterung bereitstellen, damit Agents Capability discovern können.

AgentCard Extension Objekt

{
  "uri": "https://agentic-commerce.org/axp/v0.1",
  "required": false,
  "params": {
    "roles": ["brand","catalog","experience_provider"]
  }
}


⸻

9. Beispiel Workflows

9.1 Discovery und Ranking
	1.	Agent ruft axp.searchCatalog mit Intent Filtern
	2.	Agent lädt für Top 3 Produkte axp.getProduct
	3.	Agent gewichtet nach agent_ranking_hint und return_rate
	4.	Agent bettet Capsule über axp.getCapsule ein

9.2 Content Verständnis
	1.	Agent extrahiert machine_captions und document semantic_summary
	2.	Optional Embeddings nutzen für semantische Suche

9.3 Experience to Cart Bridge

Capsule sendet add_to_cart Event an den Agent. Der Agent erzeugt Cart im Shop System. Zahlung läuft später über AP2.

⸻

10. Schemas erzeugen
	•	Lege schemas/axp/ an
	•	Erstelle brand_profile.schema.json, product.schema.json, experience_capsule.schema.json
	•	Generiere TypeScript Typen mit typescript-json-schema
	•	Generiere Pydantic Modelle mit datamodel-code-generator

⸻

11. Minimal MCP Server
	•	Node plus Fastify oder Python plus FastAPI
	•	Endpunkte als MCP Tools registrieren
	•	In Memory Datenquelle mit Beispieldaten
	•	Serve Capsules aus assets/capsules
	•	Logging von Tool Calls
	•	Tests:
	•	Schema Validation
	•	Rate Limit
	•	Capsule Sandbox Policy

⸻

12. Beispiel Einbettung im Chat UI

Der Server liefert für axp.getCapsule ein sandbox_embed. Das Chat UI legt ein iframe mit Content Security Policy an, registriert postMessage Brücke und leitet nur die erlaubten Events weiter. Keine weiteren Rechte.

⸻

13. Mapping zu AP2
	•	AXP liefert Kontext, Trust, Differenzierung und Experiences
	•	AP2 liefert Intent Mandate, Cart Mandate, Payment Mandate und Dispute Evidenz
	•	Empfehlung: product.provenance.signature und brand_profile.brand.data_provenance an AP2 Cart Mandate anhängen, damit bei Disputes die Experience und Trust Evidenz herangezogen werden kann.  ￼

⸻

14. Quickstart Tasks
	1.	Schemas erstellen und validieren
	2.	Drei Beispiel Produkte erzeugen, eine Capsule bauen
	3.	MCP Server starten, Tools manuell durchspielen
	4.	Mini Demo Chat UI rendern: Suche, Produktkarte, Capsule Einbettung
	5.	Readme schreiben, inklusive Curl Beispiele

⸻

Bottom line: AXP macht die weichen Faktoren maschinenlesbar und liefert eine sichere Schnittstelle für eingebettete Micro Experiences. Damit steigt die Conversion, sinken Retouren und Agenten treffen bessere Entscheidungen. Wenn das steht, verdrahten wir es hart mit AP2 für den letzten Meter zur Zahlung.