# Lovart directory store

Saves The Queensland Legal Directory into a new Lovart project/task.

## Local catalog

```bash
node lovart/extract_directory.js
```

Writes:

- `lovart/directory.json` — full structured catalog
- `lovart/directory.brief.md` — compact board copy for Lovart

## New Lovart task

Set keys from Lovart → Avatar → AK/SK Management, then:

```bash
export LOVART_ACCESS_KEY="ak_xxx"
export LOVART_SECRET_KEY="sk_xxx"
python3 lovart/save_to_lovart.py
```

The script:

1. Rebuilds the local catalog from `js/directoryConstruct.js`
2. Runs `create-project` (new Lovart task)
3. Activates it as `theQLD Legal Directory`
4. Uploads the catalog when the CDN accepts the files
5. Starts a new thinking-mode thread that stores the directory on the canvas

State is written to `lovart/task.json`. Canvas URL shape:

`https://www.lovart.ai/canvas?projectId={project_id}`
