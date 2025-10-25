from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.schemas import (
    SearchRequest,
    MatchResult,
    AIQueryRequest,
    AIQueryResponse,
    AIChatResponse
)
from app.services.ai_service import chat_with_database
from app.db import models
from app.core.auth import get_current_user
from app.db.models_users import User
from datetime import datetime
import time

router = APIRouter()


@router.post("/chat", response_model=AIChatResponse)
async def chat_endpoint(
    request: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with the database using natural language.
    Example: "Find me Python developers with 5+ years experience"
    """
    start_time = time.time()
    
    try:
        print(f"📥 Chat request from user: {current_user.email}")
        print(f"📝 Query: {request.query_text}")
        if request.conversation_history:
            print(f"💬 Conversation history: {len(request.conversation_history)} messages")
        
        # Process the query with AI using user's personal API key if configured
        response_data = await chat_with_database(
            request.query_text, 
            db, 
            current_user,
            conversation_history=request.conversation_history
        )
        
        print(f"✅ Chat response generated")
        
        execution_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        # Extract candidate IDs - handle both list of strings and list of dicts
        candidates_data = response_data.get("candidates", [])
        if candidates_data and isinstance(candidates_data[0], dict):
            candidate_ids = [c["id"] for c in candidates_data]
        else:
            # Already a list of UUIDs (strings)
            candidate_ids = candidates_data
        
        # Fetch candidate details from database to create CandidateInfo objects
        candidate_info_list = []
        if candidate_ids:
            from uuid import UUID
            # Convert string UUIDs to UUID objects
            uuid_list = [UUID(str(cid)) for cid in candidate_ids]
            
            # Query database for candidate details
            candidates = db.query(models.Candidate).filter(
                models.Candidate.id.in_(uuid_list)
            ).all()
            
            # Create CandidateInfo objects
            for candidate in candidates:
                candidate_info_list.append({
                    "id": candidate.id,
                    "name": f"{candidate.first_name} {candidate.last_name}"
                })
        
        # Save query to database
        ai_query = models.AIChatQuery(
            user_id=request.user_id or "anonymous",
            query_text=request.query_text,
            response=response_data.get("response", ""),
            related_candidates=candidate_ids,  # Store UUIDs only
            related_jobs=response_data.get("jobs", []),
            execution_time_ms=execution_time,
            timestamp=datetime.utcnow()
        )
        
        db.add(ai_query)
        db.commit()
        
        # Return response with candidate info (names included)
        return AIChatResponse(
            response=response_data.get("response", ""),
            candidates=candidate_info_list,
            jobs=response_data.get("jobs", [])
        )
        
    except HTTPException:
        # Re-raise HTTPException as-is (403, 429, etc.)
        raise
    except Exception as e:
        print(f"❌ Chat endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[MatchResult])
async def semantic_search_endpoint(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform semantic search for candidates matching job requirements.
    Example: "Senior Full Stack Developer with React and Python"
    Note: This now uses the chat interface for intelligent matching
    """
    try:
        # Use chat interface for semantic search with user's personal API key if configured
        chat_result = await chat_with_database(request.query, db, current_user)
        
        # Extract candidate IDs from chat response
        candidate_ids = chat_result.get("candidates", [])
        
        # Build match results
        results = []
        for candidate_id in candidate_ids[:request.limit]:
            candidate = db.query(models.Candidate).filter(
                models.Candidate.id == candidate_id
            ).first()
            
            if candidate:
                results.append(MatchResult(
                    candidate_id=candidate.id,
                    candidate_name=f"{candidate.first_name} {candidate.last_name}",
                    match_score=90.0,  # AI-determined score
                    matched_skills=[],
                    reasoning=chat_result.get("response", "")[:200]
                ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queries", response_model=List[AIQueryResponse])
def get_query_history(
    skip: int = 0,
    limit: int = 50,
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """Get AI query history"""
    query = db.query(models.AIChatQuery)
    
    if user_id:
        query = query.filter(models.AIChatQuery.user_id == user_id)
    
    queries = query.order_by(
        models.AIChatQuery.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    return queries


@router.delete("/queries")
def delete_all_queries(
    user_id: str = "anonymous",
    db: Session = Depends(get_db)
):
    """Delete all chat history for a user"""
    try:
        deleted_count = db.query(models.AIChatQuery).filter(
            models.AIChatQuery.user_id == user_id
        ).delete()
        
        db.commit()
        
        return {
            "message": f"Deleted {deleted_count} chat messages",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
