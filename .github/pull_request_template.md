# Pull Request

## 📋 Description

<!-- Provide a brief description of the changes in this PR -->

## 🎯 Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Configuration change
- [ ] 🧪 Test improvement
- [ ] ♻️ Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🔒 Security improvement

## 🔗 Related Issues

<!-- Link to related issues using keywords like "Fixes #123" or "Closes #456" -->

- Fixes #
- Related to #

## 🧪 Testing

### Test Coverage
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All existing tests pass
- [ ] Test coverage meets requirements (90%+)

### Manual Testing
<!-- Describe the manual testing performed -->

- [ ] Tested locally
- [ ] Tested in staging environment
- [ ] API endpoints tested with Postman/curl
- [ ] Database migrations tested

### Test Commands
```bash
# Commands used to test the changes
pytest tests/unit/test_new_feature.py -v
pytest tests/integration/ -v
```

## 🔒 Security Checklist

- [ ] No sensitive data (passwords, keys, tokens) in code
- [ ] Input validation implemented where needed
- [ ] Authentication/authorization properly implemented
- [ ] SQL injection prevention measures in place
- [ ] Security scan passed (bandit, safety)

## 📊 Performance Impact

<!-- Describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance impact assessed and acceptable
- [ ] Load testing performed (if applicable)

## 🗄️ Database Changes

- [ ] No database changes
- [ ] Database migration included
- [ ] Migration tested locally
- [ ] Migration is reversible
- [ ] Data migration strategy documented (if applicable)

## 📚 Documentation

- [ ] Code is self-documenting with clear variable/function names
- [ ] Docstrings added/updated for new functions/classes
- [ ] API documentation updated (if applicable)
- [ ] README updated (if applicable)
- [ ] CHANGELOG updated (if applicable)

## 🚀 Deployment Notes

<!-- Any special deployment considerations -->

- [ ] No special deployment requirements
- [ ] Environment variables need to be updated
- [ ] Configuration changes required
- [ ] Service restart required
- [ ] Database migration required

### Environment Variables
<!-- List any new environment variables -->

```bash
# New environment variables (if any)
NEW_VARIABLE=value
```

## ✅ Pre-merge Checklist

- [ ] Code follows project style guidelines (ruff, mypy)
- [ ] Self-review completed
- [ ] Code is properly commented
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] CI/CD pipeline passes
- [ ] Security scan passes
- [ ] Code owners have reviewed (if applicable)

## 📸 Screenshots/Logs

<!-- Include screenshots, logs, or other relevant media -->

## 🤔 Questions for Reviewers

<!-- Any specific areas you'd like reviewers to focus on -->

## 📝 Additional Notes

<!-- Any additional information that would be helpful for reviewers -->

---

### Reviewer Guidelines

**For Reviewers:**
- [ ] Code quality and style
- [ ] Test coverage and quality
- [ ] Security considerations
- [ ] Performance implications
- [ ] Documentation completeness
- [ ] API design (if applicable)
- [ ] Database design (if applicable)

**Review Focus Areas:**
- Business logic correctness
- Error handling
- Edge cases
- Code maintainability
- Security vulnerabilities
