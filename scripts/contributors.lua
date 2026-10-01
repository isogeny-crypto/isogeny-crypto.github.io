-- Absolute project root. quarto.project.directory is unset when previewing a
-- single file, so fall back to this script's location (<root>/scripts/),
-- which PANDOC_SCRIPT_FILE gives relative to the page's own directory.
local function project_root()
  local dir = quarto.project and quarto.project.directory
  if dir and dir ~= "" then return dir end
  local root = pandoc.path.directory(pandoc.path.directory(PANDOC_SCRIPT_FILE))
  if pandoc.path.is_absolute(root) then return root end
  local abs = pandoc.system.get_working_directory()
  for _, part in ipairs(pandoc.path.split(root)) do
    if part == ".." then
      abs = pandoc.path.directory(abs)
    elseif part ~= "." then
      abs = pandoc.path.join({abs, part})
    end
  end
  return abs
end

local function has_refs_div(blocks)
  for _, block in ipairs(blocks) do
    if block.t == "Div" and block.identifier == "refs" then
      return true
    end
  end
  return false
end

local function has_citations(doc)
  local found = false
  doc:walk({
    Cite = function(_)
      found = true
    end
  })
  return found
end

-- schemes/key-establishment/sidh.qmd -> .contributors/schemes/key-establishment/sidh.md
-- (must match snippet_path_for() in fetch_contributors.py)
local function snippet_path()
  local input = quarto.doc.input_file
  if not input or input == "" then return nil end
  local root = project_root()
  local stem = pandoc.path.split_extension(pandoc.path.make_relative(input, root))
  return pandoc.path.join({root, ".contributors", stem .. ".md"})
end

function Pandoc(doc)
-- Insert {#refs} div if the document cites anything but has no refs block
  if doc.meta["bibliography"] and has_citations(doc) and not has_refs_div(doc.blocks) then
    doc.blocks:insert(pandoc.Header(2, pandoc.Inlines("References"), pandoc.Attr("references")))
    doc.blocks:insert(pandoc.Div({}, pandoc.Attr("refs")))
  end

  local matched_path = snippet_path()
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