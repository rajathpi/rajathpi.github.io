---
title: Docker Layers, Registries and S3, Explained
description: A beginner-friendly explanation of Docker layers, checksums, manifests, registries, and how they compare to storing tarballs in S3.
meta: May 12, 2026 · 3 min read
date: 2026-05
topic: Notes
list: Docker layers, registries and S3, explained
---

Change one file in a Docker image and push it, and about 2 KB goes up, not the 900 MB of Python underneath. The same trick means a layer you already have never downloads twice.

It works because of three small things: layers, digests and manifests. This post explains each, and why a registry is not just a bucket of tarballs.

## A Dockerfile becomes layers

```
FROM python:3.11           # Step 1
RUN pip install flask      # Step 2
COPY app.py /app/          # Step 3
CMD ["python", "/app/app.py"]
```

Each step makes a layer, a snapshot of filesystem changes. Here that is Python (~900 MB), Flask (~5 MB) and your `app.py` (~2 KB). Docker stacks them into the container filesystem.


<figure class="fig">
<div class="bars">
<div class="bar"><span class="l">Python</span><span class="b" style="--v:100"></span><span class="n">~900 MB</span></div>
<div class="bar"><span class="l">Flask</span><span class="b" style="--v:0.56"></span><span class="n">~5 MB</span></div>
<div class="bar hot"><span class="l">app.py</span><span class="b" style="--v:0.0002"></span><span class="n">~2 KB</span></div>
</div>
<figcaption>Layer sizes, to scale. Only the last one changes.</figcaption>
</figure>


## A digest names each layer

Each layer gets a SHA256 digest of its contents, like `sha256:9f2c1b3e8a...`. Same contents give the same digest.

So if Docker already holds a digest, it never downloads or uploads that layer again.

## A manifest lists the layers

The manifest is a small JSON file, a few KB, that lists layer digests in order. It is the recipe: stack these layers like this.

```
{ "layers": [
  { "digest": "sha256:9f2c1b3e8a..." },
  { "digest": "sha256:4d8e2a1f7c..." },
  { "digest": "sha256:b1c4d5e6f7..." } ] }
```

## Registries store the parts, not the whole

A registry (ECR, Docker Hub, JFrog Artifactory) stores layers and manifests separately. Docker rebuilds the final image on your machine when you pull. Only `docker save` makes one fused tarball.

ECR often keeps layer blobs in S3 underneath, but you talk to the registry, not S3.

## Push and pull move only what is missing

On `docker push`, Docker asks the registry whether it has each digest. It uploads only the missing layers, then the manifest last. If only `app.py` changed, about 2 KB goes up.


<figure class="fig">
<ol class="flow">
<li><b>Ask registry</b><span>does it have this digest?</span></li>
<li class="hot"><b>Upload missing layers</b><span>skip the ones it has</span></li>
<li><b>Upload manifest</b><span>last</span></li>
</ol>
</figure>


On `docker pull`, Docker fetches the manifest, checks its local cache, and downloads only the layers it lacks.

## A raw S3 tarball loses all of this

If you run `docker save` and copy the tarball to S3, S3 sees one big file. It has no layers, no manifest and no dedup.

```
docker save myrepo/myapp:v1 > myapp.tar
aws s3 cp myapp.tar s3://my-bucket/
```

Every consumer downloads the whole image, even if only `app.py` changed.

## In short

- Layer: the filesystem change from one Dockerfile step.
- Digest: the SHA256 fingerprint of a layer, used for caching and dedup.
- Manifest: a small JSON file listing layer digests in order.
- Registry: stores layers and manifests separately, and transfers only what is missing.
- Raw S3 tarball: no layers, no dedup, a full download every time.
