# Pipeline rebuild notes

## Patterns to follow

- Keep bronze files as close to the original source as possible.
- Put all cleaning and feature logic in the silver processing layer.
- Max concurrency - Have the scheduler create all jobs up front and write them to the database first.
- Make each job small and explicit, like "download this sensor for this day" or "process this day for this dataset."
- Keep collectors/processors simple: one worker run should do one job only.
- Let the orchestrator decide what is ready to run by checking dependencies in the database.
- Store retry, backoff, and concurrency policy in orchestration state, not scattered across collector code.
- Use per-source concurrency/rate limits so one slow or rate-limited source doesn't block everything else.
- Test with live data only. No mocks or stubs. (Make it fast by using small samples, but only real data)

## Anti Patterns - DO NOT

- Add data engineering steps in the bronze layer.
- Clean, deduping, or reshaping data in bronze.
- Hide fan-out loops inside collectors or processors.
- Mix scheduler, orchestrator, and worker responsibilities.
- Write tests with mocks, stubs, or "test mode".
