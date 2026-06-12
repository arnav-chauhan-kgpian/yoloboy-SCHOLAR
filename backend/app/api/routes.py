from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from app.state.session_state import SessionState
from app.graph.workflow import build_scholarai_graph
from app.knowledge.opportunity_store import OpportunityStore
from app.file_extract import extract_resume_text
import asyncio
import json
import uuid

router = APIRouter(prefix="/api")
graph = build_scholarai_graph()
store = OpportunityStore()
session_states: dict[str, SessionState] = {}


def _apply_state_updates(target: dict, source: dict) -> None:
    for key, value in source.items():
        if key in ("narration", "application_results", "errors"):
            target.setdefault(key, [])
            target[key].extend(value)
        else:
            target[key] = value


DEMO_RESUME_TEXT = """Maya Chen
maya.chen@stanford.edu

EDUCATION
Stanford University
Bachelor of Science in Pre-Med
GPA: 3.7
International Student (F-1 Visa)

SKILLS
Research: Clinical research methodology, data collection, literature reviews
Patient Care: Community health, patient intake, vital signs, health education
Public Health: Epidemiology, health policy, underserved populations
Communication: Written and verbal, Spanish conversational

EXPERIENCE
Free Clinic Volunteer | Stanford Community Health Center
- Assisted healthcare professionals in patient intake and vital sign measurement
- Provided health education materials to underserved populations

Research Assistant | Stanford Department of Public Health
- Conducted literature reviews on rural healthcare access
- Analyzed patient outcome data

GOALS AND INTERESTS
Become a physician serving rural communities.
Passionate about reducing healthcare disparities.
Seeking opportunities in community medicine and public health.

CERTIFICATIONS
CPR/AED Certified
HIPAA Compliance Training
"""


def _build_initial_state(session_id: str, resume_text: str) -> SessionState:
    return {
        "session_id": session_id,
        "phase": "profile",
        "raw_resume_text": resume_text,
        "narration": [],
        "errors": [],
        "opportunities": [],
        "eligibility_results": [],
        "application_results": [],
        "profile_result": None,
        "profile": None,
        "discovery_result": None,
        "eligibility_result": None,
        "match_result": None,
        "tracker_result": None,
    }


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    content = await file.read()
    try:
        resume_text = extract_resume_text(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text found — if this is a scanned/image PDF, try a text-based PDF, DOCX, or TXT.",
        )
    session_states[session_id] = _build_initial_state(session_id, resume_text)
    return {"session_id": session_id, "message": "Resume uploaded, ready to start"}


@router.post("/demo")
async def start_demo():
    session_id = str(uuid.uuid4())
    session_states[session_id] = _build_initial_state(
        session_id=session_id,
        resume_text=DEMO_RESUME_TEXT,
    )
    return {"session_id": session_id, "message": "Demo started", "is_demo": True}


@router.get("/start-session/{session_id}")
async def start_session(session_id: str):
    state = session_states.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator():
        accumulated = dict(state)
        try:
            async for update in graph.astream(state):
                for node_name, node_output in update.items():
                    _apply_state_updates(accumulated, node_output)
                    session_states[session_id] = dict(accumulated)
                    payload = jsonable_encoder({"node": node_name, "output": node_output})
                    yield f"data: {json.dumps(payload)}\n\n"
                    await asyncio.sleep(0.05)
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    state = session_states.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return state


@router.get("/opportunities")
async def list_opportunities():
    return [o.model_dump() for o in store.get_all()]


@router.get("/opportunities/search")
async def search_opportunities(q: str = ""):
    if q:
        return [o.model_dump() for o in store.search_by_query(q)]
    return [o.model_dump() for o in store.get_all()]


@router.get("/opportunities/{opp_id}")
async def get_opportunity(opp_id: str):
    opp = store.get_by_id(opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp.model_dump()


@router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}