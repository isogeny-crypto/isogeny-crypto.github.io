local script_dir = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local project_dir = pandoc.path.directory(script_dir)
local contributors_dir = pandoc.path.join({project_dir, ".contributors"})

function Pandoc(doc)
  local title = doc.meta["title"]
  if not title then return doc end
  title = pandoc.utils.stringify(title)

  -- Match snippet file by title (case-insensitive substring match on stem)
  local title_lower = title:lower()
  local matched_path = nil

  local handle = io.popen("ls " .. contributors_dir)
  if not handle then return doc end
  for filename in handle:lines() do
    local stem = filename:match("^(.+)%.md$")
    if stem and title_lower:find(stem:lower(), 1, true) then
      matched_path = pandoc.path.join({contributors_dir, filename})
      break
    end
  end
  handle:close()

  if not matched_path then return doc end

  local f = io.open(matched_path, "r")
  if not f then return doc end
  local content = f:read("*a")
  f:close()

  doc.blocks:insert(pandoc.HorizontalRule())
  local snippet_doc = pandoc.read(content, "markdown")
  for _, block in ipairs(snippet_doc.blocks) do
    doc.blocks:insert(block)
  end

  return doc
end