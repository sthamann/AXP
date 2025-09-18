# Contributing to AXP Protocol

Thank you for your interest in contributing to the Agentic Experience Protocol! This document provides guidelines and instructions for contributing to the project.

## 🎯 Vision

AXP aims to make commerce experiences machine-readable for AI agents, enabling richer, more trustworthy, and more engaging shopping experiences. We welcome contributions that align with this vision.

## 📋 How to Contribute

### Reporting Issues

1. **Check existing issues** first to avoid duplicates
2. Use the appropriate issue template:
   - 🐛 Bug Report
   - ✨ Feature Request
   - 📚 Documentation Improvement
   - 💡 General Idea/Discussion

3. Provide detailed information:
   - Clear description of the issue
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details (OS, Node version, etc.)

### Proposing Changes

1. **Discuss first**: For significant changes, open an issue to discuss before implementing
2. **Follow the spec**: Ensure changes align with the AXP specification
3. **Maintain backwards compatibility**: Breaking changes require major version bump

### Pull Request Process

1. **Fork and clone** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**:
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed
4. **Test thoroughly**:
   ```bash
   npm test
   npm run lint
   npm run validate:schemas
   ```
5. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add support for new capsule modality"
   ```
6. **Push and create PR**:
   - Fill out the PR template completely
   - Link related issues
   - Request review from maintainers

## 🏗️ Development Setup

### Prerequisites

- Node.js 18+
- npm or yarn
- Git

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/axp-protocol.git
cd axp-protocol

# Install dependencies
npm install

# Run tests
npm test

# Start development server
npm run server:dev

# Run demo client
npm run demo:client
```

### Project Structure

```
axp-protocol/
├── schemas/axp/        # JSON Schema definitions
├── src/
│   ├── server/        # MCP server implementation
│   └── types/         # TypeScript types
├── examples/
│   ├── data/          # Example data files
│   └── capsules/      # Example experience capsules
├── docs/              # Documentation
└── tests/             # Test suites
```

## 📝 Coding Standards

### TypeScript/JavaScript

- Use TypeScript for new code
- Follow ESLint configuration
- Use async/await over callbacks
- Document complex functions with JSDoc

```typescript
/**
 * Calculate soft signal scores for a product
 * @param product - Product to analyze
 * @returns Calculated soft signals with evidence
 */
async function calculateSoftSignals(
  product: Product
): Promise<SoftSignals> {
  // Implementation
}
```

### Python

- Follow PEP 8 style guide
- Use type hints
- Document with docstrings

```python
def calculate_soft_signals(product: Product) -> SoftSignals:
    """
    Calculate soft signal scores for a product.
    
    Args:
        product: Product to analyze
        
    Returns:
        Calculated soft signals with evidence
    """
    # Implementation
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

Examples:
```
feat: add AR capsule modality support
fix: correct score calculation for sustainability
docs: update integration guide with Python examples
```

## 🧪 Testing

### Unit Tests

Write tests for all new functionality:

```typescript
describe('SoftSignals', () => {
  test('calculates uniqueness score correctly', () => {
    const product = createMockProduct();
    const score = calculateUniquenessScore(product);
    expect(score).toBeGreaterThanOrEqual(0);
    expect(score).toBeLessThanOrEqual(1);
  });
});
```

### Integration Tests

Test MCP tools end-to-end:

```typescript
describe('MCP Tools', () => {
  test('searchCatalog filters by soft signals', async () => {
    const results = await client.callTool('axp.searchCatalog', {
      filters: {
        soft_min: {
          sustainability_score: 0.7
        }
      }
    });
    
    results.items.forEach(item => {
      expect(item.soft_signals.sustainability_score).toBeGreaterThanOrEqual(0.7);
    });
  });
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- product.test.ts

# Run in watch mode
npm run test:watch
```

## 📚 Documentation

### When to Update Docs

Update documentation when you:
- Add new features
- Change API interfaces
- Modify schemas
- Add new examples
- Fix errors or clarify existing docs

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add diagrams where helpful
- Keep README focused on getting started
- Put detailed info in specific docs

### Building Documentation

```bash
# Generate TypeScript docs
npm run docs:generate

# Validate all links
npm run docs:validate
```

## 🔐 Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Email security@agentic-commerce.org with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Never commit secrets or API keys
- Validate all inputs
- Use parameterized queries
- Keep dependencies updated
- Follow OWASP guidelines

## 📦 Schema Changes

### Adding Fields

1. New fields should be optional initially
2. Document the field purpose and format
3. Update TypeScript types
4. Update Pydantic models
5. Add validation rules
6. Update examples

### Deprecating Fields

1. Mark as deprecated in schema
2. Add deprecation notice in docs
3. Maintain for at least 2 minor versions
4. Provide migration guide

## 🎨 Experience Capsules

### Creating New Capsules

1. Follow security guidelines strictly
2. Include comprehensive manifest
3. Implement full PostMessage API
4. Test in sandbox environment
5. Document parameters and events

### Capsule Guidelines

- Minimize external dependencies
- Respect resource limits
- Handle errors gracefully
- Provide fallback for older browsers
- Include accessibility features

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in package.json
- [ ] Schemas version updated
- [ ] Git tag created
- [ ] GitHub release created
- [ ] npm package published

## 🤝 Community

### Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Please read and follow it in all interactions.

### Getting Help

- **Discord**: [Join our community](https://discord.gg/agentic-commerce)
- **GitHub Discussions**: Ask questions and share ideas
- **Stack Overflow**: Tag with `axp-protocol`

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- GitHub contributors page
- Release notes

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make AXP better! 🎉
