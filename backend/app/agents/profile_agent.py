from app.agents.base import BaseAgent
from app.state.session_state import SessionState
from app.models.profile import StudentProfile, ProfileExtractionResult, CitizenshipStatus, EnrollmentStatus
from app.llm import get_llm_or_none, parse_json_response
from typing import Any
import json
import re


class ProfileAgent(BaseAgent):
    name = "ProfileAgent"
    description = "Extracts structured student profile from uploaded resume"

    async def run(self, state: SessionState) -> dict[str, Any]:
        resume_text = state.get("raw_resume_text", "")
        if not resume_text:
            return {"errors": ["[ProfileAgent] No resume text provided"]}

        narration_messages = self.narrate("📄 Reading the résumé to understand who this student is...")
        narration_messages["narration"].append("🧬 Pulling out education, skills, experience, and goals...")

        llm = get_llm_or_none()
        if llm:
            profile = await self._extract_with_llm(llm, resume_text, narration_messages)
        else:
            narration_messages["narration"].append("🧬 Structuring the résumé into a clear student profile...")
            profile = self._extract_deterministic(resume_text)

        missing = self._find_missing_fields(profile)
        confidence = 1.0 - (len(missing) * 0.1)

        result = ProfileExtractionResult(
            profile=profile,
            confidence=max(confidence, 0.3),
            missing_fields=missing,
            narration=narration_messages["narration"],
        )

        narration_messages["narration"].append(f"✅ Got it — {profile.name}, a {profile.degree_level} {profile.major} student at {profile.university}.")
        if missing:
            narration_messages["narration"].append(f"📝 A few details I'll confirm along the way: {', '.join(missing)}.")

        return {
            "profile_result": result,
            "profile": profile,
            "phase": "discovery",
            "narration": narration_messages["narration"],
        }

    async def _extract_with_llm(self, llm, resume_text: str, narration: dict) -> StudentProfile:
        prompt = f"""Extract a structured student profile from this resume text. Return JSON matching this schema:
{{
  "name": "string",
  "email": "string",
  "citizenship": "us_citizen | permanent_resident | international | daca",
  "enrollment": "full_time | part_time",
  "gpa": float or null,
  "major": "string",
  "university": "string",
  "degree_level": "string (e.g. Bachelor, Master, PhD)",
  "graduation_date": "YYYY-MM-DD or null",
  "skills": ["string"],
  "goals": ["string"],
  "extracurriculars": ["string"],
  "financial_need": "string or null",
  "location_preferences": ["string"]
}}

Resume:
{resume_text}

IMPORTANT: If citizenship is not explicitly stated, infer "international" for non-US universities.
Return ONLY valid JSON, no markdown."""

        response = await llm.ainvoke(prompt)
        try:
            data = parse_json_response(response.content)
            return StudentProfile(
                **data,
                raw_resume_text=resume_text,
            )
        except Exception:
            narration["narration"].append("🧬 Re-checking the extracted details for accuracy...")
            return self._extract_deterministic(resume_text)

    def _extract_deterministic(self, text: str) -> StudentProfile:
        name = "Unknown"
        email = ""
        gpa = None
        major = "Undeclared"
        university = "Unknown"
        degree_level = "Bachelor"
        skills = []
        goals = []
        extracurriculars = []
        location_preferences = []

        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', text)
        if email_match:
            email = email_match.group(0)

        lines = [l.strip() for l in text.replace('\r', '').split('\n') if l.strip()]
        for line in lines:
            if '@' in line or 'http' in line.lower() or 'phone' in line.lower() or len(line) > 60:
                continue
            if len(line.split()) >= 2 and re.match(r'^[A-Z][a-z]+(\s[A-Z][a-z]+)+$', line):
                name = line
                break

        gpa_match = re.search(r'(?:GPA|gpa)[:\s]*(\d+\.?\d*)', text)
        if gpa_match:
            try:
                gpa = float(gpa_match.group(1))
            except ValueError:
                pass

        gpa_slash = re.search(r'(\d+\.?\d*)\s*/\s*4\.0', text)
        if gpa_slash and gpa is None:
            try:
                gpa = float(gpa_slash.group(1))
            except ValueError:
                pass

        for kw in ["PhD", "Ph.D.", "Doctorate", "PhD Candidate",
                     "Master", "Master's", "M.S.", "M.A.",
                     "Bachelor", "Bachelor's", "B.S.", "B.A.", "B.E.",
                     "High School", "Associate"]:
            if kw.lower() in text.lower():
                degree_level = kw
                break

        major_patterns = [
            r'(?:Major|major)[:\s]+([A-Za-z\s&,-]{2,50})',
            r'(?:Studying|studying)[:\s]+([A-Za-z\s&,-]{2,50})',
            r'(?:Pursuing|pursuing)[:\s]+([A-Za-z\s&,-]{2,50})',
            r'(?:B\.S\.|B\.A\.|M\.S\.|Ph\.D\.)[:\s]+([A-Za-z\s&,-]{2,50})',
            r'(?:Bachelor|Bachelor\'s|Master|Master\'s|PhD|Ph\.D\.)(?:\s+of\s+\w+)?\s+in\s+([A-Za-z\s&,-]{2,50})',
        ]
        for pattern in major_patterns:
            m = re.search(pattern, text)
            if m:
                candidate = m.group(1).split('\n')[0].strip().rstrip(',.')
                if len(candidate) > 2:
                    major = candidate
                    break

        uni_keywords = ["University", "College", "Institute of Technology", "Institute", "School of"]
        for kw in uni_keywords:
            idx = text.find(kw)
            if idx >= 0:
                start = max(0, text.rfind('\n', 0, idx) + 1)
                end = text.find('\n', idx)
                if end == -1:
                    end = len(text)
                candidate = text[start:end].strip()
                candidate = re.sub(r'^\d+\s*', '', candidate).strip()
                if kw in candidate:
                    university = candidate
                    break

        skill_keywords = [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "SQL",
            "React", "Node.js", "Angular", "Vue", "Django", "Flask", "Spring",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "Linux",
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP",
            "Data Analysis", "Data Science", "Statistics", "R", "MATLAB",
            "HTML", "CSS", "REST APIs", "GraphQL", "MongoDB", "PostgreSQL",
            "Agile", "Scrum", "Leadership", "Communication", "Problem Solving",
            "Public Speaking", "Research", "Teamwork",
            "Patient Care", "Public Health", "Health Education", "Clinical Research",
            "Epidemiology", "Health Policy", "Biostatistics", "Data Collection",
        ]
        for skill in skill_keywords:
            if skill.lower() in text.lower():
                if skill not in skills:
                    skills.append(skill)

        goal_kw = ["interest", "passionate", "goal", "aspire", "seeking", "aim to", "want to"]
        for line in lines:
            lower = line.lower()
            if any(g in lower for g in goal_kw) and len(line) > 15:
                goals.append(line.strip())
                if len(goals) >= 3:
                    break

        return StudentProfile(
            name=name,
            email=email or f"{name.lower().replace(' ', '.')}@email.com",
            citizenship=CitizenshipStatus.INTERNATIONAL,
            enrollment=EnrollmentStatus.FULL_TIME,
            gpa=gpa,
            major=major,
            university=university,
            degree_level=degree_level,
            skills=skills,
            goals=goals,
            extracurriculars=extracurriculars,
            location_preferences=location_preferences,
            raw_resume_text=text,
        )

    def _find_missing_fields(self, profile: StudentProfile) -> list[str]:
        missing = []
        if profile.name == "Unknown":
            missing.append("name")
        if profile.gpa is None:
            missing.append("gpa")
        if not profile.goals:
            missing.append("goals")
        if profile.graduation_date is None:
            missing.append("graduation_date")
        if not profile.skills:
            missing.append("skills")
        return missing