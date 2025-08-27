# 🧪 LegalLex MVP2 - Testing Guide

This guide will walk you through testing all functionalities of the system before production deployment.

## 🆕 Recent Updates (Latest Version)
- **Logo Positioning**: Logos are now centered on login page and in the left sidebar
- **Enhanced Search**: Updated to use the optimized search method from `djesearchapp.py`
- **Admin File Management**: Admins can now delete uploaded analysis files
- **Robust Logging**: Comprehensive logging throughout the application with `app.log` file
- **Error Handling**: Improved error handling and user feedback
- **Bug Fixes**: Fixed SearchRule compatibility issues between different modules

> **Note**: These updates improve user experience, system reliability, and administrative capabilities. All functionality has been thoroughly tested and documented in this guide.

## 🚀 Setup for Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Application
```bash
# Method 1: Direct execution
streamlit run app.py

# Method 2: Full production test
./start_production.sh
```

The app will be available at: http://localhost:8501

---

## 🔐 Test Authentication System

### Test 1: Client Login (Caper)
1. Go to http://localhost:8501
2. You should see the login page with logo **centered**
3. Enter credentials:
   - **Username**: `Caper`
   - **Password**: `Caper`
4. Click "Entrar"
5. ✅ **Expected**: Login successful, redirect to client dashboard with logo **centered in left sidebar**

### Test 2: Admin Login (lucasaurich)
1. If already logged in, logout first
2. Enter credentials:
   - **Username**: `lucasaurich`
   - **Password**: `caneta123`
3. Click "Entrar"
4. ✅ **Expected**: Login successful, redirect to admin upload page with **centered logo**

### Test 3: Invalid Credentials
1. Try logging in with wrong credentials
2. ✅ **Expected**: Error message "Usuário ou senha inválidos!"

---

## 👤 Test Client (Caper) Functionalities

### Test 4: Navigate Client Dashboard
1. Login as `Caper`
2. Check sidebar navigation has 3 options:
   - ⚙️ Configurar Regras
   - 📋 Resultados Diários  
   - 🔍 Análises Inteligentes
3. ✅ **Expected**: All three pages accessible, logo visible on all pages

### Test 5: Configure Automation Rules
1. Go to "⚙️ Configurar Regras"
2. Check that next execution time is displayed (tomorrow 6:00 AM Brasília)
3. Click "➕ Adicionar Regra"
4. Fill out a test rule:
   - **Nome da Regra**: "Teste OAB"
   - **Tipo de Regra**: "Incluir"
   - **Número da OAB**: "8773"
   - **UF da OAB**: "ES"
   - **Data de Início**: Set to today's date
5. Click "💾 Salvar Regras"
6. ✅ **Expected**: Success message, rule appears in summary

### Test 6: Add Multiple Rules
1. Add another rule:
   - **Nome da Regra**: "Cliente Darwin"
   - **Tipo de Regra**: "Incluir"
   - **Nome da Parte**: "Darwin"
2. Add an exclusion rule:
   - **Nome da Regra**: "Excluir Teste"
   - **Tipo de Regra**: "Excluir"
   - **Número da OAB**: "14072"
   - **UF da OAB**: "ES"
3. ✅ **Expected**: Multiple rules configured and visible in summary

### Test 7: Test Manual Search (Daily Results Page)
1. Go to "📋 Resultados Diários"
2. Click "🔍 Executar Busca Manual (Teste)"
3. ✅ **Expected**: 
   - Progress indicators show
   - Search executes with configured rules
   - Results appear with pagination
   - Publications displayed as cards

### Test 8: View Daily Results
1. Stay on "📋 Resultados Diários" page
2. Change date selector to today
3. ✅ **Expected**: Results from manual test search are displayed

### Test 9: Análises Inteligentes (Empty State)
1. Go to "🔍 Análises Inteligentes"
2. ✅ **Expected**: Message "Nenhuma análise disponível no momento"

---

## 🔧 Test Admin (lucasaurich) Functionalities

