import tikzjax from 'node-tikzjax';
const tex2svg = typeof tikzjax === 'function' ? tikzjax : tikzjax.default;

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => (input += chunk));
process.stdin.on('end', async () => {
  // Pull out \usetikzlibrary{...} so it can be passed as an option,
  // since it doesn't always work fine left inline.
  let body = input;
  let tikzLibraries = '';
  const libMatch = body.match(/\\usetikzlibrary\{([^}]*)\}/);
  if (libMatch) {
    tikzLibraries = libMatch[1];
    body = body.replace(libMatch[0], '');
  }

  const source = `\\begin{document}\n${body}\n\\end{document}`;

  try {
    const svg = await tex2svg(source, {
      tikzLibraries,
      embedFontCss: true,
      fontCssUrl: '/tikzjax-assets/fonts.css', // reuse your self-hosted fonts
    });
    process.stdout.write(svg);
  } catch (err) {
    process.stderr.write(String(err));
    process.exit(1);
  }
});