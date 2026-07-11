-- discs.lua
-- Expands shorthand []{r=.. g=.. b=..} spans into colored "disc" bullets,
-- so scheme lists in .qmd files can write e.g.:
--
--   - []{r=50 b=50} pSIDH (2022--2023)
--
-- instead of writing out the raw HTML/CSS by hand. r/g/b are percentages
-- (0-100) for red / green / blue, matching the wiki's legend:
--   r = torsion points, b = Deuring correspondence, g = group action.
-- Any subset of r/g/b may be given; a single color (e.g. []{r=100}) gives
-- a solid disc, two or three give a split conic-gradient disc in that
-- ratio, read clockwise starting at 12 o'clock in the order r, b, g.

local order = { "r", "b", "g" }
local color_var = {
  r = "var(--dot-red)",
  b = "var(--dot-blue)",
  g = "var(--dot-green)",
}

function Span(el)
  local stops = {}
  for _, key in ipairs(order) do
    local raw = el.attributes[key]
    if raw then
      local pct = tonumber(raw)
      if pct and pct > 0 then
        table.insert(stops, { key = key, pct = pct })
      end
    end
  end

  if #stops == 0 then
    return nil -- not one of ours, leave untouched
  end

  local css
  if #stops == 1 then
    css = "background: " .. color_var[stops[1].key] .. ";"
  else
    local parts = {}
    local cursor = 0
    for _, s in ipairs(stops) do
      local from, to = cursor, cursor + s.pct
      table.insert(parts, color_var[s.key] .. " " .. from .. "% " .. to .. "%")
      cursor = to
    end
    css = "background: conic-gradient(" .. table.concat(parts, ", ") .. ");"
  end

  return pandoc.RawInline(
    "html",
    '<span class="scheme-disc" style="' .. css .. '"></span>'
  )
end