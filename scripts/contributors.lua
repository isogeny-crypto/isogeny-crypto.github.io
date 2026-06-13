local script_dir = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local project_dir = pandoc.path.directory(script_dir)
local contributors_dir = pandoc.path.join({project_dir, ".contributors"})

local function has_refs_div(blocks)
  for _, block in ipairs(blocks) do
    if block.t == "Div" and block.identifier == "refs" then
      return true
    end
  end
  return false
end

function Pandoc(doc)
  local title = doc.meta["title"]
  if not title then return doc end
  title = pandoc.utils.stringify(title)

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

-- Insert {#refs} div if the document cites anything but has no refs block
  if doc.meta["bibliography"] and not has_refs_div(doc.blocks) then
    doc.blocks:insert(pandoc.HorizontalRule())
    doc.blocks:insert(pandoc.Header(2, "References"))
    doc.blocks:insert(pandoc.Div({}, pandoc.Attr("refs")))
  end

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