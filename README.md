# claude-sucks-not
## intro
Sucking in (or straight out refusiong to) processing multiple PDFs forced author to apply what he learnt from exam with cheat sheets: cheating the sheets by putting as many slides in one page as possible. Human's pair of eyes will work a bit harder the smaller a PDF gets, but not Claude. So long as it is above the readable threshold, it does not mind. It is just the number of PDF pages it minds, duh.

## tldr
Fit multiple PDF pages onto a single output page.

# instructions
 
## setup
 
```bash
pip install -r requirements.txt
```
 
## usage
 
```bash
python pdf.py <input.pdf> <slides_per_page> [output.pdf]
```
 
## examples
 
```bash
python pdf.py aima_atwin.pdf 4
python pdf.py strategi_prabowo.pdf 2 handout.pdf
```
 
Supported values for `slides_per_page`: `1, 2, 4, 6, 8, 9, 16`
PDF files to process are in the `pdfs` folder
 