# Simple fix file to apply to ai_service.py
# Replace the chat_with_database method with this simplified version

SIMPLIFIED_CHAT = '''
    async def chat_with_database(self, query: str, db: Session) -> Dict[str, Any]:
        """AI chat - simplified to prevent infinite loops"""
        
        # Get limited candidates to prevent context overflow
        candidates = db.query(models.Candidate).limit(15).all()
        
        if not candidates:
            return {
                "response": "No candidates found in database.",
                "candidates": [],
                "jobs": []
            }
        
        # Build CONCISE context
        context_parts = []
        for candidate in candidates:
            skills = [f"{s.skill_name}" for s in candidate.skills[:5]]
            work = candidate.work_experiences[0] if candidate.work_experiences else None
            work_str = f"{work.job_title} at {work.company_name}" if work else "No experience"
            
            context_parts.append(
                f"{candidate.first_name} {candidate.last_name} | "
                f"{candidate.career_level or 'N/A'} | "
                f"Skills: {', '.join(skills) if skills else 'None'} | "
                f"Recent: {work_str}"
            )
        
        database_context = "\\n".join(context_parts)
        
        # Detect language
        import re
        is_arabic = bool(re.search(r'[\\u0600-\\u06FF]', query))
        
        # Simple, clear instructions
        system_message = """You are an HR assistant. Answer questions about candidates.
RULES:
- Keep response under 200 words
- Only mention candidates that match the question  
- If just a name is given, provide a brief profile
- NEVER repeat the same text
- Match user's language (Arabic or English)"""
        
        lang_note = "Respond in Arabic" if is_arabic else "Respond in English"
        
        user_prompt = f'''{lang_note}

Question: {query}

Candidates: {database_context}

Brief answer (max 200 words):'''
        
        try:
            ai_response = await self.call_ai(user_prompt, system_message)
            ai_response = ai_response.strip()[:1000]  # Hard limit to prevent loops
            
            # Return only mentioned candidates
            relevant_candidates = []
            for candidate in candidates:
                full_name = f"{candidate.first_name} {candidate.last_name}".lower()
                if full_name in query.lower() or full_name in ai_response.lower():
                    relevant_candidates.append({
                        "id": str(candidate.id),
                        "name": f"{candidate.first_name} {candidate.last_name}",
                        "email": candidate.email
                    })
            
            return {
                "response": ai_response,
                "candidates": relevant_candidates[:5],  # Max 5
                "jobs": []
            }
        
        except Exception as e:
            print(f"Error in chat: {e}")
            return {
                "response": f"Error: {str(e)}",
                "candidates": [],
                "jobs": []
            }
'''
