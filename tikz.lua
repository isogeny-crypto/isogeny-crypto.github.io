local script_dir = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local tikz2svg_path = pandoc.path.join({script_dir, "tikz2svg.mjs"})

function CodeBlock(el)
  if el.classes:includes("tikz") then
    local svg = pandoc.pipe("node", {tikz2svg_path}, el.text)
    local html = '<div class="tikz-diagram">' .. svg .. '</div>'
    return pandoc.RawBlock("html", html)
  end
end