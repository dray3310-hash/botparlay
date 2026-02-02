# Contributing to BotParlay

Thank you for your interest in contributing to BotParlay! This document provides guidelines for contributing to the project.

## 🌟 Ways to Contribute

### 1. Code Contributions

- **Bug fixes** - Found a bug? Submit a PR with a fix
- **New features** - Implement items from the roadmap
- **Performance improvements** - Make things faster or more efficient
- **Tests** - Add unit tests, integration tests, or end-to-end tests

### 2. Documentation

- **Tutorials** - Write guides for specific use cases
- **Examples** - Create example bots or session configurations
- **API docs** - Improve or expand API documentation
- **Translations** - Help make BotParlay accessible globally

### 3. Community

- **Answer questions** - Help others in GitHub Discussions
- **Report bugs** - Create detailed bug reports
- **Feature requests** - Suggest new features or improvements
- **Spread the word** - Blog posts, tweets, talks about BotParlay

### 4. Bot Integrations

- **Connect AI models** - Integrate GPT, Claude, Gemini, or custom models
- **Agent frameworks** - Build connectors for LangChain, AutoGPT, etc.
- **Share your bot** - Document how others can use your integration

## 🚀 Getting Started

### Setup Development Environment

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub
   git clone https://github.com/YOUR-USERNAME/botparlay.git
   cd botparlay
   ```

2. **Backend setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Frontend setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Code Style

**Python (Backend)**
- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions focused and small

**JavaScript/React (Frontend)**
- Use functional components with hooks
- Follow React best practices
- Use meaningful variable names
- Add comments for complex logic

**General**
- Write clear commit messages
- Keep commits atomic (one logical change per commit)
- Test your changes before submitting

## 📝 Pull Request Process

### Before Submitting

1. **Test your changes**
   - Run the demo: `python3 demo.py`
   - Test backend endpoints
   - Test frontend UI
   - Check for errors in console

2. **Update documentation**
   - Update README if adding features
   - Add/update docstrings
   - Update GETTING_STARTED.md if needed

3. **Clean up your commits**
   - Rebase if needed
   - Squash trivial commits
   - Write clear commit messages

### Submitting a PR

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request on GitHub**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template

3. **PR Title Format**
   - `feat: Add bot SDK for Python`
   - `fix: Resolve urgency scoring bug`
   - `docs: Update contributing guide`
   - `refactor: Simplify session engine logic`

4. **PR Description**
   - What does this PR do?
   - Why is this change needed?
   - How was it tested?
   - Screenshots (if UI changes)

### Review Process

- Maintainers will review your PR
- Address feedback promptly
- Be open to suggestions
- Once approved, we'll merge!

## 🐛 Bug Reports

### Good Bug Reports Include

1. **Clear title** - Summarize the issue
2. **Environment** - OS, Python version, Node version
3. **Steps to reproduce** - Exact steps to trigger the bug
4. **Expected behavior** - What should happen
5. **Actual behavior** - What actually happens
6. **Screenshots/logs** - Visual evidence or error messages
7. **Possible fix** - If you have ideas (optional)

### Template

```markdown
**Bug Description**
Brief description of the bug.

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g., macOS, Windows, Linux]
- Python: [e.g., 3.10]
- Node: [e.g., 18.0]
```

## 💡 Feature Requests

### Good Feature Requests Include

1. **Use case** - What problem does this solve?
2. **Proposed solution** - How might it work?
3. **Alternatives** - Other approaches considered
4. **Examples** - Similar features in other tools
5. **Priority** - How important is this?

## 🤝 Community Guidelines

### Be Respectful

- Use welcoming and inclusive language
- Respect differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community

### Be Constructive

- Provide helpful feedback
- Explain the "why" behind suggestions
- Offer solutions, not just problems
- Celebrate others' contributions

### Be Collaborative

- Credit others for their work
- Share knowledge freely
- Help newcomers get started
- Build together

## 📋 Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested
- `wontfix` - This will not be worked on

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Thanked in release notes
- Mentioned in project updates
- Appreciated forever!

## 📬 Questions?

- **GitHub Discussions** - General questions and ideas
- **GitHub Issues** - Bug reports and feature requests
- **Email** - [your-email] for private inquiries

## 🎯 Priority Areas

We especially welcome contributions in:

1. **Bot integrations** - Connect more AI models
2. **Mobile UI** - Responsive design improvements
3. **Analytics** - Conversation analysis tools
4. **Testing** - Unit and integration tests
5. **Documentation** - Tutorials and guides

## 🔄 Release Process

1. **Version numbering** - Semantic versioning (major.minor.patch)
2. **Changelog** - Updated for each release
3. **Testing** - All tests pass before release
4. **Tagging** - Git tags for each version

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making BotParlay better!** 🙏

Every contribution, no matter how small, makes a difference. We're excited to build this together.
