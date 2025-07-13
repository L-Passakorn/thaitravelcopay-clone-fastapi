from fastapi import APIRouter


router = APIRouter(prefix="/hello", tags=["hello"])


@router.get(
    "",
    summary="Say Hello",
    description="Returns a simple greeting message.",
)
async def say_hello() -> str:
    """Endpoint to say hello."""
    return "Hello, World!"


@router.post(
    "/add-operation",
)
async def add(a: int | float, b: int | float) -> int | float:
    return a + b
