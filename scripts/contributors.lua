local script_dir = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local project_dir = pandoc.path.directory(script_dir)
local contributors_dir = pandoc.path.join({project_dir, ".contributors"})

function Pandoc(doc)
  local input_file = PANDOC_STATE.input_files[1]
  if not input_file then return doc end

  -- Extract filename stem without extension (works on all Pandoc versions)
  local stem = input_file:match("([^/\\]+)%.qmd$")
  if not stem then return doc end

  local snippet_path = pandoc.path.join({contributors_dir, stem .. ".md"})

  local f = io.open(snippet_path, "r")
  if not f then return doc end

  local content = f:read("*a")
  f:close()

  local snippet_doc = pandoc.read(content, "markdown")
  for _, block in ipairs(snippet_doc.blocks) do
    doc.blocks:insert(block)
  end

  return doc
end