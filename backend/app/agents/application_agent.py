from app.agents.base import BaseAgent
from app.state.session_state import SessionState
from app.models.application import ApplicationResult, GeneratedDocument, DocumentType
from app.llm import get_llm_or_none
from typing import Any


class ApplicationAgent(BaseAgent):
    name = "ApplicationAgent"
    description = "Generates tailored resumes, cover letters, and SOPs"

    async def run(self, state: SessionState) -> dict[str, Any]:
        profile = state.get("profile")
        match_result = state.get("match_result")

        if not profile or not match_result:
            return self.error("Missing profile or match results for application generation")

        first_name = profile.name.split()[0] if profile.name and profile.name != "Unknown" else "this student"

        narration = []
        narration.append("📝 Drafting tailored application materials...")

        top_opportunities = match_result.top_picks[:3]
        opportunities_map = {o.id: o for o in state.get("opportunities", [])}

        llm = get_llm_or_none()
        if not llm:
            narration.append(f"✍️ Personalizing every document to {first_name}'s background...")

        results = []
        for ranked in top_opportunities:
            opp = opportunities_map.get(ranked.opportunity_id)
            if not opp:
                continue

            narration.append(f"✍️ Tailoring an application for {opp.title}...")

            documents = []

            if llm:
                resume = await self._generate_resume(llm, profile, opp)
            else:
                resume = self._template_resume(profile, opp)
            documents.append(resume)
            narration.append(f"✅ Resume aligned to {opp.organization}'s priorities.")

            if llm:
                cover = await self._generate_cover_letter(llm, profile, opp)
            else:
                cover = self._template_cover_letter(profile, opp)
            documents.append(cover)
            narration.append(f"✅ Cover letter written for {opp.organization}.")

            if opp.type.value == "scholarship":
                if llm:
                    sop = await self._generate_sop(llm, profile, opp)
                else:
                    sop = self._template_sop(profile, opp)
                documents.append(sop)
                narration.append(f"✅ Statement of purpose crafted for {opp.title}.")

            results.append(ApplicationResult(
                opportunity_id=opp.id,
                opportunity_title=opp.title,
                documents=documents,
                narration=[],
            ))

        return {
            "application_results": results,
            "narration": narration,
        }

    async def _generate_resume(self, llm, profile, opportunity) -> GeneratedDocument:
        prompt = f"""Generate a tailored resume for this student applying to {opportunity.title} at {opportunity.organization}.

Student Profile:
- Name: {profile.name}
- Major: {profile.major} at {profile.university}
- GPA: {profile.gpa or 'N/A'}
- Skills: {', '.join(profile.skills) if profile.skills else 'N/A'}
- Goals: {', '.join(profile.goals) if profile.goals else 'N/A'}
- Extracurriculars: {', '.join(profile.extracurriculars) if profile.extracurriculars else 'N/A'}

Opportunity Requirements: {', '.join(opportunity.requirements[:5]) if opportunity.requirements else 'General'}

Write a professional resume in plain text format. Emphasize skills and experiences relevant to this opportunity."""

        response = await llm.ainvoke(prompt)
        return GeneratedDocument(
            type=DocumentType.RESUME,
            opportunity_id=opportunity.id,
            content=response.content,
        )

    async def _generate_cover_letter(self, llm, profile, opportunity) -> GeneratedDocument:
        prompt = f"""Write a tailored cover letter for {profile.name} applying to {opportunity.title} at {opportunity.organization}.

Student: {profile.major}, {profile.university}, GPA {profile.gpa or 'N/A'}
Skills: {', '.join(profile.skills[:5]) if profile.skills else 'N/A'}
Goals: {', '.join(profile.goals[:3]) if profile.goals else 'N/A'}

Opportunity: {opportunity.description[:300]}
Requirements: {', '.join(opportunity.requirements[:5]) if opportunity.requirements else 'General'}

Write a professional, persuasive cover letter. Be concise and specific."""

        response = await llm.ainvoke(prompt)
        return GeneratedDocument(
            type=DocumentType.COVER_LETTER,
            opportunity_id=opportunity.id,
            content=response.content,
        )

    async def _generate_sop(self, llm, profile, opportunity) -> GeneratedDocument:
        prompt = f"""Write a Statement of Purpose for {profile.name} applying for {opportunity.title} at {opportunity.organization}.

Student: {profile.major} at {profile.university}, GPA {profile.gpa or 'N/A'}
Goals: {', '.join(profile.goals) if profile.goals else 'N/A'}
Extracurriculars: {', '.join(profile.extracurriculars) if profile.extracurriculars else 'N/A'}

Scholarship Description: {opportunity.description[:300]}

Write a compelling SOP that connects the student's background and goals to this scholarship. Be authentic and specific. 400-600 words."""

        response = await llm.ainvoke(prompt)
        return GeneratedDocument(
            type=DocumentType.SOP,
            opportunity_id=opportunity.id,
            content=response.content,
        )

    def _template_resume(self, profile, opportunity) -> GeneratedDocument:
        skill_lines = "\n".join(f"  - {s}" for s in (profile.skills or ["N/A"]))
        goal_lines = "\n".join(f"  - {g}" for g in (profile.goals or ["Seeking opportunities in " + profile.major]))
        content = f"""{profile.name}
{profile.email} | {profile.major} | {profile.university}

===== EDUCATION =====
{profile.degree_level} in {profile.major}
{profile.university}
GPA: {profile.gpa or 'N/A'}

===== SKILLS =====
{skill_lines}

===== GOALS =====
{goal_lines}

===== TARGET =====
{opportunity.title} — {opportunity.organization}
{opportunity.description[:200]}

===== RELEVANT REQUIREMENTS =====
{chr(10).join(f'  - {r}' for r in (opportunity.requirements[:5] or ['General']))}"""
        return GeneratedDocument(
            type=DocumentType.RESUME,
            opportunity_id=opportunity.id,
            content=content.strip(),
        )

    def _template_cover_letter(self, profile, opportunity) -> GeneratedDocument:
        content = f"""Dear {opportunity.organization} Hiring Team,

I am writing to express my strong interest in the {opportunity.title} position. As a {profile.degree_level} student in {profile.major} at {profile.university}, I believe my academic background and skills make me a strong candidate.

My coursework and projects in {profile.major} have prepared me well for this opportunity. {f'With a GPA of {profile.gpa}, ' if profile.gpa else ''}I have demonstrated consistent academic excellence and a deep commitment to my field.

Key skills I bring to this role include:
{chr(10).join(f'- {s}' for s in (profile.skills[:6] or ['Strong analytical abilities', 'Team collaboration', 'Quick learning']))}

I am particularly drawn to {opportunity.organization} because of its reputation and the opportunity to contribute to meaningful work. This position aligns perfectly with my career goals.

Thank you for considering my application. I look forward to the opportunity to discuss how I can contribute to your team.

Best regards,
{profile.name}
{profile.email}"""
        return GeneratedDocument(
            type=DocumentType.COVER_LETTER,
            opportunity_id=opportunity.id,
            content=content.strip(),
        )

    def _template_sop(self, profile, opportunity) -> GeneratedDocument:
        content = f"""STATEMENT OF PURPOSE

{opportunity.title}
{opportunity.organization}

Applicant: {profile.name}
Program: {profile.major} — {profile.university}

INTRODUCTION

I am {profile.name}, a {profile.degree_level.lower()} student in {profile.major} at {profile.university}. I am applying for the {opportunity.title} because it represents a unique opportunity to advance my academic and professional journey.

ACADEMIC BACKGROUND

My academic journey in {profile.major} has equipped me with a strong foundation in both theoretical concepts and practical applications. {f'With a GPA of {profile.gpa}, ' if profile.gpa else ''}I have consistently strived for excellence.

SKILLS AND EXPERIENCE

My technical skills include: {', '.join(profile.skills[:8]) if profile.skills else 'strong analytical and problem-solving abilities'}. These skills have been developed through coursework, projects, and collaborative work.

GOALS

This scholarship would enable me to focus on my studies and research without financial constraint, allowing me to fully dedicate myself to making meaningful contributions to {profile.major}.

{', '.join(profile.goals) if profile.goals else f'I aim to leverage my education in {profile.major} to drive innovation and solve real-world problems.'}

CONCLUSION

I am confident that my background, skills, and passion align with the mission of {opportunity.organization}. This opportunity would be transformative for my career, and I am committed to making the most of it.<｜end▁of▁thinking｜>"""
        return GeneratedDocument(
            type=DocumentType.SOP,
            opportunity_id=opportunity.id,
            content=content.strip(),
        )