# 🧪 Fresh Installation Test

This folder contains test scripts and documentation to verify that the ATS system can be installed and configured from scratch following the main README.md instructions.

## 📋 Test Checklist

### Prerequisites Verification
- [ ] Node.js 18+ installed
- [ ] Python 3.9+ installed  
- [ ] PostgreSQL 13+ installed
- [ ] Git installed
- [ ] Groq API key obtained

### Installation Steps Test
- [ ] Repository clone successful
- [ ] Backend dependencies installation
- [ ] Frontend dependencies installation
- [ ] Database setup and schema creation
- [ ] Environment configuration
- [ ] Backend startup successful
- [ ] Frontend startup successful
- [ ] Admin user creation
- [ ] Basic functionality test

### Test Scripts

1. **`test-prerequisites.ps1`** - Verify all required software is installed
2. **`test-installation.ps1`** - Test complete installation process
3. **`test-functionality.ps1`** - Test basic application functionality
4. **`INSTALLATION_LOG.md`** - Document any issues encountered

## 🚀 Quick Test Run

```powershell
# Run all tests
.\run-all-tests.ps1

# Or run individual tests
.\test-prerequisites.ps1
.\test-installation.ps1
.\test-functionality.ps1
```

## 📝 Notes

- This test simulates a completely fresh environment
- Any issues found should be documented in INSTALLATION_LOG.md
- Successful tests validate the main README.md instructions
- Failed tests indicate areas needing improvement in documentation