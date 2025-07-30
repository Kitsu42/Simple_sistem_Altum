from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def read_example():
    return {"msg": "Example router funcionando!"}
