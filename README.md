# Medicine Prescription Analyzer

## Overview

The Medicine Prescription Analyzer is an advanced tool designed to streamline the process of analyzing and interpreting medical prescriptions, with a focus on veterinary applications. By combining Optical Character Recognition (OCR) technology with the power of OpenAI's language models, this project aims to improve accuracy and efficiency in prescription handling.

## Key Features

- **OCR Integration**: Extract text from handwritten or printed medical prescriptions.
- **OpenAI-Powered Analysis**: Utilize GPT-3.5-turbo or GPT-4-turbo models to interpret prescription content.
- **Dosage Calculation**: Automatically calculate and verify dosage information.
- **Ingredient Identification**: Cross-reference prescriptions with a database of antimicrobial ingredients.
- **Structured Output**: Generate organized Excel reports with analyzed prescription data.

## Prerequisites

- Python 3.7 or higher
- OpenAI API key
- OCR library (specifics to be determined based on implementation)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/parthsshetty04/Med-Script
   cd Med-Script
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up OpenAI API credentials:
   - Set environment variables:
     ```bash
     export OPENAI_ORGANIZATION="your-organization-id"
     export OPENAI_API_KEY="your-api-key"
     ```
   - Or modify the script directly (not recommended for security reasons).

## Usage

1. Prepare input files:
   - Place prescription images or scanned documents in the `input/images/` directory.
   - Update `ingredient_list.csv` with relevant antimicrobial ingredients.

2. Run the analyzer:
   ```bash
   python run_analyzer.py
   ```

3. Find the output Excel file in the `output/` directory.

## Configuration

Modify `config.py` to customize:
- Input and output file paths
- OpenAI model selection (GPT-3.5-turbo or GPT-4-turbo)
- OCR settings
- Analysis parameters

## Testing

1. Use sample prescriptions provided in `tests/sample_prescriptions/` for initial testing.
2. Run the test suite:
   ```bash
   python -m unittest discover tests
   ```

## Troubleshooting

- Ensure all environment variables are correctly set.
- Check OpenAI API rate limits and quotas.
- Refer to error messages in the console output for specific issues.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- OpenAI for providing the GPT models
- Contributors to the OCR libraries used in this project

## Citation

If you use this tool in your research, please cite:

Brian Hur, Lucy Lu Wang, Laura Hardefeldt, and Meliha Yetisgen. 2024. [*Is That the Right Dose? Investigating Generative Language Model Performance on Veterinary Prescription Text Analysis*](https://aclanthology.org/2024.bionlp-1.30/). In Proceedings of the 23rd Workshop on Biomedical Natural Language Processing, pages 390–397, Bangkok, Thailand. Association for Computational Linguistics.
