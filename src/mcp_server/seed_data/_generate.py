"""Run this script once to regenerate jobs.json: python _generate.py"""
import json
import random
import uuid
from datetime import date, timedelta

random.seed(42)

COMPANIES = [
    ("Google", "public"), ("Meta", "public"), ("Amazon", "public"),
    ("Apple", "public"), ("Microsoft", "public"), ("Netflix", "public"),
    ("Stripe", "series-g"), ("Airbnb", "public"), ("Lyft", "public"),
    ("Uber", "public"), ("Databricks", "series-i"), ("Snowflake", "public"),
    ("Confluent", "public"), ("Cloudflare", "public"), ("Figma", "public"),
    ("Notion", "series-c"), ("Linear", "series-b"), ("Vercel", "series-c"),
    ("Anthropic", "series-e"), ("OpenAI", "private"), ("Spotify", "public"),
    ("Shopify", "public"), ("GitHub", "public"), ("GitLab", "public"),
    ("Datadog", "public"), ("Twilio", "public"), ("Okta", "public"),
    ("Palantir", "public"), ("Robinhood", "public"), ("Coinbase", "public"),
    ("Block", "public"), ("DoorDash", "public"), ("Instacart", "public"),
    ("Pinterest", "public"), ("Reddit", "public"), ("Discord", "series-h"),
    ("Hashicorp", "public"), ("PlanetScale", "series-c"), ("Replit", "series-b"),
    ("Supabase", "series-b"),
]

LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
    "Remote", "Los Angeles, CA", "Boston, MA", "Chicago, IL",
    "Denver, CO", "Atlanta, GA", "San Jose, CA", "Menlo Park, CA",
    "Redmond, WA", "Bellevue, WA", "Remote",  # duplicate for higher weight
]

TEAM_SIZES = ["4-6", "6-10", "8-12", "10-15", "12-20", "20-40"]

INTERVIEW_PROCESSES = [
    "Phone screen → 2 technical interviews → system design → hiring manager",
    "Recruiter call → take-home → 4-round onsite (coding, design, behavioral, culture)",
    "Screening call → 3 technical rounds → bar raiser",
    "Initial call → coding challenge → 5-round virtual onsite",
    "Recruiter screen → 2 coding rounds → system design → cross-functional",
    None,
]

