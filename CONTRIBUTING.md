# Contributing to Smart System Health Monitor

Thank you for your interest in contributing to the Smart System Health Monitor! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for testing)
- Basic knowledge of Python, system monitoring, and machine learning

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/smart-system-health-monitor.git
   cd smart-system-health-monitor
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create configuration file**
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

4. **Run tests**
   ```bash
   python -c "import src.monitor; import src.alerts; import src.ml_predictor; print('All imports successful')"
   ```

## 📋 Contribution Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add email notification support
fix: resolve memory leak in monitoring loop
docs: update installation instructions
test: add unit tests for ML predictor
refactor: improve error handling in alerts module
```

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, well-documented code
   - Add tests if applicable
   - Update documentation

3. **Test your changes**
   ```bash
   # Test the dashboard
   streamlit run src/dashboard.py
   
   # Test monitoring
   python monitor_enhanced.py
   ```

4. **Submit a pull request**
   - Provide a clear description of changes
   - Reference any related issues
   - Include screenshots for UI changes

## 🎯 Areas for Contribution

### High Priority

- **Testing**: Add comprehensive unit and integration tests
- **Documentation**: Improve documentation and add examples
- **Performance**: Optimize monitoring and ML prediction performance
- **Security**: Enhance security for alerting and data storage

### Medium Priority

- **New Metrics**: Add support for additional system metrics
- **UI/UX**: Improve dashboard design and user experience
- **ML Models**: Implement additional machine learning algorithms
- **Deployment**: Add support for more deployment platforms

### Low Priority

- **Internationalization**: Add support for multiple languages
- **Themes**: Add dark/light theme support
- **Mobile**: Optimize dashboard for mobile devices
- **API**: Create REST API for external integrations

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_monitor.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Writing Tests

- Create test files in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

Example test structure:
```python
import unittest
from unittest.mock import patch, MagicMock
from src.monitor import SystemMonitor

class TestSystemMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = SystemMonitor()
    
    def test_cpu_usage_retrieval(self):
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.return_value = 50.0
            result = self.monitor.get_cpu_usage()
            self.assertEqual(result, 50.0)
```

## 📚 Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include examples for complex functions

Example:
```python
def predict_cpu_usage(self, metrics: Dict[str, Any], horizon: int = 10) -> Dict[str, Any]:
    """
    Predict CPU usage for the next N minutes.
    
    Args:
        metrics: Current system metrics
        horizon: Prediction horizon in minutes
        
    Returns:
        Dictionary containing predictions and confidence intervals
        
    Example:
        >>> predictor = MLPredictor()
        >>> metrics = {'cpu_usage': 50.0, 'ram_usage': 60.0}
        >>> result = predictor.predict_cpu_usage(metrics, 15)
        >>> print(result['cpu_usage']['value'])
        52.3
    """
```

### README Updates

- Update README.md for new features
- Add installation instructions for new dependencies
- Include configuration examples
- Update screenshots and demos

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment information**
   - Operating system and version
   - Python version
   - Package versions

2. **Steps to reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior

3. **Error messages**
   - Full error traceback
   - Log files if applicable

4. **Additional context**
   - Screenshots if relevant
   - Configuration files (remove sensitive data)

## 💡 Feature Requests

When requesting features, please provide:

1. **Problem description**
   - What problem does this solve?
   - Who would benefit from this feature?

2. **Proposed solution**
   - How should this feature work?
   - Any design considerations?

3. **Alternatives considered**
   - What other approaches were considered?
   - Why is this approach preferred?

## 🏷️ Release Process

### Version Numbering

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Update documentation
- [ ] Run all tests
- [ ] Test deployment scripts
- [ ] Create release notes

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: For security issues or private matters

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks or political discussions
- Spam or off-topic discussions

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to the Smart System Health Monitor! 🎉
