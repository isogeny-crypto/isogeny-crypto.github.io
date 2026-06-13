local script_dir = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local project_dir = pandoc.path.directory(script_dir)
local tikz2svg_path = pandoc.path.join({project_dir, "tikz2svg.mjs"})
local cache_dir = pandoc.path.join({project_dir, ".tikz-cache"})

local script_dir = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local project_dir = pandoc.path.directory(script_dir)
local tikz2svg_path = pandoc.path.join({project_dir, "tikz2svg.mjs"})
local cache_dir = pandoc.path.join({project_dir, ".tikz-cache"})

-- Make sure the cache directory exists
os.execute("mkdir -p " .. cache_dir)

-- Simple hash: turn the source into a safe filename
local function hash(str)
  local h = 5381
  for i = 1, #str do
    h = ((h * 33) + string.byte(str, i)) % 0x7FFFFFFF
  end
  return string.format("%x", h)
end

function CodeBlock(el)
  if el.classes:includes("tikz") then
    local key  = hash(el.text)
    local path = pandoc.path.join({cache_dir, key .. ".svg"})

    -- Return cached SVG if it exists
    local f = io.open(path, "r")
    if f then
      local svg = f:read("*a")
      f:close()
      return pandoc.RawBlock("html", '<div class="tikz-diagram">' .. svg .. '</div>')
    end

    -- Otherwise render and save to cache
    local svg = pandoc.pipe("node", {tikz2svg_path}, el.text)

    local out = io.open(path, "w")
    if out then
      out:write(svg)
      out:close()
    end

    return pandoc.RawBlock("html", '<div class="tikz-diagram">' .. svg .. '</div>')
  end
end