from fastapi import FastAPI


app = FastAPI(title="ArthaPilot")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