ROLES = {
    "junior": [
        ("Junior Backend Engineer", ["Python", "Go", "PostgreSQL", "REST APIs", "Git"],
         ["Docker", "Redis", "gRPC"], 85_000, 125_000),
        ("Junior Frontend Engineer", ["React", "TypeScript", "CSS", "HTML", "Git"],
         ["Next.js", "GraphQL", "Storybook"], 80_000, 120_000),
        ("Junior Data Engineer", ["Python", "SQL", "Spark", "Airflow", "Git"],
         ["dbt", "Snowflake", "Kafka"], 85_000, 125_000),
        ("Junior Full Stack Engineer", ["React", "Node.js", "TypeScript", "PostgreSQL", "Git"],
         ["Redis", "Docker", "AWS"], 82_000, 122_000),
        ("Junior SRE", ["Python", "Linux", "Bash", "Kubernetes", "Git"],
         ["Terraform", "Prometheus", "AWS"], 88_000, 128_000),
    ],
    "mid": [
        ("Backend Engineer", ["Python", "Go", "PostgreSQL", "Kafka", "Kubernetes"],
         ["Rust", "gRPC", "Redis", "AWS"], 130_000, 185_000),
        ("Frontend Engineer", ["React", "TypeScript", "Next.js", "GraphQL", "CSS"],
         ["Vue.js", "Vite", "Webpack", "Testing Library"], 125_000, 180_000),
        ("Full Stack Engineer", ["React", "Node.js", "TypeScript", "PostgreSQL", "Docker"],
         ["Redis", "Kafka", "AWS", "GCP"], 128_000, 182_000),
        ("Data Engineer", ["Python", "Spark", "Airflow", "dbt", "Snowflake"],
         ["Kafka", "Flink", "BigQuery", "Terraform"], 130_000, 185_000),
        ("ML Engineer", ["Python", "PyTorch", "scikit-learn", "SQL", "Docker"],
         ["TensorFlow", "MLflow", "Spark", "Kubernetes"], 140_000, 195_000),
        ("SRE", ["Kubernetes", "Terraform", "Go", "Prometheus", "Python"],
         ["Grafana", "AWS", "GCP", "Ansible"], 135_000, 190_000),
        ("Platform Engineer", ["Kubernetes", "Terraform", "AWS", "Go", "Python"],
         ["Helm", "ArgoCD", "Datadog", "Vault"], 135_000, 192_000),
        ("Security Engineer", ["Python", "AWS", "IAM", "SAST", "DAST"],
         ["Go", "Terraform", "Kubernetes", "SIEM"], 138_000, 190_000),
        ("iOS Engineer", ["Swift", "SwiftUI", "Xcode", "REST APIs", "Core Data"],
         ["Combine", "RxSwift", "CI/CD", "Instruments"], 130_000, 185_000),
        ("Android Engineer", ["Kotlin", "Jetpack Compose", "Android SDK", "REST APIs", "Gradle"],
         ["Coroutines", "Dagger", "Firebase", "CI/CD"], 130_000, 185_000),
    ],
    "senior": [
        ("Senior Backend Engineer", ["Python", "Go", "PostgreSQL", "Kafka", "Kubernetes", "gRPC"],
         ["Rust", "Redis", "AWS", "Distributed Systems"], 170_000, 260_000),
        ("Senior Frontend Engineer", ["React", "TypeScript", "Next.js", "GraphQL", "Performance Optimization"],
         ["Vue.js", "Web Workers", "WebAssembly", "Design Systems"], 165_000, 255_000),
        ("Senior Full Stack Engineer", ["React", "Node.js", "TypeScript", "PostgreSQL", "Kubernetes", "AWS"],
         ["Redis", "Kafka", "GCP", "System Design"], 168_000, 258_000),
        ("Senior Data Engineer", ["Python", "Spark", "Airflow", "dbt", "Snowflake", "Kafka"],
         ["Flink", "BigQuery", "Terraform", "Data Modeling"], 172_000, 262_000),
        ("Senior ML Engineer", ["Python", "PyTorch", "TensorFlow", "Kubernetes", "MLflow", "SQL"],
         ["Triton", "ONNX", "Spark", "Feature Stores"], 185_000, 280_000),
        ("Senior SRE", ["Kubernetes", "Terraform", "Go", "Prometheus", "Grafana", "AWS"],
         ["Chaos Engineering", "eBPF", "GCP", "OpenTelemetry"], 178_000, 268_000),
        ("Senior Platform Engineer", ["Kubernetes", "Terraform", "AWS", "Go", "Python", "Helm"],
         ["ArgoCD", "Backstage", "Datadog", "Service Mesh"], 175_000, 265_000),
        ("Senior Security Engineer", ["Python", "AWS", "IAM", "Kubernetes", "Threat Modeling", "Go"],
         ["Zero Trust", "SIEM", "Terraform", "Cryptography"], 178_000, 268_000),
        ("Senior Data Scientist", ["Python", "PyTorch", "scikit-learn", "SQL", "A/B Testing", "Spark"],
         ["R", "Causal Inference", "MLflow", "Databricks"], 175_000, 265_000),
        ("Senior iOS Engineer", ["Swift", "SwiftUI", "Xcode", "Core Data", "Combine", "REST APIs"],
         ["Metal", "ARKit", "CI/CD", "App Store Connect"], 168_000, 255_000),
        ("Senior Android Engineer", ["Kotlin", "Jetpack Compose", "Android SDK", "Coroutines", "Dagger"],
         ["NDK", "Benchmark", "Firebase", "CI/CD"], 168_000, 255_000),
        ("Senior DevOps Engineer", ["Kubernetes", "Terraform", "AWS", "CI/CD", "Python", "Bash"],
         ["GCP", "Azure", "Ansible", "ArgoCD"], 170_000, 258_000),
    ],
    "staff": [
        ("Staff Backend Engineer", ["Python", "Go", "Distributed Systems", "Kafka", "Kubernetes", "System Design"],
         ["Rust", "gRPC", "Consensus Algorithms", "Data Modeling"], 230_000, 330_000),
        ("Staff Frontend Engineer", ["React", "TypeScript", "Performance", "Web Platform", "System Design", "Mentorship"],
         ["Compiler Tooling", "WebAssembly", "Design Systems"], 225_000, 320_000),
        ("Staff ML Engineer", ["Python", "PyTorch", "Large Scale Training", "Distributed Systems", "MLOps"],
         ["CUDA", "Triton", "Feature Stores", "Model Serving"], 250_000, 360_000),
        ("Staff Platform Engineer", ["Kubernetes", "AWS", "Terraform", "Go", "Developer Experience", "System Design"],
         ["eBPF", "Service Mesh", "Backstage", "Multi-cloud"], 235_000, 335_000),
        ("Staff Data Engineer", ["Python", "Spark", "Distributed Systems", "Data Modeling", "System Design", "dbt"],
         ["Flink", "Data Mesh", "Delta Lake", "Iceberg"], 232_000, 332_000),
        ("Staff Security Engineer", ["Threat Modeling", "Cryptography", "AWS", "Go", "Zero Trust", "System Design"],
         ["Post-Quantum Crypto", "Formal Verification", "Red Team"], 238_000, 338_000),
    ],
    "principal": [
        ("Principal Engineer", ["System Design", "Go", "Python", "Distributed Systems", "Mentorship", "Technical Strategy"],
         ["Rust", "Consensus Protocols", "Multi-region", "OSS Leadership"], 300_000, 440_000),
        ("Principal ML Engineer", ["LLM Training", "PyTorch", "CUDA", "Distributed Training", "Research", "Technical Strategy"],
         ["Triton", "RLHF", "Evaluation Frameworks", "Post-training"], 330_000, 460_000),
        ("Principal Platform Engineer", ["Kubernetes", "Multi-cloud", "Developer Platforms", "Technical Strategy", "Go"],
         ["eBPF", "Confidential Computing", "Supply Chain Security"], 305_000, 435_000),
        ("Principal Data Engineer", ["Data Architecture", "Distributed Systems", "Technical Strategy", "Python", "Spark"],
         ["Data Mesh", "Lakehouse", "Real-time Analytics"], 298_000, 428_000),
    ],
}

