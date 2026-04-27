@echo off
cd /d C:\dev\TechChallengeF04\medvision-ai

echo === Configurando Git ===
git config core.editor "true"
git config --global core.editor "true"

echo.
echo === Limpando estado ===
git merge --abort 2>nul
git rebase --abort 2>nul

echo.
echo === Status ===
git status

echo.
echo === Tentando push ===
git push origin main

echo.
echo === Resultado ===
if %ERRORLEVEL% EQU 0 (
    echo [OK] Push realizado com sucesso!
) else (
    echo [ERRO] Falha no push. Codigo: %ERRORLEVEL%
)

echo.
pause
