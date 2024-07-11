const CTRL = "Ctrl";
const ALT = "Alt";
const ENTER = "↵ Enter";
const SPACE = "Space";
const BACKTICK = "&grave;";
const WINDOWS = "⊞"
const MENU = "☰";


function generate(content, style = "")
{
    modifier = ""
    if (Array.from("AD").includes(content))
        style = (`background: #aaaadd;`).concat(style)
    else if (Array.from("FH").includes(content))
        style = (`background: #ddaaaa;`).concat(style)
    else if (Array.from("JL").includes(content))
        style = (`background: #ddddaa;`).concat(style)
    else if (Array.from("←→").includes(content))
        style = (`background: #aaddaa;`).concat(style)
    else if ([SPACE, ENTER].includes(content))
        style = (`background: #aaaaaa;`).concat(style)

    if (style === "")
        return `<div class="keyin"><p${modifier}>${content}</p></div>`
    else 
        return `<div class="keyin" style="${style}"><p${modifier}>${content}</p></div>`
}

let rowdiv = '<div class="keyrow" style="width: 33em">'

html = '<div style="display: flex"><div>' 
html = html.concat(rowdiv)
html = html.concat(generate(BACKTICK, "min-width: 1.5em"))
for (let letter of "1234567890-=")
    html = html.concat(generate(letter))
html = html.concat(generate("Backspace", "width: 100%"))
html = html.concat(`</div>${rowdiv}`)
html = html.concat(generate("Tab", "min-width: 3em"))
for (let letter of "QWERTYUIOP[]")
    html = html.concat(generate(letter))
html = html.concat(generate("&bsol;", "width: 100%;"))
html = html.concat(`</div>${rowdiv}`)
html = html.concat(generate("Caps", "min-width: 4em"))
for (let letter of "ASDFGHJKL;'")
    html = html.concat(generate(letter))
html = html.concat(generate(ENTER, "width: 100%;"))
html = html.concat(`</div>${rowdiv}`)
html = html.concat(generate("Shift", "min-width: 5em;"))
for (let letter of "ZXCVBNM")
    html = html.concat(generate(letter))
html = html.concat(generate("&lt;"))
html = html.concat(generate("&gt;"))
html = html.concat(generate("/"))
html = html.concat(generate("Shift", "width: 100%;"))
html = html.concat(`</div>${rowdiv}`)
html = html.concat(generate(CTRL, "font-size: 10px"))
html = html.concat(generate(WINDOWS))
html = html.concat(generate(ALT, "font-size: 12px"))
html = html.concat(generate(SPACE, "width: 100%;"))
html = html.concat(generate(ALT, "font-size: 12px"))
html = html.concat(generate(WINDOWS))
html = html.concat(generate(MENU))
html = html.concat(generate(CTRL, "font-size: 10px"))
html = html.concat(`</div>`)
rowdiv = '<div class="keyrow" style="align-items: center; justify-content: center">'
html = html.concat(`</div><div style="margin: auto 0 0 10px">${rowdiv}`)
html = html.concat(generate("↑"))
html = html.concat(`</div>${rowdiv}`)
html = html.concat(generate("←"))
html = html.concat(generate("↓"))
html = html.concat(generate("→"))
html = html.concat(`</div>`)
html = html.concat('</div></div>')
console.log(html)