DESCRIPTIONS = {
    "junior": (
        "We are looking for a motivated {title} to join our {team_size} engineering team. "
        "You will work closely with senior engineers to build and maintain production systems, "
        "contribute to code reviews, and grow your technical skills. This is a great opportunity "
        "to learn from experienced engineers while making a real impact from day one."
    ),
    "mid": (
        "We are hiring a {title} to join our {team_size} team at {company}. "
        "You will own features end-to-end, contribute to technical decisions, "
        "collaborate across teams, and help level up junior engineers. "
        "Expect high ownership, a strong feedback culture, and meaningful technical challenges."
    ),
    "senior": (
        "We are looking for a {title} who thrives on complex problems and high-impact work. "
        "At {company} you will drive technical decisions, mentor engineers, "
        "design systems that scale to millions of users, and collaborate with product and leadership "
        "to shape roadmap. We expect strong communication and a track record of shipping."
    ),
    "staff": (
        "As a {title} at {company}, you will set technical direction across multiple teams, "
        "identify and resolve systemic issues, and partner with engineering leadership to drive "
        "multi-quarter initiatives. You bring deep expertise, strong cross-functional influence, "
        "and a history of raising the bar for your organization."
    ),
    "principal": (
        "This is a senior individual-contributor role for an engineer who operates at the intersection "
        "of technology and business strategy. As a {title} at {company}, you will shape our "
        "engineering strategy, drive company-wide architectural decisions, represent technical vision "
        "externally, and serve as a technical authority across the organization."
    ),
}

def random_date() -> str:
    start = date(2024, 6, 1)
    end = date(2025, 3, 1)
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()

def make_job(level: str) -> dict:
    role = random.choice(ROLES[level])
    title, req_skills, nice_skills, sal_min_base, sal_max_base = role
    company, stage = random.choice(COMPANIES)
    location = random.choice(LOCATIONS)
    remote_ok = location == "Remote" or random.random() < 0.35
    sal_variance = random.randint(-10_000, 10_000)
    team_size = random.choice(TEAM_SIZES)
    desc = DESCRIPTIONS[level].format(title=title, company=company, team_size=team_size)
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "company": company,
        "location": location,
        "remote_ok": remote_ok,
        "salary_min": sal_min_base + sal_variance,
        "salary_max": sal_max_base + sal_variance,
        "role_level": level,
        "required_skills": req_skills,
        "nice_to_have_skills": nice_skills,
        "full_description": desc,
        "posted_date": random_date(),
        "company_stage": stage,
        "team_size_estimate": team_size,
        "interview_process": random.choice(INTERVIEW_PROCESSES),
    }

# Distribution: junior 10%, mid 30%, senior 40%, staff 15%, principal 5%
DISTRIBUTION = [
    ("junior", 20),
    ("mid", 60),
    ("senior", 80),
    ("staff", 30),
    ("principal", 10),
]

jobs = []
for level, count in DISTRIBUTION:
    for _ in range(count):
        jobs.append(make_job(level))

random.shuffle(jobs)

out = "/Users/dakota/repos/portfolio/tech-job-market-agent/src/mcp_server/seed_data/jobs.json"
with open(out, "w") as f:
    json.dump(jobs, f, indent=2)

print(f"Generated {len(jobs)} jobs → {out}")