### Test 10: Admin Upload Interface
1. Logout and login as `lucasaurich`
2. ✅ **Expected**: Upload page with file upload component and **centered logo**
3. Check that logo is displayed
4. Check logout button works
5. ✅ **Expected**: "Gerenciar Análises Existentes" section shows uploaded files with delete buttons

### Test 11: Upload Analysis Files
1. Create a test HTML file or use the existing `0038036-1620188080024_20250724_001749.html`
2. Click "Choose files" and select one or more HTML files
3. Click "📤 Enviar Análises"
4. ✅ **Expected**: 
   - Success message showing number of files uploaded
   - Counter shows "Total de análises disponíveis: X"

### Test 12: Upload Multiple Files and Test Deletion
1. Create 2-3 additional HTML test files:
```html
<!DOCTYPE html>
<html>
<head><title>Test Analysis</title></head>
<body><h1>Test Legal Analysis</h1><p>This is a test analysis.</p></body>
</html>
```
2. Upload multiple files at once
3. ✅ **Expected**: All files uploaded successfully
4. Check the "Gerenciar Análises Existentes" section
5. ✅ **Expected**: All uploaded files appear with delete buttons
6. Test deleting one file by clicking "🗑️ Deletar"
7. ✅ **Expected**: File is deleted and no longer appears in the list

---

## 🔄 Test Integration (Upload → View Cycle)

### Test 13: View Uploaded Analyses as Client
1. Logout from admin and login as `Caper`
2. Go to "🔍 Análises Inteligentes"
3. ✅ **Expected**:
   - Uploaded analyses appear as expandable cards
   - Pagination works (if more than 10 analyses)
   - HTML content displays correctly when expanded
   - No indication of who uploaded the files

### Test 14: Test Pagination
1. If you have 10+ analyses, test pagination
2. ✅ **Expected**: Page selector appears, content changes between pages

---

## ⏰ Test Cronjob System

### Test 15: Manual Cronjob Execution
```bash
# In a separate terminal, run:
python cronjob_scheduler.py test
```
1. ✅ **Expected**:
   - Console shows search execution progress
   - Creates `daily_results/results_YYYY-MM-DD.json` file
   - Creates/updates `cronjob.log` file

### Test 16: Check Saved Rules File
1. After configuring rules as Caper, check if `saved_rules.json` was created
2. ✅ **Expected**: File contains your configured rules in JSON format

### Test 17: Verify Cronjob Results in App
1. After running manual cronjob test (Test 15)
2. Login as `Caper` and go to "📋 Resultados Diários"
3. Select today's date
4. ✅ **Expected**: Results from cronjob execution are displayed

---

## 🕰️ Test Automated 6 AM Execution (Optional)

### Test 18: Simulate 6 AM Execution
**Option A: Wait for real 6 AM**
1. Leave the system running with `./start_production.sh`
2. Check at 6:01 AM Brasília time
3. ✅ **Expected**: New results file created, visible in client dashboard

**Option B: Modify schedule for testing**
1. Edit `cronjob_scheduler.py` line with `schedule.every().day.at("06:00")`
2. Change to a few minutes from now, e.g., `schedule.every().day.at("14:35")`
3. Restart the system and wait
4. ✅ **Expected**: Automatic execution occurs at scheduled time

---

## 🐳 Test Docker Deployment

### Test 19: Docker Build and Run
```bash
# Build and start with Docker Compose
docker-compose up -d

# Check if running
docker-compose ps

# View logs
docker-compose logs -f
```
1. ✅ **Expected**: Container starts successfully, app accessible at localhost:8501

### Test 20: Docker Persistence
1. Upload some analyses through admin interface
2. Configure some rules as client
3. Stop container: `docker-compose down`
4. Restart: `docker-compose up -d`
5. ✅ **Expected**: All data persists (analyses, rules, results)

---

## 📋 Test Logging and Error Handling

### Test 21: Application Logging
1. Start the application: `streamlit run app.py`
2. Check that `app.log` file is created in the project directory
3. Login as both admin and client users
4. Navigate through different pages
5. Upload and delete some files
6. Run a manual search
7. ✅ **Expected**: 
   - All actions are logged with timestamps
   - Log file contains INFO, WARNING, and ERROR messages
   - Console shows log output during operations

