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

-- Wrap the SVG; {.tikz fig-alt="..."} becomes the diagram's accessible name,
-- so screen readers announce a description instead of raw SVG glyphs.
local function wrap(svg, alt)
  local attrs = 'class="tikz-diagram"'
  if alt and alt ~= "" then
    local escaped = alt:gsub("&", "&amp;"):gsub('"', "&quot;"):gsub("<", "&lt;"):gsub(">", "&gt;")
    attrs = attrs .. ' role="img" aria-label="' .. escaped .. '"'
  end
  return pandoc.RawBlock("html", "<div " .. attrs .. ">" .. fix_font_path(svg) .. "</div>")
end

function CodeBlock(el)
  if el.classes:includes("tikz") then
    local alt  = el.attributes["fig-alt"]
    local key  = hash(el.text)
    local path = pandoc.path.join({cache_dir, key .. ".svg"})

    -- Return cached SVG if it exists
    local f = io.open(path, "r")
    if f then
      local svg = f:read("*a")
      f:close()
      return wrap(svg, alt)
    end

    -- Otherwise render and save to cache
    local ok, svg = pcall(pandoc.pipe, "node", {tikz2svg_path}, el.text)
    if not ok then
      error("TikZ diagram failed to render in " .. tostring(quarto.doc.input_file)
        .. (alt and (' (fig-alt "' .. alt .. '")') or "")
        .. ". Check for unsupported packages/fonts or several \\usetikzlibrary lines.")
    end

    local out = io.open(path, "w")
    if out then
      out:write(svg)
      out:close()
    end

    return wrap(svg, alt)
  end
end