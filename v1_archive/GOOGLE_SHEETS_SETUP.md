# Google Sheets API Setup - Quick Guide

## 1. Google Cloud Console Setup (5 Min)

1. Gehe zu: https://console.cloud.google.com/
2. Erstelle neues Projekt: "Clip Finder"
3. Enable Google Sheets API:
   - Suche nach "Google Sheets API"
   - Click "Enable"

## 2. Service Account erstellen

1. Navigation Menu → "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name: "clip-finder-bot"
4. Click "Create and Continue"
5. Role: "Editor" (oder "Basic → Editor")
6. Click "Done"

## 3. JSON Key erstellen

1. Click auf deinen Service Account
2. Tab "Keys" → "Add Key" → "Create new key"
3. Type: JSON
4. Download die JSON-Datei
5. **Wichtig:** Speichere sie als:
   `~/custom-clip-finder/credentials/google_sheets_credentials.json`

## 4. Sheet freigeben

1. Öffne deine Google Sheet
2. Click "Share" (Teilen)
3. Füge die Service Account Email hinzu:
   - Format: clip-finder-bot@project-id.iam.gserviceaccount.com
   - (findest du in der JSON Datei unter "client_email")
4. Rolle: "Editor"
5. Send!

## 5. Sheet ID kopieren

Deine Sheet URL:
https://docs.google.com/spreadsheets/d/1ABELrl8UEhVCvL4qRujAdw3tWoftL70olcjF9hedL0A/edit

Sheet ID ist: `1ABELrl8UEhVCvL4qRujAdw3tWoftL70olcjF9hedL0A`

Speichere diese in: `.env`

✅ Fertig! Jetzt kann das Script deine Sheet lesen.