### Test 22: Error Handling and Recovery
1. Try actions that might cause errors (invalid files, network issues)
2. ✅ **Expected**: 
   - Errors are gracefully handled and logged
   - User sees helpful error messages
   - Application doesn't crash
   - Recovery instructions are provided

---

## 🔍 Test Error Scenarios

### Test 23: Invalid File Upload
1. Login as admin
2. Try uploading a non-HTML file (e.g., .txt, .pdf)
3. ✅ **Expected**: File rejected by upload component

### Test 24: No Rules Configured
1. Login as Caper
2. Clear all rules ("🗑️ Limpar Regras")
3. Go to Daily Results and try manual search
4. ✅ **Expected**: Warning message about configuring rules first

### Test 25: Network Error Simulation
1. Disconnect internet
2. Try manual search as Caper
3. ✅ **Expected**: Graceful error handling with error message

---

## 🎯 Complete Test Checklist

- [ ] ✅ Login works for both users with **centered logos**
- [ ] ✅ Client can configure automation rules  
- [ ] ✅ Client can view daily results
- [ ] ✅ Client can view uploaded analyses
- [ ] ✅ Admin can upload multiple HTML files
- [ ] ✅ **Admin can delete uploaded analysis files**
- [ ] ✅ Uploaded files appear for client immediately
- [ ] ✅ Manual cronjob execution works
- [ ] ✅ Cronjob creates proper result files
- [ ] ✅ Results from cronjob appear in client dashboard
- [ ] ✅ Logo appears **centered** on all pages (login, sidebar, main)
- [ ] ✅ **Application logging works correctly**
- [ ] ✅ **Error handling is robust and informative**
- [ ] ✅ Logout functionality works
- [ ] ✅ Docker deployment works
- [ ] ✅ Data persists across restarts

---

## 🚨 Troubleshooting Testing Issues

### Issue: App won't start
```bash
# Check if port is in use
lsof -i :8501

# Try different port
streamlit run app.py --server.port 8502
```

### Issue: Cronjob not working
```bash
# Check log file
tail -f cronjob.log

# Verify rules file exists
cat saved_rules.json

# Test manually
python cronjob_scheduler.py test
```

### Issue: Files not uploading
```bash
# Check directory permissions
ls -la analyses/
mkdir -p analyses
chmod 755 analyses/
```

### Issue: Results not showing
- Verify `daily_results/` directory exists
- Check if `results_YYYY-MM-DD.json` files are created
- Ensure date selector matches result file date

### Issue: Logging not working
```bash
# Check if log file exists
ls -la app.log

# View recent log entries
tail -f app.log

# Check file permissions
chmod 644 app.log
```

### Issue: Delete functionality not working
```bash
# Check directory permissions
ls -la analyses/
chmod 755 analyses/
chmod 644 analyses/*.html
```

---

## 📝 Test Results Documentation

Document your test results:

| Test | Status | Notes |
|------|---------|--------|
| Authentication | ✅/❌ | |
| Rules Configuration | ✅/❌ | |
| Manual Search | ✅/❌ | |
| File Upload | ✅/❌ | |
| Cronjob Execution | ✅/❌ | |
| Docker Deployment | ✅/❌ | |

---

## ✅ Ready for Production

Once all tests pass, your system is ready for production deployment!

### Final Verification Checklist
Before going live, ensure:
- [ ] All logs are working (`app.log` being created and populated)
- [ ] Logo positioning is correct on all pages
- [ ] Admin can upload AND delete analysis files
- [ ] Client can configure rules and view results
- [ ] Search functionality uses optimized method
- [ ] Error handling provides helpful feedback
- [ ] All authentication flows work correctly
- [ ] Docker deployment is stable

### Post-Deployment Monitoring
After deployment, monitor:
- **Application logs**: `tail -f app.log`
- **System health**: Regular access to http://localhost:8501
- **Cronjob execution**: Check `cronjob.log` daily
- **Storage usage**: Monitor `analyses/` and `daily_results/` directories

Your LegalLex MVP2 system is now feature-complete and production-ready! 🎉