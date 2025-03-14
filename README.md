
[Aegiscan](https://aegiscan.com) is a modern, open source workflow automation platform built for security and IT engineers. Simple YAML-based templates for integrations with a no-code UI for workflows.
Executed using Temporal for scale and reliability.

We're on a mission to make security and IT automation more accessible through **response-as-code**. What Sigma rules did for detection, YARA for malware research, and Nuclei did for vulnerabilities, Aegiscan is doing for response automation.

## Getting Started

> [!IMPORTANT]
> Aegiscan is in active development. Expect breaking changes with releases. Review the release [changelog](https://github.com/DigitransLab/aegiscan/releases) before updating.

### Run Aegiscan locally

Deploy a local Aegiscan stack using Docker Compose. View full instructions [here](https://docs.aegiscan.com/self-hosting/deployment-options/docker-compose).

```bash
# Download Aegiscan
git clone https://github.com/DigitransLab/aegiscan.git

# Generate .env file
./env.sh

# Run Aegiscan
docker compose up -d
```

Go to [http://localhost](http://localhost) to access the UI. Sign-up with your email and password (min 12 characters). The first user to sign-up and login will be the superadmin for the instance. The API docs is accessible at [http://localhost/api/docs](http://localhost/api/docs).

### Run Aegiscan on AWS Fargate

**For advanced users:** deploy a production-ready Aegiscan stack on AWS Fargate using Terraform. View full instructions [here](https://docs.aegiscan.com/self-hosting/deployment-options/aws-ecs).

```bash
# Download Terraform files
git clone https://github.com/DigitransLab/aegiscan.git
cd aegiscan/deployments/aws

# Create and add encryption keys to AWS Secrets Manager
./scripts/create-aws-secrets.sh

# Run Terraform to deploy Aegiscan
terraform init
terraform apply
```

### Run Aegiscan on Kubernetes

Coming soon.

## Community

Have questions? Feedback? New integration ideas? Come hang out with us in the [Aegiscan Community Discord](https://discord.gg/H4XZwsYzY4).

## Aegiscan Registry

![Aegiscan Registry](img/aegiscan-template.svg)

Aegiscan Registry is a collection of integration and response-as-code templates.
Response actions are organized into [MITRE D3FEND](https://d3fend.mitre.org/) categories (`detect`, `isolate`, `evict`, `restore`, `harden`, `model`) and Aegiscan's own ontology of capabilities (e.g. `list_alerts`, `list_cases`, `list_users`). Template inputs (e.g. `start_time`, `end_time`) are normalized to fit the [Open Cyber Security Schema (OCSF)](https://schema.ocsf.io/) ontology where possible.

The future of response automation should be self-serve, where teams rapidly link common capabilities (e.g. `list_alerts` -> `enrich_ip_address` -> `block_ip_address`) into workflows.

**Examples**

Visit our documentation on Aegiscan Registry for use cases and ideas.
Or check out existing open source templates in [our repo](https://github.com/DigitransLab/aegiscan/tree/main/registry/aegiscan_registry/templates).

## Open Source vs Enterprise

This repo is available under the AGPL-3.0 license with the exception of the `ee` directory. The `ee` directory contains paid enterprise features requiring a Aegiscan Enterprise license.

Aegiscan Enteprise builds on top of Aegiscan OSS, optimized for mixed ETL and network workloads at enterprise scale.
Powered by serverless workflow execution (AWS Lambda and Knative) and S3-compatible object storage.

*If you are interested in Aegiscan's Enterprise self-hosted or managed Cloud offering, check out [our website](https://aegiscan.com) or [book a meeting with us](https://cal.com/team/aegiscan).*

## Security

SSO, audit logs, and IaaC deployments (Terraform, Kubernetes / Helm) will always be free and available. We're working on a comprehensive list of Aegiscan's threat model, security features, and hardening recommendations. For immediate answers to these questions, please reach to us on [Discord](https://discord.gg/H4XZwsYzY4).

Please report any security issues to [security@digi-trans.org](mailto:founders+security@digi-trans.org) and include `aegiscan` in the subject line.
