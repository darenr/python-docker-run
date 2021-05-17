from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse

from starlette.routing import Route

from jobs.job_driver import (
    create_job,
    run_job,
)


async def proxy_create_job(request):

    j = await request.json()

    job_ocid = create_job(j["runtime"], j["job_spec"])

    return JSONResponse({"job_ocid": job_ocid})


async def proxy_run_job(request):
    j = await request.json()
    job_ocid = j["job_ocid"]

    try:
        return StreamingResponse(run_job(job_ocid), media_type="text/plain")

    except ValueError as e:
        raise HTTPException(status_code, detail=e.message)


# fmt: off
app = Starlette(
    debug=True,
    routes=[
        Route('/run_job', proxy_run_job),
        Route('/create_job', proxy_create_job)
    ]
)
# fmt: on
