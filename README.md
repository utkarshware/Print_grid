**Print Grid**

A small Python script that fetches a public Google Doc containing coordinate/character data and prints the character grid formed by those points.

**Requirements**

- **Python:**: Python 3.8+ (no external packages required)

**Usage**

- **Run:**: Fetches a Google Doc (must be publicly viewable) and prints the grid to stdout.

```batch
python print_grid.py <google-doc-url>
```

- **Function:**: The script exposes a callable function `print_grid_from_doc_url(url)` which can be imported and used from other Python code.

**Input format**

- **Inline triplets:**: Lines containing coordinate and character triplets such as `12 5 #` or `12,5,#` (the parser supports typical separators).
- **U+HEX tokens:**: Characters may be specified using Unicode codepoints like `U+2588`.
- **Vertical triplets:**: The document may list triplets vertically (three lines: `x` on one line, `char` on the next, `y` on the next). The parser attempts to handle this format as well.
- **Notes:**: The parser tolerates multiple formats and will print a warning (to stderr) for malformed inline lines it cannot parse.

**Output orientation**

- **Y-axis:**: `y` increases downwards; the printed rows go from minimum `y` at the top to maximum `y` at the bottom.

**Examples**

- Run against a Google Doc URL (replace `<google-doc-url>`):

```batch
python print_grid.py "https://docs.google.com/document/d/EXAMPLE_ID/edit"
```

- If your Windows console cannot render block characters, either change code page to UTF-8 before running:

```batch
chcp 65001
python print_grid.py <google-doc-url>
```

or redirect output to a UTF-8 file and open it in an editor that supports Unicode:

```batch
python print_grid.py <google-doc-url> > grid.txt
```

**Troubleshooting**

- **No coordinate data found:** Ensure the Google Doc is exported as plain text (`export?format=txt`) and is publicly readable. The script attempts to use the Google Docs export endpoint but requires the document to be accessible.
- **Unicode / encoding issues:** If you see `UnicodeEncodeError` when printing block characters on Windows, change terminal encoding to UTF-8 (`chcp 65001`), use PowerShell, or redirect output to a file.


