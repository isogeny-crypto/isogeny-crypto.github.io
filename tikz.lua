function CodeBlock(el)
  if el.classes:includes("tikz") then
    local html = '<div class="tikz-diagram">'
              .. '<script type="text/tikz">\n'
              .. el.text
              .. '\n</script>'
              .. '</div>'
    return pandoc.RawBlock("html", html)
  end
end