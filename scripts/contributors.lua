local script_dir = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local project_dir = pandoc.path.directory(script_dir)
local contributors_dir = pandoc.path.join({project_dir, ".contributors"})

function Meta(meta)
  -- Store meta so we can use it in Blocks
  _meta = meta
  return meta
end

function Blocks(blocks)
  if not _meta then return blocks end

  -- Try to get source file from env variable Quarto sets
  local source = os.getenv("QUARTO_DOCUMENT_PATH")
  io.stderr:write("DEBUG QUARTO_DOCUMENT_PATH: " .. (source or "NIL") .. "\n")

  if not source then return blocks end

  local stem = source:match("([^/\\]+)%.qmd$")
  if not stem then return blocks end

  local snippet_path = pandoc.path.join({contributors_dir, stem .. ".md"})
  local f = io.open(snippet_path, "r")
  if not f then return blocks end

  local content = f:read("*a")
  f:close()

  local snippet_doc = pandoc.read(content, "markdown")
  for _, block in ipairs(snippet_doc.blocks) do
    blocks:insert(block)
  end

  return blocks
end