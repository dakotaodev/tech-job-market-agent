from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    id: str = Field(description="Unique job posting identifier")
    title: str = Field(description="Job title, e.g. 'Senior Backend Engineer'")
    company: str = Field(description="Hiring company name")
    location: str = Field(description="City, state, or 'remote'")
    remote_ok: bool = Field(description="Whether the role supports remote work")
    salary_min: int = Field(description="Minimum base salary (USD annual)")
    salary_max: int = Field(description="Maximum base salary (USD annual)")
    role_level: str = Field(description="Seniority level: 'junior' | 'mid' | 'senior' | 'staff' | 'principal'")
    required_skills: list[str] = Field(description="Required technical skills")
    nice_to_have_skills: list[str] = Field(description="Optional or preferred skills")
    full_description: str = Field(description="Complete job description text")
    posted_date: str = Field(description="Date posted in ISO 8601 format")
    company_stage: str = Field(description="Company stage, e.g. 'public', 'series-b', 'startup'")
    team_size_estimate: str = Field(description="Estimated team size, e.g. '8-12'")
    interview_process: str | None = Field(default=None, description="Description of the interview process if known")


class SalaryReport(BaseModel):
    job_title: str = Field(description="Job title searched for, possibly normalized if a fallback match was applied")
    company: str | None = Field(default=None, description="Company filter applied, if any")
    location: str | None = Field(default=None, description="Location filter applied, if any")
    p25: int = Field(description="25th percentile salary (USD annual)")
    p50: int = Field(description="Median (50th percentile) salary (USD annual)")
    p75: int = Field(description="75th percentile salary (USD annual)")
    p90: int = Field(description="90th percentile salary (USD annual)")
    total_records: int = Field(description="Number of salary records used; indicates statistical confidence")
    companies_represented: int = Field(description="Number of unique companies in the dataset")
    location_breakdown: dict[str, int] = Field(description="Median salary by location for the matching records")


class SkillEntry(BaseModel):
    skill: str = Field(description="Skill name, e.g. 'Kubernetes', 'Rust'")
    frequency_pct: float = Field(description="Percentage of jobs in the filtered set requiring this skill")
    trend_direction: str = Field(description="Trend relative to prior period: 'rising' | 'stable' | 'declining'")
    yoy_change: float = Field(description="Year-over-year change in frequency percentage points, if available")


class SkillTrendReport(BaseModel):
    skills: list[SkillEntry] = Field(description="Skills sorted by frequency descending")
    time_window: str = Field(description="Time window queried, e.g. '30d', '90d', '180d', '1y'")
    total_jobs_analyzed: int = Field(description="Total job postings analyzed in the trend calculation")


class CompanyEntry(BaseModel):
    company_name: str = Field(description="Company name")
    median_salary: int = Field(description="p50 salary for the role level at this company (USD annual)")
    salary_range: dict[str, int] = Field(description="Salary percentiles with keys 'p25', 'p50', 'p75', 'p90'")
    open_roles_count: int = Field(description="Total number of open job postings for this company")
    hiring_velocity: float = Field(description="Fraction of total jobs posted in the last 30 days")
    common_skills: list[str] = Field(description="Top 5 most frequently required skills for this company")
    avg_tenure_estimate: str = Field(description="Estimated average tenure inferred from role progression patterns")


class CompanyComparison(BaseModel):
    companies: list[CompanyEntry] = Field(description="One entry per queried company, up to 3")
    role_level_filter: str | None = Field(default=None, description="Seniority level filter applied, e.g. 'senior', 'staff'")


class NegotiationReport(BaseModel):
    market_position: str = Field(description="Offer position relative to p50 market salary: 'below' | 'at' | 'above'")
    current_offer: int = Field(description="Candidate's current offer amount (USD annual base)")
    p50_market_salary: int = Field(description="p50 market salary for the role and location")
    suggested_counter: int = Field(description="Recommended counter-offer based on p75; 0 if offer is already above market")
    talking_points: list[str] = Field(description="3–5 concrete negotiation talking points")
    comparable_offers: list[dict] = Field(description="Similar role offers with keys 'company', 'location', 'salary_range'")
    risk_assessment: str = Field(description="Brief assessment of negotiation risk, e.g. 'Low risk — offer is below market'")


class QueryPlan(BaseModel):
    question: str = Field(description="Original user question")
    role_title: str | None = Field(default=None, description="Extracted job title or role, e.g. 'Senior Backend Engineer'")
    company: str | None = Field(default=None, description="Extracted company name, e.g. 'Stripe'")
    location: str | None = Field(default=None, description="Extracted location: city, state, or 'remote'")
    min_salary: int | None = Field(default=None, description="Minimum salary expectation extracted from the question")
    yoe: int | None = Field(default=None, description="Years of experience extracted from the question")
    current_offer: int | None = Field(default=None, description="Current offer amount if this is a negotiation query")
    intent: str = Field(description="Parsed query intent: 'salary' | 'skills' | 'negotiation' | 'comparison' | 'general'")


class ToolResult(BaseModel):
    tool_name: str = Field(description="Name of the MCP tool called, e.g. 'get_salary_data'")
    status: str = Field(description="Outcome of the tool call: 'success' | 'error'")
    data: dict | None = Field(default=None, description="Tool result serialized to dict, or None if an error occurred")
    error: str | None = Field(default=None, description="Error message if status is 'error', else None")
    timestamp: str = Field(description="ISO 8601 timestamp of when the tool was called")
