# Log Analyzer Research Paper

This directory contains all files related to the research paper "Log Analyzer: A Versatile Framework for Multi-Format Log Analysis in Cybersecurity Applications".

## Directory Structure

- **Individual Sections**: Each section of the paper is maintained as a separate Markdown file for easier editing and version control.
- **Figures**: All diagrams and visual assets are stored in the `figures/` directory.
- **Bibliography**: References are maintained in BibTeX format in `bibliography.bib`.
- **LaTeX Template**: A complete LaTeX template is provided in `paper.tex` for academic publication.

## Files

### Main Files
- `main.md` - Complete paper combining all sections
- `paper.tex` - LaTeX template for academic publication
- `bibliography.bib` - BibTeX bibliography file
- `paper_outline.md` - Detailed outline of the paper structure

### Paper Sections
- `abstract_introduction.md` - Abstract and Introduction
- `related_work.md` - Review of existing log analysis tools
- `system_architecture.md` - Overall framework design and components
- `log_format_support.md` - Details on supported log formats
- `remote_log_acquisition.md` - Remote log collection capabilities
- `data_processing.md` - Data processing and analysis techniques
- `visualization_techniques.md` - Visualization approaches
- `case_studies.md` - Real-world application examples
- `performance_evaluation.md` - Benchmarks and comparisons
- `future_work.md` - Future research directions
- `conclusion.md` - Summary of contributions
- `references.md` - References in Markdown format
- `appendices.md` - Additional implementation details

### Figures
- `figures/` - Directory containing all diagrams and visual assets

## Building the Paper

### Using the Unified Tool
The easiest way to work with the paper is using the provided `paper_tools.py` script:

```bash
# Combine all sections into a single markdown file
python paper_tools.py combine

# Create a Word document
python paper_tools.py docx

# Create a PDF document (requires pandoc)
python paper_tools.py pdf

# Clean up temporary files
python paper_tools.py clean

# Show help information
python paper_tools.py help
```

### Using the Makefile
You can also use the provided Makefile:

```bash
# Build all formats (markdown, latex, docx)
make all

# Build only the docx version
make docx

# Build only the PDF from LaTeX
make latex

# Show all available targets
make help
```

### LaTeX to PDF
To generate a PDF from the LaTeX template:

```bash
# Compile LaTeX to PDF
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

## Contributing

When editing the paper:

1. Make changes to the individual section files rather than the combined `main.md`
2. Update the bibliography when adding new references
3. Place new figures in the `figures/` directory following the naming convention
4. Run the build process to generate an updated PDF

## Publication Target

This paper is being prepared for submission to:
- IEEE Transactions on Information Forensics and Security
- ACM Transactions on Privacy and Security
- Journal of Cybersecurity (Oxford Academic)

## Contact

For questions or contributions, please contact [Your Name] at [your.email@example.com].
