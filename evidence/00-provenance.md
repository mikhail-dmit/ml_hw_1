# Font Awesome Free 6.4.0: npm registry provenance check

## Artifact and source

- Package: `@fortawesome/fontawesome-free@6.4.0`.
- Registry version metadata: https://registry.npmjs.org/@fortawesome/fontawesome-free/6.4.0
- Registry `dist.tarball`: https://registry.npmjs.org/@fortawesome/fontawesome-free/-/fontawesome-free-6.4.0.tgz
- Archive checked: the original tarball used for the previous audits and vendoring, still present at:

```text
/var/folders/kq/7bqwgn4j20z70l738kc_0b_h0000gn/T/opencode/fontawesome-6.4.0-vkMrGM/fontawesome-free-6.4.0.tgz
```

The original archive was available, so no replacement download was needed.

## Published hash versus local hash

| Measurement | Value |
| --- | --- |
| npm registry `dist.shasum` (SHA-1) | `1ee0c174e472c84b23cb46c995154dc383e3b4fe` |
| Original local tarball SHA-1 | `1ee0c174e472c84b23cb46c995154dc383e3b4fe` |
| SHA-1 comparison | **MATCH** |
| Original local tarball SHA-256 | `385681597a3301b5f56fc70136274f9fd081e0ac5b9f8222351ac7e89465dfa2` |

The comparison was also performed programmatically against a fresh registry response, with an assertion requiring the two SHA-1 values to be equal before checking the vendored files.

## Commands run

The registry's published SHA-1 was obtained with the requested command:

```bash
curl -s https://registry.npmjs.org/@fortawesome/fontawesome-free/6.4.0 \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['dist']['shasum'])"
```

The local archive was hashed with macOS's `shasum`. `shasum -a 1` and `shasum -a 256` compute the same digests as `sha1sum` and `sha256sum`, respectively:

```bash
shasum -a 1 /var/folders/kq/7bqwgn4j20z70l738kc_0b_h0000gn/T/opencode/fontawesome-6.4.0-vkMrGM/fontawesome-free-6.4.0.tgz
shasum -a 256 /var/folders/kq/7bqwgn4j20z70l738kc_0b_h0000gn/T/opencode/fontawesome-6.4.0-vkMrGM/fontawesome-free-6.4.0.tgz
```

## Direct archive-to-vendor verification

After the registry hash matched, Python's `tarfile` module read the following archive members and compared their uncompressed bytes directly with the corresponding vendored files. Every comparison matched:

| Archive member | Vendored file | Byte comparison |
| --- | --- | --- |
| `package/metadata/icon-families.json` | `vendor/fontawesome-free-6.4.0/metadata/icon-families.json` | **MATCH** |
| `package/metadata/categories.yml` | `vendor/fontawesome-free-6.4.0/metadata/categories.yml` | **MATCH** |
| `package/package.json` | `vendor/fontawesome-free-6.4.0/package.json` | **MATCH** |
| `package/LICENSE.txt` | `vendor/fontawesome-free-6.4.0/LICENSE.txt` | **MATCH** |

## What this establishes—and its limits

The original archive's SHA-1 matches the value npm publishes for this exact package version, establishing a registry-backed integrity link to the published npm artifact. Direct byte comparisons then link the four vendored upstream files to that checked archive. The independently computed SHA-256 is a stronger local fingerprint and agrees with the hash recorded in the earlier audit evidence.

This is an integrity check against the npm registry response obtained over HTTPS, not an independent publisher signature or proof that the publisher or registry was uncompromised. SHA-1 is not collision-resistant against a deliberate adversary; the local SHA-256 is recorded here but was not compared with an independently published SHA-256. Neither hash establishes the code's safety, the metadata's semantic correctness, or whether an icon is an appropriate depiction of a dish; those are separate questions from artifact provenance.
