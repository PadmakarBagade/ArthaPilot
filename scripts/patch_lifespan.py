"""Migrate @app.on_event('startup') to lifespan context manager in main.py."""
import pathlib

main_path = pathlib.Path(__file__).parent.parent / "backend" / "app" / "main.py"
content = main_path.read_text(encoding="utf-8")

# Step 1: Add contextlib import if not already present
if "asynccontextmanager" not in content:
    content = content.replace(
        "import csv\nimport json\nfrom uuid import uuid4",
        "import csv\nimport json\nfrom contextlib import asynccontextmanager\nfrom uuid import uuid4",
        1,
    )
    print("[1] Added asynccontextmanager import")
else:
    print("[1] asynccontextmanager already present")

# Step 2: Replace create_tables() call + app = FastAPI + on_event block
OLD_BLOCK = (
    "app = FastAPI(title=\"ArthaPilot\")\n"
    "create_tables()\n"
    "MAX_UPLOAD_BYTES = settings.upload_max_size_mb * 1024 * 1024\n"
    "app.add_middleware(\n"
    "    CORSMiddleware,\n"
    "    allow_origins=settings.cors_origin_list,\n"
    "    allow_credentials=True,\n"
    "    allow_methods=[\"*\"],\n"
    "    allow_headers=[\"*\"],\n"
    ")\n"
    "\n"
    "\n"
    "@app.on_event(\"startup\")\n"
    "def startup_event():\n"
    "    if settings.seed_demo:\n"
    "        with Session(bind=engine) as db:\n"
    "            seed_demo(db)\n"
)

NEW_BLOCK = (
    "@asynccontextmanager\n"
    "async def lifespan(app_instance: FastAPI):\n"
    "    create_tables()\n"
    "    if settings.seed_demo:\n"
    "        with Session(bind=engine) as db:\n"
    "            seed_demo(db)\n"
    "    yield\n"
    "\n"
    "\n"
    "app = FastAPI(title=\"ArthaPilot\", lifespan=lifespan)\n"
    "MAX_UPLOAD_BYTES = settings.upload_max_size_mb * 1024 * 1024\n"
    "app.add_middleware(\n"
    "    CORSMiddleware,\n"
    "    allow_origins=settings.cors_origin_list,\n"
    "    allow_credentials=True,\n"
    "    allow_methods=[\"*\"],\n"
    "    allow_headers=[\"*\"],\n"
    ")\n"
)

if OLD_BLOCK in content:
    content = content.replace(OLD_BLOCK, NEW_BLOCK, 1)
    print("[2] Replaced on_event with lifespan OK")
else:
    print("[2] OLD_BLOCK not found — checking...")
    idx = content.find("@app.on_event")
    if idx >= 0:
        print(repr(content[max(0, idx-300):idx+200]))
    else:
        print("No @app.on_event found either!")

main_path.write_text(content, encoding="utf-8")
print("Done — written back to", main_path)

