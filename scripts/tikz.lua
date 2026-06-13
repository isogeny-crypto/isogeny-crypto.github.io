local script_dir = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local project_dir = pandoc.path.directory(script_dir)
local cache_dir = pandoc.path.join({project_dir, ".tikz-cache"})
local tikz2svg_path = pandoc.path.join({project_dir, "scripts", "tikz2svg.mjs"})

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

-- Fix the relative fonts.css import baked in by node-tikzjax
local function fix_font_path(svg)
  return svg:gsub("@import url%(fonts%.css%)", "@import url(/assets/fonts.css)")
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
      return pandoc.RawBlock("html", '<div class="tikz-diagram">' .. fix_font_path(svg) .. '</div>')
    end

    -- Otherwise render and save to cache
    local svg = pandoc.pipe("node", {tikz2svg_path}, el.text)

    local out = io.open(path, "w")
    if out then
      out:write(svg)
      out:close()
    end

    return pandoc.RawBlock("html", '<div class="tikz-diagram">' .. fix_font_path(svg) .. '</div>')
  end
end