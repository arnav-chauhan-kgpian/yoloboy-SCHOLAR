from app.agents.base import BaseAgent
from app.state.session_state import SessionState
from app.models.eligibility import (
    EligibilityResult, EligibilityBatchResult, EligibilityVerdict, EligibilityReason
)
from typing import Any
import json
import re


class EligibilityAgent(BaseAgent):
    name = "EligibilityAgent"
    description = "Screens opportunities for eligibility with exact reasoning"

    # GPA within this margin of the requirement is Borderline (soft), not a hard reject.
    GPA_TOLERANCE = 0.2

    CITIZENSHIP_LABELS = {
        "us_citizen": "US Citizen",
        "permanent_resident": "Permanent Resident",
        "international": "International Student",
        "daca": "DACA Recipient",
    }

    async def run(self, state: SessionState) -> dict[str, Any]:
        profile = state.get("profile")
        opportunities = state.get("opportunities", [])
        
        if not profile:
            return self.error("No profile available for eligibility check")
        if not opportunities:
            return self.error("No opportunities to check eligibility against")

        first_name = profile.name.split()[0] if profile.name and profile.name != "Unknown" else "this student"

        narration = []
        narration.append(f"⚖️ Screening {len(opportunities)} opportunities against eligibility requirements...")

        results = []
        for opp in opportunities:
            result = self._check_eligibility(profile, opp)
            results.append(result)

        eligible = [r for r in results if r.verdict == EligibilityVerdict.ELIGIBLE]
        borderline = [r for r in results if r.verdict == EligibilityVerdict.BORDERLINE]
        rejected = [r for r in results if r.verdict == EligibilityVerdict.NOT_ELIGIBLE]

        narration.append(f"✅ {len(eligible)} look like strong fits for {first_name}.")
        narration.append(f"⚠️ {len(borderline)} are close calls worth a careful look.")
        narration.append(f"❌ Ruled out {len(rejected)} that miss a hard requirement — here's why:")

        for r in rejected[:3]:
            narration.append(f"{r.summary[:110]}")

        batch = EligibilityBatchResult(
            results=results,
            eligible_count=len(eligible),
            borderline_count=len(borderline),
            rejected_count=len(rejected),
            narration=narration,
        )

        return {
            "eligibility_result": batch,
            "eligibility_results": results,
            "phase": "matching",
            "narration": narration,
        }

    def _check_eligibility(self, profile, opportunity) -> EligibilityResult:
        reasons = []
        reasons.extend(self._check_citizenship(profile, opportunity))
        reasons.extend(self._check_gpa(profile, opportunity))
        reasons.extend(self._check_degree_level(profile, opportunity))
        reasons.extend(self._check_field_of_study(profile, opportunity))

        failed = [r for r in reasons if not r.passed]
        hard_fails = [r for r in failed if r.severity == "hard"]
        soft_fails = [r for r in failed if r.severity == "soft"]

        # Deterministic rollup: a single hard fail disqualifies; otherwise any soft
        # issue is Borderline; a clean sweep is Eligible. Eligibility score follows
        # the frozen Match-engine convention (0 / 0.55-0.75 / 1.0).
        if hard_fails:
            verdict = EligibilityVerdict.NOT_ELIGIBLE
            score = 0.0
        elif soft_fails:
            verdict = EligibilityVerdict.BORDERLINE
            score = max(0.55, 0.75 - 0.1 * (len(soft_fails) - 1))
        else:
            verdict = EligibilityVerdict.ELIGIBLE
            score = 1.0

        emoji = {"eligible": "✅", "borderline": "⚠️", "not_eligible": "❌"}
        summary = f"{emoji[verdict.value]} {opportunity.title}: "
        if verdict == EligibilityVerdict.ELIGIBLE:
            summary += "Meets all requirements"
        else:
            # Lead with the decisive (hard) reasons, then soft, so the headline is exact.
            decisive = (hard_fails + soft_fails)[:2]
            summary += "; ".join(r.notes for r in decisive)

        return EligibilityResult(
            opportunity_id=opportunity.id,
            verdict=verdict,
            score=round(score, 2),
            reasons=reasons,
            summary=summary,
            narration=[],
        )

    def _check_citizenship(self, profile, opportunity) -> list[EligibilityReason]:
        reqs = opportunity.citizenship_requirements
        if not reqs:
            return []

        labels = self.CITIZENSHIP_LABELS
        student = profile.citizenship.value
        student_label = labels.get(student, student)

        # Symmetric parse: build the set of statuses the opportunity ALLOWS.
        text = " ".join(reqs).lower()
        allowed = set()
        if any(k in text for k in ["us citizen", "u.s. citizen", "american citizen", "us national", "u.s. national"]):
            allowed.add("us_citizen")
        if any(k in text for k in ["permanent resident", "green card"]):
            allowed.add("permanent_resident")
        if any(k in text for k in ["international", "non-us", "non us", "foreign national", "non-citizen", "not a us citizen"]):
            allowed.add("international")
        if "daca" in text:
            allowed.add("daca")

        # Unparseable citizenship text → don't fabricate a rejection.
        if not allowed:
            return [EligibilityReason(
                requirement="Citizenship requirement",
                student_value=student_label,
                passed=True,
                severity="soft",
                notes="Citizenship requirement could not be parsed; assuming open",
            )]

        if student in allowed:
            return [EligibilityReason(
                requirement="Citizenship requirement",
                student_value=student_label,
                passed=True,
                severity="hard",
                notes="Citizenship requirement met",
            )]

        allowed_label = " or ".join(
            labels[a] for a in ["us_citizen", "permanent_resident", "international", "daca"] if a in allowed
        )
        return [EligibilityReason(
            requirement="Citizenship requirement",
            student_value=student_label,
            passed=False,
            severity="hard",
            notes=f"Requires {allowed_label}. Student = {student_label}.",
        )]

    def _check_gpa(self, profile, opportunity) -> list[EligibilityReason]:
        req = opportunity.gpa_requirement
        if req is None:
            return []

        requirement = f"GPA ≥ {req}"

        if profile.gpa is None:
            # Unknown on a gating field → Borderline, never a confident pass/fail.
            return [EligibilityReason(
                requirement=requirement,
                student_value="Not reported",
                passed=False,
                severity="soft",
                notes="GPA not reported — cannot confirm requirement",
            )]
        if profile.gpa >= req:
            return [EligibilityReason(
                requirement=requirement,
                student_value=str(profile.gpa),
                passed=True,
                severity="hard",
                notes="GPA requirement met",
            )]
        if profile.gpa >= req - self.GPA_TOLERANCE:
            # Near-miss within tolerance → Borderline, not disqualified.
            return [EligibilityReason(
                requirement=requirement,
                student_value=str(profile.gpa),
                passed=False,
                severity="soft",
                notes=f"GPA {profile.gpa} is just under the {req} requirement (within {self.GPA_TOLERANCE})",
            )]
        return [EligibilityReason(
            requirement=requirement,
            student_value=str(profile.gpa),
            passed=False,
            severity="hard",
            notes=f"GPA {profile.gpa} is below the {req} requirement",
        )]

    def _check_degree_level(self, profile, opportunity) -> list[EligibilityReason]:
        if not opportunity.degree_levels:
            return []

        profile_degree = profile.degree_level.lower()
        match = any(
            profile_degree in dl.lower() or dl.lower() in profile_degree
            for dl in opportunity.degree_levels
        )

        return [EligibilityReason(
            requirement=f"Degree level: {', '.join(opportunity.degree_levels)}",
            student_value=profile.degree_level,
            passed=match,
            severity="hard",
            notes="Degree level matches" if match
            else f"{profile.degree_level} not in required levels ({', '.join(opportunity.degree_levels)})",
        )]

    def _check_field_of_study(self, profile, opportunity) -> list[EligibilityReason]:
        fields = opportunity.fields_of_study
        if not fields:
            return []

        profile_major = profile.major.lower()
        match = False
        for f in fields:
            f_lower = f.lower()
            if f_lower == "all fields":
                match = True
                break
            if profile_major in f_lower or f_lower in profile_major:
                match = True
                break
            major_words = re.sub(r'[^a-z0-9\s]', ' ', profile_major).split()
            field_words = re.sub(r'[^a-z0-9\s]', ' ', f_lower).split()
            if set(major_words) & set(field_words):
                match = True
                break
            if any(mw in fw or fw in mw for mw in major_words for fw in field_words if len(mw) > 2 and len(fw) > 2):
                match = True
                break

        return [EligibilityReason(
            requirement=f"Field: {', '.join(fields)}",
            student_value=profile.major,
            passed=match,
            severity="hard",
            notes="Field matches" if match
            else f"{profile.major} does not match required fields ({', '.join(fields)})",
        )]