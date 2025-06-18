# Makefile for building the research paper

# Default target
all: markdown latex docx

# Build the complete markdown file
markdown:
	python paper_tools.py combine

# Convert markdown to PDF
markdown-pdf: markdown
	python paper_tools.py pdf

# Build LaTeX PDF
latex:
	pdflatex paper.tex
	bibtex paper
	pdflatex paper.tex
	pdflatex paper.tex

# Build DOCX version
docx: markdown
	python paper_tools.py docx

# Clean up temporary files
clean:
	python paper_tools.py clean
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.lof *.lot *.fls *.fdb_latexmk *.synctex.gz

# Clean everything including output files
clean-all: clean
	rm -f complete_paper.md log_analyzer_paper_md.pdf paper.pdf log_analyzer_paper.docx

# Help target
help:
	@echo "Available targets:"
	@echo "  all         - Build markdown, latex, and docx versions"
	@echo "  markdown    - Build the complete markdown file"
	@echo "  markdown-pdf - Convert markdown to PDF"
	@echo "  latex       - Build the LaTeX PDF"
	@echo "  docx        - Build the Word DOCX version"
	@echo "  clean       - Remove temporary files"
	@echo "  clean-all   - Remove all generated files"
	@echo "  help        - Show this help message"

.PHONY: all markdown markdown-pdf latex docx clean clean-all help
