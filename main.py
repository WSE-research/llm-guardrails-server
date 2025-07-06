from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models import ModerationRequest, ModerationResponse
from service import ModerationService

# Initialize FastAPI app
app = FastAPI(
    title="LLM Guardrails Server",
    description="A moderation server compatible with OpenAI's moderation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Update to specific origins in production
    allow_credentials=True,
    allow_methods=["*"], # TODO: Update to specific methods in production
    allow_headers=["*"], # TODO: Update to specific headers in production
)

# Initialize moderation service
moderation_service = ModerationService(use_bert=True, flagging_threshold=0.5)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LLM Guardrails Server",
        "version": "0.1.0",
        "endpoints": {
            "moderation": "/v1/moderations",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "bert_available": moderation_service.use_bert,
        "regex_available": True
    }


@app.post("/v1/moderations", response_model=ModerationResponse)
async def create_moderation(request: ModerationRequest):
    """
    Create a moderation analysis for the provided input.
    
    Compatible with OpenAI's moderation API format.
    """
    try:
        result = moderation_service.moderate(
            input_data=request.input,
            model=request.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Moderation failed: {str(e)}") from e


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
