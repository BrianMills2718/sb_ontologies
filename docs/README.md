# Schema-Based Ontologies & Literature Analysis Pipeline

A comprehensive framework for applying theoretical frameworks to analyze texts using AI, with an interactive web interface for visualization and exploration.

## 🎯 Overview

This project systematically processes academic literature through a two-stage "Analyst & Assembler" workflow, creating structured, machine-readable representations of academic theories using JSON Schema and semantic networks. The system includes an interactive web UI for applying these frameworks to analyze any text using OpenAI's structured outputs.

## 🚀 Features

### 📚 Literature Processing Pipeline
- **50+ YAML Schemas**: Pre-processed theoretical frameworks from multiple disciplines
- **SchemaSage Methodology**: Systematic extraction of theoretical constructs
- **Post-processing**: Integration with universal CORE.json and sharedProps.json definitions

### 🎨 Interactive Web Interface
- **Framework Selection**: Nested categories (Argumentation → AIF/Toulmin, etc.)
- **Text Analysis**: Apply any framework to analyze any text
- **Rich Visualizations**: Charts, network graphs, and interactive displays
- **Chat Interface**: Ask questions about analysis results
- **Export Capabilities**: Download results as CSV/JSON

### 📊 Framework-Specific Visualizations
- **Information Disorder**: Agent flows, credibility analysis, interpretation modes
- **Argumentation**: Claim-evidence networks, argument strength distributions  
- **Behavior Change**: Technique effectiveness, intervention categorization
- **Cultural Evolution**: Meme transmission dynamics, selection pressures
- **Action Theory**: Metatheory applications across scales

## 🛠 Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Git

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/BrianMills2718/sb_ontologies.git
cd sb_ontologies
```

2. **Set up environment:**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your OpenAI API key
nano .env
```

3. **Launch the UI:**
```bash
./run_ui.sh
```

4. **Open in browser:**
Navigate to `http://localhost:8501`

## 📁 Project Structure

```
sb_ontologies/
├── literature/                 # Processed academic papers & schemas
│   ├── argumentation/          # AIF, Toulmin Method
│   ├── behavior_change/        # BCT Taxonomy, BCW, etc.
│   ├── information_disorder/   # Wardle & Derakhshan framework
│   ├── cultural_evolution/     # Memetics, transmission dynamics
│   ├── action_theory/          # Interdisciplinary synthesis
│   └── ...                     # 15+ other domains
├── texts/                      # Sample texts for analysis
│   ├── grusch_testimony.txt    # UAP congressional hearing
│   └── ...                     # Additional analysis targets
├── analysis_results/           # Generated analysis outputs
├── schema_analysis_ui.py       # Main web interface
├── extract_with_schema.py      # Core analysis engine
└── README.md                   # This file
```

## 🎮 Usage Examples

### 1. Information Disorder Analysis
```python
# Framework: Wardle & Derakhshan (2017)
# Text: Congressional testimony
# Output: Agents, messages, interpreters, credibility dynamics
```

### 2. Argumentation Analysis
```python
# Framework: AIF Specification or Toulmin Method
# Text: Policy debate transcript
# Output: Claims, evidence, rebuttals, argument structure
```

### 3. Behavior Change Analysis
```python
# Framework: BCT Taxonomy v1 (93 techniques)
# Text: Health intervention description
# Output: Technique categorization, effectiveness prediction
```

## 📊 Sample Visualizations

The UI automatically generates:
- **Pie Charts**: Distribution of entity types
- **Network Graphs**: Relationship structures
- **Bar Charts**: Frequency analyses
- **Scatter Plots**: Correlation patterns
- **Interactive Tables**: Sortable, filterable data

## 🧠 Theoretical Frameworks Included

### Core Domains (50+ frameworks):
- **Argumentation**: AIF, Toulmin Method
- **Behavior Change**: BCT Taxonomy, BCW, Intervention Mapping
- **Information Disorder**: Misinformation dynamics
- **Cultural Evolution**: Memetics, transmission theory
- **Action Theory**: 8 metatheories synthesis
- **Persuasion**: Elaboration likelihood, fear appeals
- **Social Marketing**: Kotler-Zaltman, social change models
- **Operational Code**: Leadership belief analysis
- **Decision Theory**: Poliheuristic, cognitive mapping

## 🔬 Methodology

### SchemaSage Analysis Process:
1. **Input**: Academic paper text
2. **Analysis**: AI generates YAML with 5 keys:
   - Citation
   - Annotation  
   - Model Type
   - Rationale
   - Schema Blueprint
3. **Assembly**: Python script injects universal definitions
4. **Output**: Complete, valid JSON Schema

### AI Integration:
- **OpenAI o3 Model**: Structured output generation
- **Pydantic Validation**: Schema compliance enforcement
- **Framework-Specific Prompts**: Tailored to each theory

## 📈 Results & Applications

### Demonstrated Applications:
- **UAP Testimony Analysis**: Information disorder framework applied to congressional hearing
- **Policy Document Analysis**: Argumentation frameworks for evidence assessment
- **Health Communication**: Behavior change technique identification
- **Media Analysis**: Cultural transmission pattern detection

### Research Impact:
- **Cross-Disciplinary Integration**: Bridge isolated theoretical traditions
- **Systematic Analysis**: Reproducible framework application
- **Visual Exploration**: Interactive theory validation
- **Empirical Testing**: Framework effectiveness measurement

## 🤝 Contributing

1. **Add New Frameworks**: Follow SchemaSage methodology
2. **Enhance Visualizations**: Framework-specific chart types
3. **Expand Text Corpus**: Additional analysis targets
4. **Improve UI**: User experience enhancements

## 📝 Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Fixed (DO NOT CHANGE)
OPENAI_MODEL=o3
```

## 🔒 Security Notes

- API keys are excluded from version control
- Environment variables managed through `.env` files
- No sensitive data committed to repository

## 📚 Academic Foundation

Based on established theoretical frameworks from:
- **Communication Theory**: Information disorder, persuasion models
- **Psychology**: Behavior change, cognitive processing
- **Political Science**: Operational code, decision analysis  
- **Sociology**: Cultural evolution, social movements
- **Computer Science**: Argumentation, knowledge representation

## 🎖 Citation

If you use this work in research, please cite:

```bibtex
@software{schema_ontologies_2025,
  title={Schema-Based Ontologies \& Literature Analysis Pipeline},
  author={Generated with Claude Code},
  year={2025},
  url={https://github.com/BrianMills2718/sb_ontologies},
  note={Interactive framework for applying theoretical models to text analysis}
}
```

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/BrianMills2718/sb_ontologies/issues)
- **Documentation**: See `/literature/Index.md` for full framework catalog
- **Examples**: Sample analyses in `/analysis_results/`

---

**🤖 Generated with [Claude Code](https://claude.ai/code)**

**Co-Authored-By: Claude <noreply@anthropic.com>**